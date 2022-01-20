import queue
import multiprocessing


class Worker(multiprocessing.Process):

    def __init__(self, inq, outq, name=None):
        super().__init__(target=None, name=name, daemon=True)
        self.inq = inq
        self.outq = outq

    def do_job(self, job):
        raise NotImplementedError

    def run(self):
        while True:
            try:
                # Use timeout to avoid blocking the process forever and give it a
                # a chance to respond to signals
                job = self.inq.get(block=True, timeout=1)
                result = self.do_job(job, more_jobs=not self.inq.empty())
                self.outq.put(result)
            except queue.Empty:
                pass
