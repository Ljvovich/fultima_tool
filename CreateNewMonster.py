from dataclasses import dataclass
from tkinter import ttk
from tkinter.ttk import Scrollbar
from platform import system as get_sys
from dataclasses_json import dataclass_json

from test_strings import int_error
from CustomWidgets import LabeledScale

from CustomFrames import *

fields = {'Type': 30, 'lvl': 2, 'initiative': 2, 'HP': 3, 'MP': 3}
stats = ["DEX", "INS", "MIG", "WLP"]


class MonsterOnCanvas(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name = tk.StringVar()
        self.name.set("Insert Creature Name")

        self.storage: dict[str, tk.Variable or dict] = {}

        # Outer General
        fields_frame = tk.LabelFrame(self, text='General Info', labelanchor='nw')

        tk.Entry(fields_frame, justify=tk.CENTER, textvariable=self.name, width=80).pack(side=tk.TOP, padx=5)
        self.storage['name'] = self.name

        for label, width in fields.items():
            self.storage[label] = tk.StringVar() if label == 'Type' else tk.IntVar()
            one, two = fabricate_pair(fields_frame, label, width, var=self.storage[label])
            one.pack(side=tk.LEFT)
            two.pack(side=tk.LEFT)

        # Outer Stat
        stat_frame = tk.LabelFrame(self, text='Stats', width=80)

        for label in stats:
            int_slider = tk.IntVar()
            slider = LabeledScale(master=stat_frame, label=label, variable=int_slider, width=80)
            slider.pack(side=tk.TOP)
            self.storage[label] = int_slider
            tk.Label(stat_frame, text=label).pack(side=tk.TOP)

        # Outer defense
        defense_frame = tk.LabelFrame(self, text='Set Defence', labelanchor='n')
        inner_defense = DefenseFrame(defense_frame)
        inner_defense.pack()

        defense, magic_defense = inner_defense.get_vars()
        defense[0].set('dexterity')
        magic_defense[0].set('insight')

        self.storage['defense'] = {'attribute': defense[0], 'value': defense[1], 'bonus': defense[2]}
        self.storage['m_Defense'] = {'attribute': magic_defense[0],
                                     'value': magic_defense[1], 'bonus': magic_defense[2]}

        # Outer Affinity
        affinity_frame = tk.LabelFrame(self, text='Affinities', labelanchor='ne')
        rf = ResistFrame(master=affinity_frame)
        rf.pack()
        self.storage['Affinity'] = rf.resists

        # Attacks and Spells
        attack_frame = get_attack_frame(self, 'Attacks')
        spell_frame = get_attack_frame(self, 'Spells')
        named_abilities = get_attack_frame(self, 'Named Abilities', placeholder='Ability')

        # Specials
        special_ability_frame = SpecialsFrame(self)

        # Loot
        loot_frame = tk.LabelFrame(self, text='Inventory & Loot', labelanchor='n')
        self.storage['loot'] = {}
        LootFrameNM(master=loot_frame, box=self.storage).pack(fill='y')

        # Geometry
        fields_frame.place(x=5, y=5)
        attack_frame.place(x=115, y=235)
        spell_frame.place(in_=attack_frame, x=-1, rely=1.1)
        special_ability_frame.place(in_=spell_frame, x=-2, rely=1.2)
        named_abilities.place(in_=special_ability_frame, x=-1, rely=1.0)
        loot_frame.place(in_=named_abilities, x=-1, rely=1.05, width=389)
        affinity_frame.place(x=320, y=80, height=140)
        defense_frame.place(x=115, y=80, width=195)
        stat_frame.place(x=5, y=80)
        tk.Button(master=self, text="Create",  bg=SOFT_GREEN, font='Bold',
                  command=self.Ok).place(in_=stat_frame, relx=0.0, rely=1.05,
                                         width=100, height=90)

    def Ok(self):
        storage = self.storage

        def _parse_d(defense_dic):
            if defense_dic['attribute'].get() == '':
                raise TypeError("You must set defense attribute")
            return {k: v.get() for k, v in defense_dic.items()}

        def _parse_l(ability_lister):
            output = {}
            element_dict = ability_lister.attacks
            for element in element_dict.values():
                key = element[0].get()
                val = element[1].get()
                output.update({key: val})
            return output

        try:
            export = ExportModel(
                storage['name'].get(),
                storage['Type'].get(),
                storage['lvl'].get(),
                storage['initiative'].get(),
                storage['HP'].get(),
                storage['MP'].get(),
                storage['DEX'].get(),
                storage['INS'].get(),
                storage['MIG'].get(),
                storage['WLP'].get(),
                _parse_d(storage['defense']),
                _parse_d(storage['m_Defense']),
                storage['Affinity'],
                _parse_l(storage['Attacks']),
                _parse_l(storage['Spells']),
                storage['special_annotation'].get(index1='1.0', index2='end')[:-1],
                storage['crisis_ability'].get(),
                _parse_l(storage['Named Abilities']),
                storage['loot']
            )
            if FORBIDDEN_CHAR in export.name: raise NameError(f"there should be no {FORBIDDEN_CHAR} char in name")
            save_file_json(self.name.get(), export)
            self.master.master.master.destroy()

        except tk.TclError:
            x, y = self._get_x_y_for_popup()
            popup = generate_popup(x=x, y=y, name="Error!", wdh=320, ht=150)
            tk.Label(popup, text=int_error).pack()
        except TypeError as e:
            x, y = self._get_x_y_for_popup()
            popup = generate_popup(x=x, y=y, name="Error!", ht=40)
            tk.Label(popup, text=e.__str__()).pack()
        except NameError as e:
            x, y = self._get_x_y_for_popup()
            popup = generate_popup(x=x, y=y, name="Error!", ht=40)
            tk.Label(popup, text=e.__str__()).pack()
        except AttributeError:
            self.master.lift()

    def _get_x_y_for_popup(self):
        master = self.master.master.master
        x = master.winfo_x() + 100
        y = master.winfo_y() + 200
        return x, y


@dataclass_json
@dataclass
class ExportModel:
    name: str
    type: str
    lvl: int
    ini: int
    hp: int
    mp: int
    dex: int
    ins: int
    mg: int
    wp: int
    defense: dict
    md: dict
    affinity: dict
    attacks: dict
    spells: dict
    special_annotation: str
    crisis_ability: str
    named_abilities: dict
    loot: dict


class Monster(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!

    thanks to https://web.archive.org/web/20170514022131id_/http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

    """

    def __init__(self, master, *args, **kw):
        ttk.Frame.__init__(self, master, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill='y', side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                                yscrollcommand=vscrollbar.set, height=1280)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        interior = MonsterOnCanvas(self.canvas, width=530, height=800)
        interior_id = self.canvas.create_window(0, 0, window=interior,
                                                anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self.canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())

        self.canvas.bind('<Configure>', _configure_canvas)
        master.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        def calculate_sys_delta(delta):
            if get_sys() == 'Windows':
                return delta//120
            return delta

        c_delta = calculate_sys_delta(event.delta)
        self.canvas.yview_scroll(-1*c_delta, "units")
