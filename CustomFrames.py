from copy import copy, deepcopy
from tkinter.scrolledtext import ScrolledText
from uuid import uuid4

import test_strings
from util_methods import *


def get_attack_frame(exemplar, label, storage=None, placeholder=None):
    if not storage: storage = exemplar.storage
    if not placeholder: placeholder = label[:-1]
    upper_frame = tk.LabelFrame(exemplar, text=label, labelanchor='n')

    attacks = AttackFrame(master=upper_frame, label_code=placeholder)
    attacks.pack()
    storage[label] = attacks
    return upper_frame


class DefenseFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes = []
        self.atr_values = []
        self.bonuses = []

        for i, DEF in enumerate(("DEFENSE", "MAGIC DEFENSE")):
            lbd = tk.LabelFrame(self, text=DEF, labelanchor='n')
            lbd.grid(column=0, row=i, sticky='nsew')
            bnd = tk.LabelFrame(self, text='Bonus', labelanchor='n')
            bnd.grid(column=1, row=i, sticky='nsew')

            attrib = tk.StringVar()
            atr_value = tk.IntVar()
            bonus_value = tk.IntVar()

            self.attributes.append(attrib)
            self.atr_values.append(atr_value)
            self.bonuses.append(bonus_value)

            dd = tk.OptionMenu(lbd, attrib, *attributes)
            dd.configure(width=8)
            dd.pack(pady=5, side=tk.LEFT)
            tk.Entry(lbd, textvariable=atr_value, width=3).pack(pady=1, side=tk.RIGHT)
            tk.Entry(bnd, textvariable=bonus_value, width=2).pack(pady=11, anchor='center')

    def get_vars(self):
        return (self.attributes[0],
                self.atr_values[0],
                self.bonuses[0]), (self.attributes[1],
                                   self.atr_values[1],
                                   self.bonuses[1])


class ResistFrame(tk.Frame):
    def __init__(self, *args, resists=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.labels = {}
        if not resists:
            self.resists = defaultdict(int)
        else:
            self.resists = resists

        for i, d_type in enumerate(RESISTS):
            resists_values = get_resist_color(self.resists[d_type])
            row = i // 3
            col = (i * 3) % 9
            icon = tk.Label(self, image=global_images[d_type])
            icon.grid(row=row, column=col)

            icon.bind("<Button-1>", lambda x, y=d_type: self.increment_resist(key=y))

            lb = tk.Label(self, text=resists_values[0], fg=resists_values[1],
                          font='Times 13 bold', width=3)
            lb.grid(row=row, column=col + 1, columnspan=2, pady=5)
            self.labels[d_type] = lb

    def increment_resist(self, *args, key):
        self.resists[key] = self._increment_resist(self.resists[key])
        self.update_label(key)

    def update_label(self, key):
        resists_values = get_resist_color(self.resists[key])
        self.labels[key].config(text=resists_values[0], fg=resists_values[1])

    @staticmethod
    def _increment_resist(value):
        ranger = (0, 1, 2, 3, -1)
        value += 1
        return ranger[value]


class HelpFrame(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        tk.Label(self, text=test_strings.help_label, justify='left').pack()


class AttackFrame(tk.Frame):
    def __init__(self, *args, label_code='Attack', **kwargs):
        super().__init__(*args, **kwargs)
        self.attacks = {}
        self.counter = 0
        self.label_code = label_code

        self.plus = tk.Button(self, image=global_images['plus'],
                              highlightthickness=0, bd=0,
                              command=self.add_attack, width=385)
        self.plus.grid(row=0, columnspan=3)

    def add_attack(self):
        self.plus.grid_forget()
        canvas = self.master.master
        height = canvas.winfo_height()
        self.counter += 1
        row = self.counter - 1
        uuid = uuid4().hex
        name = tk.Entry(self, justify=tk.LEFT, width=15)
        name.insert(0, f"{self.label_code} Name")
        effect = tk.Entry(self, justify=tk.LEFT, width=35)
        effect.insert(0, f"{self.label_code} effects and accuracy")
        destroy_button = tk.Button(self, image=global_images['minus'], highlightthickness=0, bd=0)
        self.attacks[uuid] = (name, effect, destroy_button)

        def destroyer(r):
            for widget in self.attacks.get(r):
                widget.destroy()
            self.attacks.pop(r)
            canvas.configure(height=canvas.winfo_height() - 40)

        destroy_button.config(command=lambda x=uuid: destroyer(x))

        name.grid(row=row, column=0, pady=5, padx=0)
        effect.grid(row=row, column=1, pady=5, padx=0)
        destroy_button.grid(row=row, column=2)
        canvas.configure(height=height + 40)
        self.plus.grid(row=row+1, columnspan=3)

    def get_attacks(self):
        return self.attacks


class SpecialsFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        storage = self.master.storage

        annotation_frame = tk.LabelFrame(self, text='General Special Info', labelanchor='n')

        special_annotation = ScrolledText(master=annotation_frame, width=45, height=5)
        storage['special_annotation'] = special_annotation
        special_annotation.pack(padx=2)

        crisis_a_frame = tk.LabelFrame(self, text='Effects while in CRISIS', labelanchor='n')

        crisis_ability = tk.Entry(master=crisis_a_frame, width=63)
        storage['crisis_ability'] = crisis_ability
        crisis_ability.pack(padx=2)

        # Geometry
        annotation_frame.pack(anchor='w')
        crisis_a_frame.pack(anchor='w')


class LootFrameNM(tk.Frame):
    def __init__(self, *args, box, **kwargs):
        super().__init__(*args, **kwargs)
        self.container = box
        self.container_repr = tk.StringVar()

        self.dd_option = tk.StringVar()
        self.dd_option.set('Zenit')
        self.value = tk.StringVar()
        self.changes = [{"zenit": 0, "invpts": 0, "lootable": []}]

        options = ("Zenit", "Inv. Points", "Inventory")
        # elements
        tk.Button(master=self, text="Add", command=self._add_to_container).grid(padx=2, column=0, row=0, sticky='w')
        dropdown = tk.OptionMenu(self, self.dd_option, *options)
        dropdown.config(width=10)
        dropdown.grid(column=0, row=1, sticky='w')
        self.entry = tk.Entry(self, textvariable=self.value, width=40)
        self.entry.grid(padx=3, column=1, row=1, columnspan=2)
        self.loot_list = tk.Label(self, textvariable=self.container_repr, width=48, wraplength=320)
        self.clear_b = tk.Button(master=self, text="Clear All", command=self._clean)
        self.clear_cat = tk.Button(master=self, text="Clear Category", command=self._clean_cat)
        self.undo = tk.Button(master=self, text="Undo", command=self._undo)

        self._clean()

    def _add_to_container(self):
        loot = self.container['loot']
        self.changes.append(deepcopy(loot))
        if not self.value.get(): return
        if not self.container_repr.get():
            self._turn_on_repr()
        option = self.dd_option.get()
        try:
            match option:
                case 'Zenit':
                    zeni = int(self.value.get())
                    loot["zenit"] += zeni
                case "Inv. Points":
                    invpts = int(self.value.get())
                    loot["invpts"] += invpts
                case "Inventory":
                    item = self.value.get()
                    loot["lootable"].append(item)
            self._update_repr()
        except ValueError:
            window = self.master.master.master.master.master
            x = window.winfo_x() + 100
            y = window.winfo_y() + 400
            print(x)
            print(y)
            popup = generate_popup(x=x, y=y, name="Error!", wdh=200, ht=50)
            tk.Label(popup, text=f"{option} must be integer").pack()

    def _clean(self):
        loot = self.container['loot']
        if loot: self.changes.append(deepcopy(loot))
        loot.clear()
        loot.update({"zenit": 0, "invpts": 0, "lootable": []})

        self.container_repr.set("")
        self._empty_entry()
        self._turn_off_repr()

    def _clean_cat(self):
        loot = self.container['loot']
        if loot:
            self.changes.append(deepcopy(loot))
        category = self.dd_option.get()
        match category:
            case 'Inventory':
                loot['lootable'] = []
            case "Inv. Points":
                loot['invpts'] = 0
            case "Zenit":
                loot['zenit'] = 0
        self._update_repr()

    def _undo(self):
        if len(self.changes) > 1:
            self.container['loot'] = self.changes.pop()
        else:
            self.container['loot'] = self.changes[0]
        self._update_repr()

    def _turn_on_repr(self):
        self.loot_list.grid(columnspan=3)
        self.clear_b.grid(row=3, column=0, padx=2, sticky='w')
        self.clear_cat.grid(row=3, column=1, padx=2, sticky='w')
        self.undo.grid(row=3, column=2, padx=2, sticky='w')

    def _turn_off_repr(self):
        self.loot_list.grid_forget()
        self.clear_b.grid_forget()
        self.clear_cat.grid_forget()
        self.undo.grid_forget()

    def _empty_entry(self):
        self.entry.delete(0, 'end')

    def _update_repr(self):
        self.container_repr.set(convert_dict_to_str_beauty(self.container['loot']))
