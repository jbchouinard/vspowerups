import queue
import multiprocessing
from collections import namedtuple


class PoolWorker(multiprocessing.Process):
    def __init__(self, f, jobq, resq, name=None):
        super().__init__(target=None, name=name, daemon=True)
        self.f = f
        self.jobq = jobq
        self.resq = resq

    def run(self):
        while True:
            try:
                # Use timeout else this may block forever and cause the process to not
                # respond to signals
                job_id, job = self.jobq.get(block=True, timeout=1)
                try:
                    result = self.f(job)
                    self.resq.put((job_id, True, result))
                except Exception as e:
                    self.resq.put((job_id, False, e))
            except queue.Empty:
                pass


Job = namedtuple("Job", ["job_id", "callback", "tkevent"])


class TkinterWorkerPool:
    """
    TkinterWorkerPool manages a pool of worker and is meant to offload CPU intensive
    operations in tkinter applications to avoid blocking the GUI.

    Because of the GIL, the GUI can get blocked by CPU intensive operations even
    in separate threads.

    When a job is completed, the pool can call callbacks, and/or generate Tk virtual
    events.

    The pool can have both global callbacks and tkevents (for every job) and job-specific
    callbacks and tkevents.

    TkinterWorkerPool can optionally manage a progress bar widget. It will start the
    bar when there are jobs being processed, and stop it when finished.
    """

    def __init__(
        self,
        widget,
        f,
        n=1,
        name=None,
        update_interval_ms=100,
        callback=None,
        tkevent=None,
        progress_bar=None,
        hide_progress_bar=False,
    ):
        self.f = f
        self.window = widget.winfo_toplevel()
        self.name = name
        self.update_interval_ms = update_interval_ms
        self.callback = callback
        self.tkevent = tkevent
        self.progress_bar = progress_bar
        self.hide_progress_bar = hide_progress_bar

        self.job_counter = 0
        self.open_jobs = {}
        self.jobq = multiprocessing.Queue()
        self.resq = multiprocessing.Queue()
        self.workers = [self._worker(i) for i in range(1, n + 1)]

    def start(self):
        for worker in self.workers:
            worker.start()

    def finish(self):
        for worker in self.workers:
            self.join()

        self.workers = []
        del self.jobq
        del self.resq

    def _worker(self, i):
        name = f"{self.name}-{i}" if self.name else None
        return PoolWorker(self.f, self.jobq, self.resq, name=name)

    def _job_id(self):
        job_id = self.job_counter
        self.job_counter += 1
        return job_id

    def _set_update_timer(self):
        if self.update_interval_ms:
            self.window.after(self.update_interval_ms, self.update)

    def send(self, job, callback=None, tkevent=None):
        job_id = self._job_id()
        self.jobq.put((job_id, job))
        if not self.open_jobs:
            self._set_update_timer()
            self._progress_bar_start()

        self.open_jobs[job_id] = Job(job_id, callback, tkevent)
        return job_id

    def _process_result(self, res):
        job_id, success, result = res
        job = self.open_jobs[job_id]
        del self.open_jobs[job_id]

        if not success:
            raise result

        if self.tkevent:
            self.window.event_generate(self.tkevent)
        if job.tkevent:
            self.window.event_generate(job.tkevent)
        if self.callback:
            self.callback(result)
        if job.callback:
            job.callback(result)

    def _progress_bar_start(self):
        if self.progress_bar:
            self.progress_bar.start()
            if self.hide_progress_bar:
                self.progress_bar.grid()

    def _progress_bar_stop(self):
        if self.progress_bar:
            self.progress_bar.stop()
            if self.hide_progress_bar:
                self.progress_bar.grid_remove()

    def update(self):
        try:
            res = self.resq.get(block=False)
        except queue.Empty:
            pass
        else:
            self._process_result(res)
        finally:
            if self.open_jobs:
                self._set_update_timer()
            else:
                self._progress_bar_stop()
