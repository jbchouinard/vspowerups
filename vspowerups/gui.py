import tkinter
from queue import Empty
from multiprocessing import Queue
from tkinter import font
from tkinter import ttk

from vspowerups.powerups import (
    optimize,
    Might,
    Armor,
    MaxHealth,
    Recovery,
    Cooldown,
    Area,
    Speed,
    Duration,
    Amount,
    MoveSpeed,
    Magnet,
    Luck,
    Growth,
    Greed,
)
from vspowerups.worker import Worker

EXPAND = tkinter.N + tkinter.S + tkinter.W + tkinter.E

POWER_UPS = [
    Might,
    Armor,
    MaxHealth,
    Recovery,
    Cooldown,
    Area,
    Speed,
    Duration,
    Amount,
    MoveSpeed,
    Magnet,
    Luck,
    Growth,
    Greed,
]


class PowerUpWidget(ttk.Frame):
    def __init__(self, parent, powerup, **kwargs):
        super().__init__(parent, **kwargs)
        self.var_tier = tkinter.StringVar(self, value="0")
        self.powerup = powerup
        self.group = ttk.LabelFrame(
            self, text=powerup.name, borderwidth=1, relief="groove", pad=10
        )
        self.group.grid(row=0, column=0, sticky=EXPAND)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.spinbox = ttk.Spinbox(
            self.group,
            textvariable=self.var_tier,
            from_=0,
            to=self.powerup.MAX_TIER,
            style="BigArrow.TSpinbox",
            width=2,
            font=font.Font(size=16),
            command=self.on_spinbox_change,
        )
        self.spinbox.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=EXPAND)
        self.spinbox.state(["readonly"])

        self.var_buy_cost = tkinter.StringVar(self, value=str(self.powerup.BASE_COST))
        self.buy_cost_label = ttk.Label(
            self.group, textvariable=self.var_buy_cost, width=5
        )
        self.buy_cost_label.grid(row=0, column=2)

        self.var_sell_cost = tkinter.StringVar(self, value="-")
        self.sell_cost_label = ttk.Label(
            self.group, textvariable=self.var_sell_cost, width=5
        )
        self.sell_cost_label.grid(row=1, column=2)

    def on_spinbox_change(self):
        new_tier = int(self.var_tier.get())
        if new_tier != self.powerup.current_tier:
            self.powerup.current_tier = new_tier
            self.winfo_toplevel().event_generate("<<PowerUpTierUpdate>>")


class OptimizerWorker(Worker):
    def __init__(self, inq, outq, name=None):
        super().__init__(inq, outq, name)

    def do_job(self, powerups, more_jobs):
        # Don't bother computing if there are more updates
        if more_jobs:
            return None
        result = {"powerups": {p.name: {} for p in powerups}}
        total_cost, order = optimize(powerups)
        result["total_cost"] = total_cost

        buy_list = [None] * 14
        for i, powerup in enumerate(order, 1):
            if powerup.current_tier:
                buy_list[i - 1] = f"{powerup.current_tier}x {powerup.name}"
        result["buy_list"] = [p for p in buy_list if p is not None]

        for powerup in powerups:
            if powerup.current_tier == powerup.MAX_TIER:
                result["powerups"][powerup.name]["buy_cost"] = "-"
            else:
                powerup.current_tier += 1
                next_cost, _ = optimize(powerups)
                powerup.current_tier -= 1
                result["powerups"][powerup.name]["buy_cost"] = str(
                    next_cost - total_cost
                )
            if powerup.current_tier == 0:
                result["powerups"][powerup.name]["sell_cost"] = "-"
            else:
                powerup.current_tier -= 1
                next_cost, _ = optimize(powerups)
                powerup.current_tier += 1
                result["powerups"][powerup.name]["sell_cost"] = str(
                    total_cost - next_cost
                )

        return result


class PowerUpsWidget(ttk.Frame):
    ROW_LENGTH = 4
    QUEUE_CHECK_DELAY = 20

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.job_queue = Queue()
        self.result_queue = Queue()
        self.open_jobs = 0
        self.worker = OptimizerWorker(
            self.job_queue, self.result_queue, name="vspowerups-optimizer"
        )
        self.worker.start()

        self.winfo_toplevel().bind(
            "<<PowerUpTierUpdate>>", self.callback_tier_update, add="+"
        )

        cost_frame = ttk.Frame(self)
        cost_frame.grid(row=0, column=0)
        cost_txt_label = ttk.Label(cost_frame, text="Total cost: ", style="Bold.TLabel")
        cost_txt_label.grid(row=0, column=0)

        self.widgets = {}
        self.powerups_frame = ttk.Frame(self)
        self.powerups_frame.grid(row=2, column=0)
        for i, powerup_cls in enumerate(POWER_UPS):
            widget = PowerUpWidget(self.powerups_frame, powerup_cls(), pad=5)
            widget.grid(
                row=i // self.ROW_LENGTH,
                column=i % self.ROW_LENGTH,
                sticky=tkinter.W + tkinter.E,
            )
            self.widgets[widget.powerup.name] = widget
        for i in range(self.ROW_LENGTH):
            self.powerups_frame.columnconfigure(i, weight=1)

        listframe = ttk.Frame(self)
        listlabel = ttk.Label(listframe, text="Buy Order (Optimized)")
        listlabel.grid(row=0, column=0, sticky=tkinter.W + tkinter.E)
        self.var_listbox = tkinter.StringVar(value=[])
        listbox = tkinter.Listbox(listframe, listvariable=self.var_listbox)
        listbox.grid(row=1, column=0, sticky=EXPAND)
        listframe.rowconfigure(1, weight=1)
        listframe.grid(row=2, column=1, sticky=EXPAND)

        progress_bar_frame = ttk.Frame(self, width=20)
        progress_bar_frame.grid(row=2, column=2, sticky=EXPAND, padx=5)
        self.progress_bar = ttk.Progressbar(
            progress_bar_frame,
            orient=tkinter.VERTICAL,
            length=350,
            mode="indeterminate",
            maximum=20,
        )
        self.progress_bar.grid(row=0, column=0, sticky=EXPAND)
        self.progress_bar.grid_remove()

        separator = ttk.Separator(self, orient=tkinter.HORIZONTAL)
        separator.grid(row=3, column=0, sticky=tkinter.W + tkinter.E)

        buttons_frame = ttk.Frame(self)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=15)
        ttk.Button(buttons_frame, text="Reset", command=self.on_press_reset).grid(
            row=0, column=2
        )
        ttk.Button(buttons_frame, text="Max All", command=self.on_press_max_all).grid(
            row=0, column=3
        )

        self.var_total_cost = tkinter.StringVar(value="0")
        cost_label = ttk.Label(
            cost_frame, textvariable=self.var_total_cost, style="Bold.TLabel", width=5
        )
        cost_label.grid(row=0, column=1)

    def progress_start(self):
        self.progress_bar.grid()
        self.progress_bar.start()

    def progress_stop(self):
        self.progress_bar.grid_remove()
        self.progress_bar.stop()

    def check_work_queue(self):
        result = None
        try:
            result = self.result_queue.get(block=False)
            self.open_jobs -= 1
        except Empty:
            pass
        finally:
            if self.open_jobs:
                self.after(self.QUEUE_CHECK_DELAY, self.check_work_queue)

        if not self.open_jobs:
            self.progress_stop()

        if result and not self.open_jobs:
            self.var_total_cost.set(result["total_cost"])
            self.var_listbox.set(result["buy_list"])

            for w in self.widgets.values():
                r = result["powerups"].get(w.powerup.name)
                w.var_buy_cost.set(r["buy_cost"])
                w.var_sell_cost.set(r["sell_cost"])

    def callback_tier_update(self, event):
        powerups = [w.powerup for w in self.widgets.values()]
        self.job_queue.put(powerups)
        if not self.open_jobs:
            self.progress_start()
        self.open_jobs += 1
        self.after(self.QUEUE_CHECK_DELAY, self.check_work_queue)

    def on_press_reset(self):
        for w in self.widgets.values():
            w.var_tier.set(0)
            w.powerup.current_tier = 0
        self.winfo_toplevel().event_generate("<<PowerUpTierUpdate>>")

    def on_press_max_all(self):
        for w in self.widgets.values():
            w.var_tier.set(w.powerup.MAX_TIER)
            w.powerup.current_tier = w.powerup.MAX_TIER
        self.winfo_toplevel().event_generate("<<PowerUpTierUpdate>>")


class App(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.powerups_widget = PowerUpsWidget(self, pad=10)
        self.powerups_widget.grid(row=0, column=0)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


def main():
    root = tkinter.Tk()
    root.title("Vampire Survivors Power Up Optimizer")
    spinbox_style = ttk.Style()
    spinbox_style.theme_use("default")
    spinbox_style.configure("BigArrow.TSpinbox", arrowsize=30)
    bold_style = ttk.Style()
    bold_style.theme_use("default")
    bold_style.configure("Bold.TLabel", font=font.Font(size=12, weight="bold"))
    app = App(root)
    app.grid(row=0, column=0, sticky=EXPAND)
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.mainloop()


if __name__ == "__main__":
    main()
