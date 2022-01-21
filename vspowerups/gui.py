import tkinter
from queue import Empty
from multiprocessing import Queue
from tkinter import font
from tkinter import ttk

from vspowerups.powerups import optimize, POWER_UPS

TITLE = "Vampire Survivors Power Up Optimizer"

EXPAND = tkinter.N + tkinter.S + tkinter.W + tkinter.E


class PowerUpWidget(ttk.Frame):
    def __init__(self, parent, powerup, **kwargs):
        super().__init__(parent, **kwargs)
        self.var_tier = tkinter.StringVar(self, value="0")
        self.powerup = powerup
        self.group = ttk.LabelFrame(self, text=powerup.name, pad=10)
        self.group.grid(row=0, column=0, sticky=EXPAND)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.spinbox = ttk.Spinbox(
            self.group,
            textvariable=self.var_tier,
            from_=0,
            to=self.powerup.MAX_TIER,
            width=2,
            font=FONTS["largebold"],
            command=self.on_spinbox_change,
        )
        self.spinbox.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=EXPAND)
        self.spinbox.state(["readonly"])

        self.var_buy_cost = tkinter.StringVar(self, value=str(self.powerup.BASE_COST))
        self.buy_cost_label = ttk.Label(
            self.group, textvariable=self.var_buy_cost, width=5, style="BuyCost.TLabel"
        )
        self.buy_cost_label.grid(row=0, column=2)

        self.var_sell_cost = tkinter.StringVar(self, value="-")
        self.sell_cost_label = ttk.Label(
            self.group,
            textvariable=self.var_sell_cost,
            width=5,
            style="SellCost.TLabel",
        )
        self.sell_cost_label.grid(row=1, column=2)

    def on_spinbox_change(self):
        new_tier = int(self.var_tier.get())
        if new_tier != self.powerup.current_tier:
            self.powerup.current_tier = new_tier
            self.winfo_toplevel().event_generate("<<PowerUpTierUpdate>>")


class PowerUpsWidget(ttk.Frame):
    ROW_LENGTH = 4

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.winfo_toplevel().bind("<<PowerUpTierUpdate>>", self.on_tier_update, add="+")

        cost_frame = ttk.Frame(self)
        cost_frame.grid(row=0, column=0)
        cost_txt_label = ttk.Label(cost_frame, text="Total Cost ", style="Large.TLabel")
        cost_txt_label.grid(row=0, column=0)

        self.var_total_cost = tkinter.StringVar(value="0")
        cost_label = ttk.Label(
            cost_frame,
            textvariable=self.var_total_cost,
            style="LargeBold.TLabel",
            width=5,
        )
        cost_label.grid(row=0, column=1)

        self.widgets = {}
        self.powerups_frame = ttk.Frame(self, pad=10)
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
        listlabel = ttk.Label(listframe, text="Buy Order (Optimized)", style="Large.TLabel")
        listlabel.grid(row=0, column=0, sticky=tkinter.W + tkinter.E)
        self.var_listbox = tkinter.StringVar(value=[])
        listbox = tkinter.Listbox(
            listframe,
            listvariable=self.var_listbox,
            font=FONTS["largebold"],
            state="disabled",
            disabledforeground="black",
            background="#d9d9d9",
            relief="groove",
        )
        listbox.grid(row=1, column=0, sticky=EXPAND)
        listframe.rowconfigure(1, weight=1)
        listframe.grid(row=2, column=1, sticky=EXPAND)

        buttons_frame = ttk.Frame(self)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=15)
        ttk.Button(buttons_frame, text="Reset", command=self.on_press_reset).grid(row=0, column=2)
        ttk.Button(buttons_frame, text="Max All", command=self.on_press_max_all).grid(
            row=0, column=3
        )

    def on_tier_update(self, event):
        result = optimize_all([w.powerup for w in self.widgets.values()])
        self.var_total_cost.set(result["total_cost"])
        self.var_listbox.set(result["buy_list"])

        for w in self.widgets.values():
            r = result["powerups"].get(w.powerup.name)
            w.var_buy_cost.set(r["buy_cost"])
            w.var_sell_cost.set(r["sell_cost"])

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


def optimize_all(powerups):
    total_cost, order = optimize(powerups)
    result = {
        "powerups": {p.name: {} for p in powerups},
        "total_cost": total_cost,
        "buy_list": [f"{p.current_tier}x {p.name}" for p in order if p.current_tier > 0],
    }

    for powerup in powerups:
        if powerup.current_tier == powerup.MAX_TIER:
            result["powerups"][powerup.name]["buy_cost"] = "-"
        else:
            powerup.current_tier += 1
            next_cost, _ = optimize(powerups)
            powerup.current_tier -= 1
            result["powerups"][powerup.name]["buy_cost"] = str(next_cost - total_cost)
        if powerup.current_tier == 0:
            result["powerups"][powerup.name]["sell_cost"] = "-"
        else:
            powerup.current_tier -= 1
            next_cost, _ = optimize(powerups)
            powerup.current_tier += 1
            result["powerups"][powerup.name]["sell_cost"] = str(total_cost - next_cost)

    return result


class App(ttk.Frame):
    GAME_VERSION = "v0.2.8a"

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        title_frame = ttk.Frame(self, pad=10)
        ttk.Label(title_frame, text=TITLE, style="Title.TLabel").grid(row=0, column=0)
        ttk.Label(title_frame, text=f"for game version {self.GAME_VERSION}").grid(row=1, column=0)
        title_frame.grid(row=0, column=0)

        self.powerups_widget = PowerUpsWidget(self, pad=10)
        self.powerups_widget.grid(row=1, column=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)


def get_font_family(preferred, fallback="TkDefaultFont"):
    available = font.families()
    for pref in preferred:
        if pref in available:
            return pref
    return font.nametofont(fallback).actual()["family"]


def mono_font(size=10, weight="normal"):
    return font.Font(
        family=get_font_family(MONO_FONTS, fallback="TkFixedFont"), size=size, weight=weight
    )


def normal_font(size=10, weight="normal"):
    return font.Font(
        family=get_font_family(NORMAL_FONTS, fallback="TkDefaultFont"), size=size, weight=weight
    )


MONO_FONTS = ["Noto Mono", "Liberation Mono"]
NORMAL_FONTS = ["Helvetica", "Noto Serif", "Liberation Serif"]

FONTS = {}
COLORS = {
    "darkred": "#882222",
}


def style(root):
    FONTS["default"] = mono_font(10)
    FONTS["bold"] = mono_font(10, "bold")
    FONTS["large"] = mono_font(12)
    FONTS["largebold"] = mono_font(12, "bold")
    FONTS["title"] = normal_font(18, "bold")

    style = ttk.Style(root)
    style.theme_use("default")
    style.configure("TSpinbox", arrowsize=40, arrowcolor="green")
    style.map("TSpinbox", fieldbackground=[("readonly", "white")])
    style.configure("Large.TLabel", font=FONTS["large"])
    style.configure("Bold.TLabel", font=FONTS["bold"])
    style.configure("LargeBold.TLabel", font=FONTS["largebold"])
    style.configure("Title.TLabel", font=FONTS["title"], foreground="#882222")
    style.configure("TLabel", font=FONTS["default"])
    style.configure("TLabelframe.Label", font=FONTS["largebold"])
    style.configure("TButton", font=FONTS["large"])


def main():
    root = tkinter.Tk()
    root.title(TITLE)
    style(root)
    app = App(root)
    app.grid(row=0, column=0, sticky=EXPAND)
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.mainloop()


if __name__ == "__main__":
    main()
