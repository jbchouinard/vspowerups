import tkinter
from tkinter import font, ttk


class PowerUp:
    MAX_TIER = 0
    BASE_COST = 0

    def __init__(self):
        self.target_tier = 0

    @property
    def name(self):
        return self.__class__.__name__

    def upgrade_cost(self, n_upgrades):
        cost = self.BASE_COST // 10
        n = 10 + n_upgrades
        if self.target_tier == 0:
            return 0
        elif self.target_tier == 1:
            return n * cost
        elif self.target_tier == 2:
            return (3 * n + 2) * cost
        elif self.target_tier == 3:
            return (6 * n + 8) * cost
        elif self.target_tier == 4:
            return (10 * n + 20) * cost
        else:
            return (15 * n + 40) * cost

    def score(self):
        return (self.target_tier + 1) * self.BASE_COST

    def __repr__(self):
        return f"{self.name}({self.target_tier})"

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__ and self.target_tier == other.target_tier
        )


POWER_UPS = []


def power_up(max_tier, base_cost, name):
    kls = type(name, (PowerUp,), {"BASE_COST": base_cost, "MAX_TIER": max_tier})
    POWER_UPS.append(kls)
    return kls


Might = power_up(5, 200, "Might")
Armor = power_up(3, 600, "Armor")
MaxHealth = power_up(3, 200, "MaxHealth")
Recovery = power_up(5, 200, "Recovery")
Cooldown = power_up(2, 900, "Cooldown")
Area = power_up(2, 300, "Area")
Speed = power_up(2, 300, "Speed")
Duration = power_up(2, 300, "Duration")
Amount = power_up(1, 5000, "Amount")
MoveSpeed = power_up(2, 300, "MoveSpeed")
Magnet = power_up(2, 300, "Magnet")
Luck = power_up(3, 600, "Luck")
Growth = power_up(5, 900, "Growth")
Greed = power_up(5, 200, "Greed")
Revival = power_up(1, 52000, "Revival")


def optimize(powerups):
    pups = sorted(powerups, key=lambda p: p.score(), reverse=True)
    n_upgrades = 0
    total_cost = 0
    for pup in pups:
        total_cost += pup.upgrade_cost(n_upgrades)
        n_upgrades += pup.target_tier
    return total_cost, pups


TITLE = "Vampire Survivors Power Up Optimizer"
GAME_VERSION = "0.2.10h"

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
        if new_tier != self.powerup.target_tier:
            self.powerup.target_tier = new_tier
            self.winfo_toplevel().event_generate("<<PowerUpTierUpdate>>")


class PowerUpsWidget(ttk.Frame):
    ROW_LENGTH = 4

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.winfo_toplevel().bind(
            "<<PowerUpTierUpdate>>", self.on_tier_update, add="+"
        )

        cost_frame = ttk.Frame(self)
        cost_frame.grid(row=0, column=0)
        cost_txt_label = ttk.Label(cost_frame, text="Total Cost ", style="Large.TLabel")
        cost_txt_label.grid(row=0, column=0)

        self.var_total_cost = tkinter.StringVar(value="0")
        cost_label = ttk.Label(
            cost_frame,
            textvariable=self.var_total_cost,
            style="LargeBold.TLabel",
            width=6,
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
        listlabel = ttk.Label(
            listframe, text="Buy Order (Optimized)", style="Large.TLabel"
        )
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
        ttk.Button(buttons_frame, text="Reset", command=self.on_press_reset).grid(
            row=0, column=2
        )
        ttk.Button(buttons_frame, text="Max All", command=self.on_press_max_all).grid(
            row=0, column=3
        )

    def on_tier_update(self, event):
        powerups = [w.powerup for w in self.widgets.values()]
        total_cost, order = optimize(powerups)

        self.var_total_cost.set(total_cost)
        self.var_listbox.set(
            [f"{p.target_tier}x {p.name}" for p in order if p.target_tier > 0]
        )

        for widget in self.widgets.values():
            powerup = widget.powerup
            if powerup.target_tier == powerup.MAX_TIER:
                widget.var_buy_cost.set("-")
            else:
                powerup.target_tier += 1
                next_cost, _ = optimize(powerups)
                powerup.target_tier -= 1
                widget.var_buy_cost.set(str(next_cost - total_cost))

            if powerup.target_tier == 0:
                widget.var_sell_cost.set("-")
            else:
                powerup.target_tier -= 1
                next_cost, _ = optimize(powerups)
                powerup.target_tier += 1
                widget.var_sell_cost.set(str(total_cost - next_cost))

    def on_press_reset(self):
        for w in self.widgets.values():
            w.var_tier.set(0)
            w.powerup.target_tier = 0
        self.winfo_toplevel().event_generate("<<PowerUpTierUpdate>>")

    def on_press_max_all(self):
        for w in self.widgets.values():
            w.var_tier.set(w.powerup.MAX_TIER)
            w.powerup.target_tier = w.powerup.MAX_TIER
        self.winfo_toplevel().event_generate("<<PowerUpTierUpdate>>")


class App(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        title_frame = ttk.Frame(self, pad=10)
        ttk.Label(title_frame, text=TITLE, style="Title.TLabel").grid(row=0, column=0)
        ttk.Label(title_frame, text=f"for game version {GAME_VERSION}").grid(
            row=1, column=0
        )
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
        family=get_font_family(MONO_FONTS, fallback="TkFixedFont"),
        size=size,
        weight=weight,
    )


def normal_font(size=10, weight="normal"):
    return font.Font(
        family=get_font_family(NORMAL_FONTS, fallback="TkDefaultFont"),
        size=size,
        weight=weight,
    )


MONO_FONTS = ["Noto Mono", "Liberation Mono"]
NORMAL_FONTS = ["Helvetica", "Noto Serif", "Liberation Serif"]

FONTS = {}


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
