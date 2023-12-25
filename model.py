import json

import ExternalImport
from util_methods import *


offsets = {'slow': [-1, 0, 0, 0], 'dazed': [0, -1, 0, 0], 'weak': [0, 0, -1, 0],
           'shaken': [0, 0, 0, -1], 'enraged': [-1, -1, 0, 0], 'poisoned': [0, 0, -1, -1]}


class Character:

    def __init__(self, input_json: str):

        self.statuses = {'slow': False, 'dazed': False, 'weak': False,
                         'shaken': False, 'enraged': False, 'poisoned': False}

        self.payload_back_up = input_json
        payload = json.loads(input_json)

        self.name = payload['name']
        if FORBIDDEN_CHAR in self.name: raise NameError(f"there should be no {FORBIDDEN_CHAR} char in name")

        self.lvl = payload['lvl']
        self.type = payload['type']
        self.initiative = payload['ini']
        self.maxhp = payload['hp']
        self.current_hp = payload['hp']
        self.maxsp = payload['mp']
        self.current_sp = payload['mp']

        self.crisis = False

        self.base_attributes = [payload['dex'], payload['ins'], payload['mg'], payload['wp']]
        self.cur_attrs = self.base_attributes[:]  # copy of base
        self.offset = [0, 0, 0, 0]  # dx ins mg wp

        self.defence_formula = self.parse_def(payload['defense'])
        self.mdef_formula = self.parse_def(payload['md'])  # order is important. do not refactor

        self.current_def = None
        self.current_mdef = None

        self._calculate_def(magic=False)
        self._calculate_def(magic=True)

        self.special_annotation = payload['special_annotation']

        # These could be None
        self.loot = payload.get('loot')
        self.crisis_ability = payload.get('crisis_ability')
        self.affinity = payload.get('affinity')
        self.named_abilities = payload.get('named_abilities')

        self.attacks = payload.get('attacks')
        self.spells = payload.get('spells')

        other = self.trim(payload)
        self._parse_other(other)

    def get_stat(self, stat_type, stat):
        match stat_type:
            case "base":
                match stat:
                    case "DEX":
                        return self._get_base_dx()
                    case "INS":
                        return self._get_base_ins()
                    case "MIG":
                        return self._get_base_mg()
                    case "WLP":
                        return self._get_base_wp()
            case "cur":
                match stat:
                    case "DEX":
                        return self._get_current_dx()
                    case "INS":
                        return self._get_current_ins()
                    case "MIG":
                        return self._get_current_mg()
                    case "WLP":
                        return self._get_current_wp()

    def get_defs(self):
        return self.current_def, self.current_mdef

    def set_hp(self, value):
        self.current_hp = value
        self._crisis_check()

    def set_sp(self, value):
        self.current_sp = value

    def set_new_armor_formula(self, defense_formula, m_defense_formula):
        defense = self.parse_def(defense_formula)
        m_defense = self.parse_def(m_defense_formula)

        self.defence_formula = defense
        self.mdef_formula = m_defense

        self._calculate_def(magic=False)
        self._calculate_def(magic=True)

    def reset_attr(self):
        self.cur_attrs = self.base_attributes[:]

    def external_offset(self, offset):
        self._apply_offset(offset)
        self._recalculate_current_attributes()

    def damage(self, amount):
        current = self.current_hp
        current -= amount
        self.current_hp = current if current > 0 else 0
        self._crisis_check()

    def heal(self, amount):
        current = self.current_hp
        if current > self.maxhp: return
        current += amount
        self.current_hp = current if current <= self.maxhp else self.maxhp
        self._crisis_check()

    def spend(self, amount):
        current = self.current_sp
        current -= amount
        self.current_sp = current if current > 0 else 0

    def _apply_offset(self, delta):
        self.offset = [sum(x) for x in zip(self.offset, delta)]

    def set_status(self, status):

        if status not in offsets.keys():
            return

        if self.statuses[status]:
            return

        offset = offsets[status]
        self._apply_offset(offset)
        self.statuses[status] = True
        self._recalculate_current_attributes()
        return

    def unset_status(self, status):
        if not self.statuses[status]:
            return
        offset = [x * (-1) for x in offsets[status]]
        self._apply_offset(offset)
        self.statuses[status] = False
        self._recalculate_current_attributes()
        return

    def _get_current_dx(self):
        return dice_range[self.cur_attrs[DEXTERITY]]

    def _get_current_wp(self):
        return dice_range[self.cur_attrs[WILLPOWER]]

    def _get_current_mg(self):
        dice = dice_range[self.cur_attrs[MIGHT]]
        return dice

    def _get_current_ins(self):
        return dice_range[self.cur_attrs[INSIGHT]]

    def _get_base_dx(self):
        return dice_range[self.base_attributes[DEXTERITY]]

    def _get_base_wp(self):
        return dice_range[self.base_attributes[WILLPOWER]]

    def _get_base_mg(self):
        return dice_range[self.base_attributes[MIGHT]]

    def _get_base_ins(self):
        return dice_range[self.base_attributes[INSIGHT]]

    def _recalculate_current_attributes(self):
        new_attrs = []
        check_def = False
        check_mdef = False

        for x, y in zip(self.base_attributes, self.offset):
            z = x + y
            if z < 0:
                new_attrs.append(0)
            elif z > 3:
                new_attrs.append(3)
            else:
                new_attrs.append(z)

        if self.defence_formula['type'] != 'const':
            ind = self.defence_formula['type']
            if self.cur_attrs[ind] != new_attrs[ind]:
                check_def = True

        if self.mdef_formula['type'] != 'const':
            ind = self.mdef_formula['type']
            if self.cur_attrs[ind] != new_attrs[ind]:
                check_mdef = True

        self.cur_attrs = new_attrs

        if check_def:
            self._calculate_def(magic=False)
        if check_mdef:
            self._calculate_def(magic=True)

    def _calculate_def(self, magic):
        defence_formula = {True: self.mdef_formula,
                           False: self.defence_formula}.get(magic)

        mod = 0 if 'bonus' not in defence_formula else defence_formula.get('bonus')

        if defence_formula.get('type') == 'const':
            if magic:
                self.current_mdef = defence_formula['value'] + mod
            else:
                self.current_def = defence_formula['value'] + mod
        else:
            dice = dice_range[self.cur_attrs[(defence_formula['type'])]]
            die_top_val = int(dice[1:])
            delta = die_top_val + defence_formula['value'] + mod
            if magic:
                self.current_mdef = delta
            else:
                self.current_def = delta

    def _crisis_check(self):
        crisis = int(self.maxhp / 2)
        if self.current_hp <= crisis:
            self.crisis = True
        else:
            self.crisis = False

    def _parse_other(self, other):
        if other:
            for i, v in other.items():
                if self.named_abilities:
                    self.named_abilities.update({i: v})
                else:
                    self.named_abilities = {i: v}

    @staticmethod
    def parse_def(payload):
        defence = {'type': attributes.get(payload['attribute']), 'value': payload['value']}
        if 'bonus' in payload:
            defence.update({'bonus': payload['bonus']})
        return defence

    @staticmethod
    def trim(payload):
        to_exclude = ['name', 'ini', 'hp', 'mp',
                      'dex', 'ins', 'mg', 'wp',
                      'defense', 'md', 'type', 'lvl',
                      "special_annotation", 'loot', 'spells', 'named_abilities',
                      'crisis_ability', 'affinity', 'attacks']

        for flag in to_exclude:
            try:
                payload.pop(flag)
            except KeyError:
                continue
        return payload

    @classmethod
    def from_fultimator(cls, fultimator):
        return cls(ExternalImport.convert(fultimator))
