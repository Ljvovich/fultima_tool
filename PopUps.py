import tkinter as tk
from util_methods import fabricate_pair, attributes
from CustomFrames import DefenseFrame

stats = ("DEX", "INS", "MIG", "WLP")
options = attributes.keys()
inversed_attributes = {v: k for k, v in attributes.items()}


class Setter(tk.Frame):
    def __init__(self, slave=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slave = slave
        self.model = slave.model

        self.lb = tk.LabelFrame(self.master, text='Set New Value')
        self.lb.pack(fill='both')
        self.input = tk.Entry(self.lb, justify='right')
        self.input.pack()
        self.input.bind("<Return>", self.send_change)
        self.button = tk.Button(self.lb, text="Apply", command=self.send_change)
        self.button.pack()
        self.max = tk.Button(self.lb, text="Max", command=self.max)
        self.max.pack()

    def send_change(self, *args, max_value=False):
        pass

    def max(self):
        self.send_change(max_value=True)


class SetterHP(Setter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input.insert(0, str(self.model.current_hp))

    def send_change(self, *args, max_value=False):
        try:
            new_value = self.model.maxhp if max_value else int(self.input.get())
            self.model.set_hp(new_value)
            self.slave.update_hp_sp()
            # close
            self.master.destroy()
        except ValueError:
            pass


class SetterSP(Setter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input.insert(0, str(self.model.current_sp))

    def send_change(self, max_value=False, *args):
        try:
            new_value = self.model.maxsp if max_value else int(self.input.get())
            self.model.set_sp(new_value)
            self.slave.update_hp_sp()
            # close
            self.master.destroy()
        except ValueError:
            pass


class SetterOffset(tk.Frame):
    def __init__(self, slave=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slave = slave
        self.model = slave.model

        self.widgets = []
        lb = tk.LabelFrame(self.master, text='Set new offset')
        lb.pack()
        for i, stat in enumerate(stats):
            one, two = fabricate_pair(lb, stat)
            one.grid(row=0, column=i * 2)
            two.grid(row=0, column=i * 2 + 1)
            self.widgets.append(two)
        tk.Button(lb, text="Apply", command=self.apply).grid(row=0, column=8)

    def apply(self):
        try:
            offset = [int(x.get()) for x in self.widgets]
            self.model.external_offset(offset)
            self.slave.update_atr_and_armor()
            self.master.destroy()

        except ValueError:
            pass


class SetterDefence(tk.Frame):
    def __init__(self, slave=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slave = slave
        self.model = slave.model

        df = DefenseFrame(self.master)
        df.pack(side=tk.TOP)
        self.defs, self.mdef = df.get_vars()

        self.defaults()

        tk.Button(self.master, text='save',
                  command=self.showtime).pack(side=tk.BOTTOM, expand=True)

    def showtime(self):
        try:
            defense_f = {"attribute": self.defs[0].get(),
                         "value": self.defs[1].get(),
                         "bonus": self.defs[2].get()
                         }
            m_defense_f = {"attribute": self.mdef[0].get(),
                           "value": self.mdef[1].get(),
                           "bonus": self.mdef[2].get()
                           }
            self.model.set_new_armor_formula(defense_f, m_defense_f)
            self.slave.update_atr_and_armor()
            self.master.destroy()
        except tk.TclError:
            pass

    def defaults(self):
        model = self.model

        formula = inversed_attributes[model.defence_formula['type']]
        self.defs[0].set(formula)
        self.defs[1].set(model.defence_formula['value'])
        bonus = 0 if "bonus" not in model.defence_formula else model.defence_formula['bonus']
        self.defs[2].set(bonus)

        formula = inversed_attributes[model.mdef_formula['type']]
        self.mdef[0].set(formula)
        self.mdef[1].set(model.mdef_formula['value'])
        bonus = 0 if "bonus" not in model.mdef_formula else model.mdef_formula['bonus']
        self.mdef[2].set(bonus)


