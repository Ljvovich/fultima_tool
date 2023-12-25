import tkinter as tk
import tkinter.font as tk_font
from copy import copy
from collections import defaultdict
from tkinter.messagebox import askyesno
from tkinter.scrolledtext import ScrolledText

import util_methods
from PopUps import SetterHP, SetterSP, SetterOffset, SetterDefence
from Window import App
from util_methods import get_monster_image, generate_popup_from_event, global_images, RESISTS
from CustomFrames import ResistFrame

from tkhtmlview.html_parser import DEFAULT_STACK, Fnt
from CustomWidgets import ScrollableHTMLLabel as HTMLLabel
from colors import *

import test_strings

NEW_FONT_SIZE = 12
DEFAULT_STACK[Fnt.KEY][Fnt.SIZE] = [("__DEFAULT__", NEW_FONT_SIZE)]  # Dirty hack. to manipulate tkhtmlview


def status_button_fabric(master, label):
    ft = tk_font.Font(family='Times', size=13)
    return tk.Button(master, text=label, font=ft, fg=BLACK, bd=3, cursor='target', bg=GREY)


class MonsterFrame(tk.Frame):
    def __init__(self, tab, model, app_ref):
        super().__init__(master=tab)
        self.control = app_ref
        self.stat_dice = {}
        self.status_effects = defaultdict(bool)
        self.resists = defaultdict(int)
        self.guarded = False
        self.guarded_stat = []

        self.images = copy(global_images)
        self.model = model
        self.crisis_ability = self.model.crisis_ability
        try:
            self.resists.update(model.affinity)
        except TypeError:
            pass

        self.images[self.model.name] = get_monster_image(self.model.name)

        ft = tk_font.Font(family='Times', size=13)

        # nameplates
        nameplate = tk.Label(tab, fg=PURPLE, relief='raised', text=model.name)
        nameplate["cursor"] = "target"
        nameplate.place(x=20, y=20, width=300, height=50)

        lvl_frame = tk.LabelFrame(tab, fg=PURPLE, relief='raised', text='level')
        lvl_frame.place(x=350, y=20, width=40, height=50)
        tk.Label(lvl_frame, text=model.lvl, fg=PURPLE, font=ft, width=30, anchor='e').pack()

        type_frame = tk.LabelFrame(tab, fg=PURPLE, relief='raised', text='TYPE')
        type_frame.place(x=390, y=20, width=155, height=50)
        tk.Label(type_frame, anchor='e', text=model.type, fg=PURPLE, font=ft, width=150).pack()

        init_frame = tk.LabelFrame(tab, fg=PURPLE, relief='raised', text='Init.')
        init_frame.place(x=545, y=20, width=50, height=50)
        tk.Label(init_frame, text=model.initiative, fg=PURPLE, font="Times 16 bold").pack()

        # stats
        for i, stat in enumerate(["DEX", "INS", "MIG", "WLP"]):
            stat_y = (95 + i * 25)

            tk.Label(tab, font=ft, text=stat, relief='raised').place(x=40, y=stat_y, width=40, height=30)

            base_die = tk.Label(tab, font=ft, justify='left', relief='groove')
            base_die["text"] = model.get_stat('base', stat)
            base_die.place(x=90, y=stat_y, width=40, height=30)

            current_die = tk.Label(tab, justify='left', relief='sunken', cursor='target')
            current_die["text"] = model.get_stat('cur', stat)
            current_die.place(x=130, y=stat_y, width=40, height=30)
            show, hide = self.show_offset_tooltip_fabric(i)
            current_die.bind("<Enter>", show)
            current_die.bind("<Leave>", hide)

            self.stat_dice[stat] = current_die

        tk.Label(tab, text="base    /  current").place(x=85, y=70, width=100, height=25)
        stat_gear = tk.Button(tab, image=self.images['gear'], command=self.set_stat)
        stat_gear.place(x=20, y=95, width=20, height=20)
        stat_gear.bind("<Button-1>", self.set_stat)

        # statuses
        self.slow = status_button_fabric(tab, "Slow")
        self.slow["command"] = self.apply_slow
        self.slow.place(x=168, y=95, width=70, height=28)

        self.dazed = status_button_fabric(tab, "Dazed")
        self.dazed["command"] = self.apply_dazed
        self.dazed.place(x=168, y=120, width=70, height=28)

        self.weak = status_button_fabric(tab, "Weak")
        self.weak["command"] = self.apply_weak
        self.weak.place(x=168, y=145, width=70, height=28)

        self.shaken = status_button_fabric(tab, "Shaken")
        self.shaken["command"] = self.apply_shaken
        self.shaken.place(x=168, y=170, width=70, height=28)

        self.enraged = status_button_fabric(tab, "Enrage")
        self.enraged["command"] = self.apply_enraged
        self.enraged.place(x=240, y=95, width=80, height=53)

        self.poisoned = status_button_fabric(tab, "Poisoned")
        self.poisoned["command"] = self.apply_poison
        self.poisoned.place(x=240, y=145, width=80, height=53)

        # hp and sp
        hp_sp_label_frame = tk.LabelFrame(tab, text='HP and MP')
        hp_sp_label_frame.place(x=348, y=75)
        hp_font = tk_font.Font(family='Helvetica', size=19)
        # hp
        self.hp_bar = tk.Label(hp_sp_label_frame, fg=RED, text=model.current_hp, font=hp_font, cursor='cross')
        self.hp_bar.bind("<Button-1>", self.set_hp)
        self.hp_bar.grid(row=0, column=1)

        tk.Label(hp_sp_label_frame, fg=RED, text='HP', font=hp_font).grid(row=0, column=0)
        tk.Label(hp_sp_label_frame, fg=RED, text=f'/{model.maxhp}', font=hp_font).grid(row=0, column=2)

        # crisis
        self.in_crisis_label = tk.Label(hp_sp_label_frame, fg=YELLOW_TEXT, bg=RED, text="CRISIS",
                                        font=hp_font, cursor='cross')
        self.in_crisis_label.grid(row=1, columnspan=3)
        self.in_crisis_label.grid_remove()
        self.in_crisis_label.bind("<Enter>", self.show_crisis_tooltip)
        self.in_crisis_label.bind("<Leave>", self.hide_crisis_tooltip)

        self.tooltip_frame = tk.Frame(tab)
        tk.Label(self.tooltip_frame, text=self.crisis_ability or test_strings.crisis_ability,
                 bg=GREY, width=246, height=60,
                 relief='groove', anchor='nw', font="Helvetica 8 italic", fg=RED).pack()

        # sp
        self.sp_bar = tk.Label(hp_sp_label_frame, fg=MANA_BLUE, text=model.current_sp, font=hp_font, cursor='cross')
        self.sp_bar.bind("<Button-1>", self.set_sp)
        self.sp_bar.grid(row=2, column=1)

        tk.Label(hp_sp_label_frame, fg=MANA_BLUE, text='MP', font=hp_font).grid(row=2, column=0)
        tk.Label(hp_sp_label_frame, fg=MANA_BLUE, text=f'/{model.maxsp}', font=hp_font).grid(row=2, column=2)

        dmg_lf = tk.LabelFrame(hp_sp_label_frame, text='Damage:', width=250, height=50, labelanchor='ne')
        dmg_lf.grid(row=0, column=3)
        heal_lf = tk.LabelFrame(hp_sp_label_frame, text='Heal:', width=250, height=50, labelanchor='ne')
        heal_lf.grid(row=1, column=3)
        spend_lf = tk.LabelFrame(hp_sp_label_frame, text='Spend:', width=250, height=50, labelanchor='ne')
        spend_lf.grid(row=2, column=3)

        for i, point in enumerate([20, 10, 5, 1]):
            tk.Button(dmg_lf, text=point, width=2, height=1, fg=RED,
                      command=lambda x=point: self.damage(x)).grid(column=i, row=0)
            tk.Button(heal_lf, text=point, width=2, height=1, fg=GREEN,
                      command=lambda x=point: self.heal(x)).grid(column=i, row=0)
            tk.Button(spend_lf, text=point, width=2, height=1, fg=MANA_BLUE,
                      command=lambda x=point: self.spend(x)).grid(column=i, row=0)

        # Resists and defence
        defence_frame = tk.LabelFrame(tab, text='Resists and defence', labelanchor='n')
        defence_frame.place(x=40, y=222, width=280, height=160)

        tk.Label(defence_frame, text='DEF:', font=hp_font, fg=BLACK).grid(row=0, column=0, columnspan=3)
        tk.Label(defence_frame, text='M.DEF:', font=hp_font, fg=BLACK).grid(row=0, column=7, columnspan=3)

        defence_gear = tk.Button(defence_frame, image=self.images['gear'])
        self.shield = tk.Button(defence_frame, image=self.images['shield'],
                                command=self.guard)
        self.shield.grid(row=0, column=12)
        defence_gear.grid(row=0, column=11)
        defence_gear.bind("<Button-1>", self.set_def_man)

        self.cur_def = tk.Label(defence_frame, text=model.current_def, font=hp_font, fg=GREY, anchor="e", width=2)
        self.cur_def.grid(row=0, column=4, sticky="e")
        self.cur_m_def = tk.Label(defence_frame, text=model.current_mdef, font=hp_font, fg=GREY, anchor="e", width=2)
        self.cur_m_def.grid(row=0, column=10, sticky="e")

        self.resist_frame = ResistFrame(defence_frame, resists=self.resists)
        self.resist_frame.grid(row=1, columnspan=13)
        self.model.affinity = dict(self.resists)  # fill out any non initialized affinity to the model

        # portrait and buttons
        port = self.model.name if self.images[self.model.name] else 'monster'

        tk.Label(tab, image=self.images[port]).place(x=348, y=232, width=225, height=225)

        tk.Button(tab, text="Clone", command=self._clone).place(x=40, y=385, width=93, height=40)
        tk.Button(tab, text="Remove", command=self._ruin).place(x=133, y=385, width=93, height=40)
        tk.Button(tab, text="Loot", command=self._loot_yem).place(x=226, y=385, width=93, height=40)

        # ability block
        ability_frame = tk.LabelFrame(tab, text="Basic Attacks and Spells", labelanchor='n')
        ability_frame.place(x=1080 - 460, y=20, width=440, height=520)

        HTMLLabel(master=ability_frame, html=self.construct_ba(), height=520).pack()

        s_ability_frame = tk.LabelFrame(tab, text="Special Abilities", labelanchor='n')
        s_ability_frame.place(x=40, y=570, width=1020, height=300)
        HTMLLabel(master=s_ability_frame, html=self.construct_sp_ability()).pack(fill='both')

        # Loot
        loot_frame = tk.LabelFrame(tab, text="Inventory and Loot", labelanchor='nw')
        loot_frame.place(x=40, y=440, width=560, height=100)
        self.loot_content = ScrolledText(loot_frame)
        self.loot_content.pack()
        self.i_amount, self.z_amount, loot = self.construct_loot()
        self.loot_content.insert(1.0, loot)

        z = tk.Label(tab, image=self.images['z'])
        z.place(in_=loot_frame, rely=1.02)

        tk.Label(tab, textvariable=self.z_amount, font='14').place(in_=z, x=32, y=-1)
        i = tk.Label(tab, image=self.images['ip'])
        i.place(in_=z, y=-1, x=480)
        tk.Label(tab, textvariable=self.i_amount, font='14').place(in_=i, x=40, y=-1)

        # for case of clone
        self._check_crisis()
        self._check_statuses()

    def apply_slow(self):
        status = 'slow'
        button = self.slow
        self.apply_universal(status, button)

    def apply_weak(self):
        status = 'weak'
        button = self.weak
        self.apply_universal(status, button)

    def apply_dazed(self):
        status = 'dazed'
        button = self.dazed
        self.apply_universal(status, button)

    def apply_shaken(self):
        status = 'shaken'
        button = self.shaken
        self.apply_universal(status, button)

    def apply_enraged(self):
        status = 'enraged'
        button = self.enraged
        self.apply_universal(status, button)

    def apply_poison(self):
        status = 'poisoned'
        button = self.poisoned
        self.apply_universal(status, button)

    def apply_universal(self, status, button):
        if self.status_effects[status]:
            button.configure(fg=BLACK,
                             bg=GREY,
                             relief='raised')
            self.status_effects[status] = False
            self.model.unset_status(status)
        else:
            button.configure(fg=YELLOW_TEXT,
                             bg=PURPLE,
                             relief='sunken')
            self.status_effects[status] = True
            self.model.set_status(status)
        self.update_atr_and_armor()
        return

    def damage(self, point):
        self.model.damage(point)
        self.update_hp_sp()

    def heal(self, point):
        self.model.heal(point)
        self.update_hp_sp()

    def spend(self, point):
        self.model.spend(point)
        self.update_hp_sp()

    def update_hp_sp(self):
        self.hp_bar.config(text=self.model.current_hp)
        self.sp_bar.config(text=self.model.current_sp)
        self._check_crisis()

    def _check_crisis(self):
        if self.model.crisis:
            self.show_crisis()
        else:
            self.hide_crisis()

    def set_def_man(self, *args):
        defence = generate_popup_from_event(args[0], 'Set Defence', wdh=170, ht=150)
        SetterDefence(master=defence, slave=self)

    def set_stat(self, *args):
        defence = generate_popup_from_event(args[0], 'Set Defence', wdh=300, ht=70)
        SetterOffset(master=defence, slave=self)

    def set_hp(self, *args):
        set_hp = generate_popup_from_event(args[0], 'Set HP', wdh=200)
        SetterHP(master=set_hp, slave=self)

    def set_sp(self, *args):
        set_sp = generate_popup_from_event(args[0], 'Set MP', wdh=200)
        SetterSP(master=set_sp, slave=self)

    def show_crisis_tooltip(self, *args):  # args is required as event passes info about element
        self.tooltip_frame.place(x=350, y=175, width=246, height=55)

    def hide_crisis_tooltip(self, *args):
        self.tooltip_frame.place_forget()

    def show_crisis(self):
        self.in_crisis_label.grid()

    def hide_crisis(self):
        self.in_crisis_label.grid_remove()

    def show_offset_tooltip_fabric(self, stat):
        tooltip = tk.Frame()
        label = tk.Label(tooltip, anchor='nw', font="Helvetica 8 italic")
        label.pack()

        def show_tooltip(*args):
            text = f'current offset: {self.model.offset[stat]}'
            label.config(text=text)
            tooltip.place(x=40, y=243, width=110, height=20)

        def hide_tooltip(*args):
            tooltip.place_forget()

        return show_tooltip, hide_tooltip

    def construct_ba(self):
        construct = ""
        if attacks := self.model.attacks:
            construct += '<H4>Attacks</H4>'
            for atk_n, atk_d in attacks.items():
                construct += f'<b>{atk_n}</b>: {atk_d}<br>'
        if spell := self.model.spells:
            construct += "<H4>Spells</H4>"
            for spl_n, spl_d in spell.items():
                construct += f'<b>{spl_n}</b>: {spl_d}<br>'
        return construct

    def construct_sp_ability(self):
        construct = self.model.special_annotation
        if crisis := self.model.crisis_ability:
            construct += '<br><b>While in Crisis:</b><br>'
            construct += crisis
        if attacks := self.model.named_abilities:
            construct += '<H4>Abilities</H4>'
            for atk_n, atk_d in attacks.items():
                construct += f'<b>{atk_n}</b>: {atk_d}<br>'
        return construct

    def construct_loot(self):
        zeni = tk.IntVar()
        invpts = tk.IntVar()
        constructor = test_strings.loot + self.model.name

        if self.model.loot:
            zeni.set(self.model.loot['zenit'])
            invpts.set(self.model.loot['invpts'])
            constructor = '\n'.join(self.model.loot['lootable'])
        return invpts, zeni, constructor

    def _loot_yem(self):
        ls = util_methods.loot_storage
        zeni = self.z_amount.get()
        invpts = self.i_amount.get()
        loot = self.loot_content.get(index1=1.0, index2='end')
        ls['zeni'] += zeni
        ls['invpts'] += invpts
        if loot != '\n':
            ls['lootable'] += loot

        self._clean_loot()

    def update_atr_and_armor(self):
        for stat_dice in self.stat_dice:
            self.stat_dice[stat_dice].config(text=self.model.get_stat('cur', stat_dice))

        c_def, c_mdef = self.model.get_defs()
        self.cur_def.config(text=c_def)
        self.cur_m_def.config(text=c_mdef)

    def guard(self):
        if not self.guarded:
            self.guarded = True
            self.turn_guard()
            for affinity in RESISTS:
                if self.resists[affinity] + 1 > 1:
                    self.resists[affinity] = self.resists[affinity]
                else:
                    self.resists[affinity] += 1
                    self.guarded_stat.append(affinity)
                self.resist_frame.update_label(affinity)
        else:
            self.guarded = False
            self.turn_of_guard()
            for affinity in self.guarded_stat:
                if self.resists[affinity] > 1:
                    continue
                self.resists[affinity] -= 1
                if self.resists[affinity] < -1: self.resists[affinity] = -1
                self.resist_frame.update_label(affinity)
            self.guarded_stat.clear()

    def turn_guard(self):
        self.shield.configure(relief='sunken', bg=PURPLE)

    def turn_of_guard(self):
        self.shield.configure(relief='raised', bg=DEFAULT_COLOR)

    def _ruin(self):
        self.master.destroy()

    def _clone(self):
        model = copy(self.model)
        resists = dict(self.resists)

        if resists != model.affinity:
            answer = askyesno(title="Affinity collision",
                              message=test_strings.affinity_collision)
            if answer:
                model.affinity = resists
        App.generate_monster_tab(tab_control=self.control, monster=model)

    def _check_statuses(self):
        control = []
        for status in ['slow', 'dazed', 'weak', 'shaken', 'enraged', 'poisoned']:
            if self.model.statuses[status]:
                self.status_effects[status] = True
                control.append(status)
        for status in control:
            match status:
                case 'slow':
                    self.slow.configure(fg=YELLOW_TEXT, bg=PURPLE, relief='sunken')
                case 'weak':
                    self.weak.configure(fg=YELLOW_TEXT, bg=PURPLE, relief='sunken')
                case 'dazed':
                    self.dazed.configure(fg=YELLOW_TEXT, bg=PURPLE, relief='sunken')
                case 'shaken':
                    self.shaken.configure(fg=YELLOW_TEXT, bg=PURPLE, relief='sunken')
                case 'enraged':
                    self.enraged.configure(fg=YELLOW_TEXT, bg=PURPLE, relief='sunken')
                case 'poisoned':
                    self.poisoned.configure(fg=YELLOW_TEXT, bg=PURPLE, relief='sunken')

    def _clean_loot(self):
        self.z_amount.set(0)
        self.i_amount.set(0)
        self.loot_content.delete(1.0, 'end')
        try:
            self.model.loot.clear()
        except AttributeError:
            pass
