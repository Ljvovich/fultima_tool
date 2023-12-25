import json

atr = {'dexterity': 'DEX', 'will': "WLP", 'insight': "INS", 'might': 'MIG'}


def _return_soldiers(champion):
    return int(champion[-1])


def beauty_armor(armor, arm_type):
    if armor['def'] > armor['defbonus']:
        value = armor['def']
    else:
        value = f"+ {armor['defbonus']}"
    if armor['mdef'] > armor['mdefbonus']:
        m_value = armor['mdef']
    else:
        m_value = f"+ {armor['mdefbonus']}"
    return f'{arm_type}: {armor["name"]}⬥ DEF {value}⬥ M.DEF {m_value}⬥ Init:{armor["init"]}⬥ {armor["cost"]} zenit'


def calculate_defense(payload, armory):
    armor_const = False
    armor_value = 0
    mdef_const = False
    mdef_value = 0
    m_bonus = 0
    a_bonus = 0
    ini_pen = 0
    if 'armor' in payload:
        armor = payload['armor']
        armory.append(beauty_armor(armor, 'Armor'))
        ini_pen += armor.get('init')
        if armor['def'] != 0:
            armor_const = True
            armor_value = armor.get('def')
        else:
            armor_value = armor.get('defbonus')

        if armor['mdef'] != 0:
            mdef_const = True
            mdef_value = armor.get('mdef')
        else:
            mdef_value = armor.get('mdefbonus')

    if 'shield' in payload:
        shield = payload['shield']
        armory.append(beauty_armor(shield, 'Shield'))
        ini_pen += shield.get('init')
        m_bonus += shield['mdefbonus']
        a_bonus += shield['defbonus']

    if 'extra' in payload:
        extra = payload.get('extra')
        if 'def' in extra:
            m_bonus += extra['mDef']
            a_bonus += extra['def']

    a_stat = 'const' if armor_const else "dexterity"
    m_stat = 'const' if mdef_const else "insight"

    defense = {"attribute": a_stat, "value": armor_value, "bonus": a_bonus}
    mag_defense = {"attribute": m_stat, "value": mdef_value, "bonus": m_bonus}
    return defense, mag_defense, ini_pen


def calculate_hp(mg, rank, extra, lvl):
    hp_multi = {"soldier": 1, 'elite': 2}
    base = mg * 5 + lvl * 2
    multi = _return_soldiers(rank) if rank.startswith('champion') else hp_multi.get(rank)
    if extra:
        hp = extra.get('hp')
        if hp:
            base += (int(hp))
    return base * multi


def calculate_mp(wp, rank, extra, lvl):
    base = wp * 5 + lvl
    if extra:
        mp = extra.get('mp')
        if mp:
            base += (int(mp))
    if rank.startswith('champion'): base *= 2
    return base


def check_name(name, keys):
    if name not in keys:
        return name
    if name[-1] != ')':
        return check_name(name + '(1)', keys)
    splitted = name.split('(')
    last = splitted[-1]
    try:
        number = int(last[:-1])
        number += 1
        new_name = splitted[0]
        if len(splitted) > 2:          #its possible if there were ( in name
            new_name = "(".join(splitted[:-1])
        return check_name(f'{new_name}({number})', keys)
    except ValueError:
        return check_name(name + '(1)', keys)
    except IndexError:
        return check_name(name + '(1)', keys)


def parse_super(payload, arsenal, armory):
    actions = payload.get('actions')
    abilities = payload.get('special')
    rare_gear = payload.get('raregear')

    loot = arsenal[:]
    loot += armory
    named_abilities = {}

    for named in (actions, abilities, rare_gear):
        if named:
            if named != rare_gear:
                for item in named:
                    handle_named_ability(item, named_abilities)
            else:
                gears = []
                for item in named:
                    gear = f"{item['name']}"
                    if item.get('effect'):
                        gear += f": {item['effect']}"
                        handle_named_ability(item, named_abilities)
                    gears.append(gear)
                loot += gears
    return named_abilities, {"loot": {"zenit": 0, "invpts": 0, "lootable": loot}}


def handle_named_ability(item, named_abilities):
    name = check_name(item['name'], named_abilities.keys())
    named_abilities.update({name: item['effect']})


def parse_type(rank, species):
    if rank == 'elite':
        return f'Elite {species}'
    elif rank.startswith("champion"):
        return f'{species} Champion'
    else:
        return species


def define_annotation(payload):
    annotation = ''
    if 'notes' in payload:
        for note in payload['notes']:
            annotation += f'<b>{note["name"]}</b>: {note["effect"]}<br>'
    elif 'description' in payload:
        annotation += payload['description']
    return annotation


class Weapon:
    def __init__(self, weapon):
        self.name = weapon['name']
        self.cost = weapon['cost']
        self.atr = (atr.get(weapon["att1"]), atr.get(weapon["att2"]))
        self.precision = weapon['prec']
        self.damage = weapon['damage']
        self.range = weapon['range']
        self.damage_type = weapon['type']
        self.hands = "One-handed" if weapon['hands'] == 1 else "Two-handed"

    def apply_bonuses(self, dmg, atk):
        self.precision += atk
        self.damage += dmg

    def attack(self):
        return f'⬥ {self._get_formula()}⬥ 【HR + {self.damage}】 {self.damage_type} damage'

    def __str__(self):
        formula = self._get_formula()
        damage = f'【HR + {self.damage}】 {self.damage_type} damage'
        cost = f'{self.cost} zenit'
        return f"Weapon: {self.name}⬥ {self.hands}⬥ {formula}⬥ {damage}⬥ {cost}"

    def _get_formula(self):
        formula = f'【{self.atr[0]}+{self.atr[1]}'
        if self.precision:
            if self.precision > 0: formula += "+ "
            formula += str(self.precision)
        formula += '】'
        return formula


def convert_spell(spell, bonus):
    name = spell['name']
    mp = str(spell.get('mp'))
    target = spell.get('target') if spell.get('target') else ""
    duration = spell.get('duration') if spell.get('duration') else ""
    offensive = True if spell['type'] == 'offensive' else False
    effect = str(spell.get('effect'))
    description = ''
    if offensive:
        description += f"<b>off.</b>⬥【{atr[spell['attr1']]}+{atr[spell['attr2']]}+{bonus}】"
    description += f'⬥ MP: {mp} ⬥{target} {duration} ⬥ Effect: {effect}'

    return {name: description}


def make_attack(attacks, spells, weapons, weapon_attacks, extra, lvl):
    bonus = lvl // 10
    bonus_damage = lvl // 20 * 5
    attack_bonus = 0
    spell_bonus = 0
    if extra:
        if extra.get('precision'): attack_bonus = 3
        if extra.get('magic'): spell_bonus = 3

    attacks_m = {}
    spells_m = {}

    for attack in attacks:
        attacks_m.update(convert_attack(attack, bonus=bonus + attack_bonus, bonus_damage=bonus_damage))

    if weapon_attacks:
        for attack in weapon_attacks:
            weapon = Weapon(attack['weapon'])
            weapons.append(weapon.__str__())
            w_bonus_d = 0 if 'flatdmg' not in attack else int(attack['flatdmg'])
            w_bonus_a = 0 if 'flathit' not in attack else int(attack['flathit'])
            if 'extraDamage' in attack: w_bonus_d += 5
            weapon.apply_bonuses(dmg=bonus_damage + w_bonus_d, atk=attack_bonus + bonus + w_bonus_a)
            description = weapon.attack()
            for special in attack['special']:
                description += f"⬥{special}"
            attacks_m.update({attack['name']: description})

    if spells:
        for spell in spells:
            spells_m.update(convert_spell(spell, bonus=bonus + spell_bonus))
    return attacks_m, spells_m


def convert_attack(attack, bonus, bonus_damage):
    if attack.get('extraDamage'): bonus_damage += 5
    name = attack.get('name')
    description = f"【{atr[attack['attr1']]}+{atr[attack['attr2']]}+{bonus}】⬥【HR+ {5 + bonus_damage}】 {attack['type']}"
    if attack['range'] == 'distance': description += ' ranged'
    for special in attack['special']:
        description += f"⬥{special}"

    return {name: description}


def calculate_ini(dex, ins, extra, penalty, rank):
    ini_by_rank = {"soldier": 0, 'elite': 2}
    base = dex + ins + 6
    bonus = _return_soldiers(rank) if rank.startswith('champion') else ini_by_rank.get(rank)
    if extra:
        ini_plus_4 = extra.get('init')
        if ini_plus_4: bonus += 4
        if 'extrainit' in extra:
            bonus += int(extra.get('extrainit'))
    if penalty:
        bonus += penalty
    return base + bonus


def convert_affinity(affinity_fu):
    converter = {'vu': -1, 'rs': 1, 'im': 2, 'ab': 3}
    return {k: converter.get(v) for k, v in affinity_fu.items()}


def convert(payload):
    weapons = []
    armory = []
    creature_rank = payload["rank"] if 'rank' in payload else "soldier"
    creature_type = parse_type(creature_rank, payload['species'])
    extra = payload["extra"] if 'extra' in payload else None

    lvl = payload['lvl']
    dex = payload['attributes']['dexterity'] // 2 - 3
    ins = payload['attributes']['insight'] // 2 - 3
    mg = payload['attributes']['might'] // 2 - 3
    wp = payload['attributes']['will'] // 2 - 3

    special_annotation = define_annotation(payload)
    attacks, spells = make_attack(payload.get('attacks'), payload.get('spells'),
                                  weapons, payload.get('weaponattacks'), extra, lvl)

    defense, m_defense, total_ini_penalty = calculate_defense(payload, armory)

    named_abilities, loot = parse_super(payload, weapons, armory)

    out_sistem_as_dict = {
        "name": payload['name'],
        "type": creature_type,
        "lvl": lvl,
        "ini": calculate_ini(dex, ins, extra, total_ini_penalty, creature_rank),
        "hp": calculate_hp(payload['attributes']['might'], creature_rank, extra, lvl),
        "mp": calculate_mp(payload['attributes']['will'], creature_rank, extra, lvl),
        "dex": dex,
        "ins": ins,
        "mg": mg,
        "wp": wp,
        "defense": defense,
        "md": m_defense,
        "affinity": convert_affinity(payload['affinities']),
        "attacks": attacks,
        "special_annotation": special_annotation,
    }
    for optional in [loot, named_abilities, spells]:
        if optional:
            out_sistem_as_dict.update(optional)
    out_system_payload = json.dumps(out_sistem_as_dict)
    return out_system_payload


if __name__ == "__main__":
    filepath = 'external/yuui_ui.json'
    with open(filepath, "r") as f:
        fultimator = json.load(f)
    out = convert(fultimator)
    print(out)
