import json
import tkinter as tk
from collections import defaultdict
from tkinter import filedialog as fd
from PIL import Image, ImageTk

from colors import *

tab_contents = set()
dice_range = ['d6', 'd8', 'd10', 'd12']


FORBIDDEN_CHAR = '¦'
DEXTERITY = 0
INSIGHT = 1
MIGHT = 2
WILLPOWER = 3
attributes = {'dexterity': DEXTERITY,
              'insight': INSIGHT,
              'might': MIGHT,
              'willpower': WILLPOWER,
              'const': 'const'}

loot_storage = {'zeni': 0, 'invpts': 0, 'lootable': ""}


def default_image():
    return tk.PhotoImage(file='images\\missing.png')


global_images = defaultdict(default_image)

RESISTS = ['physical', 'wind', 'bolt', 'dark', 'earth', 'fire', 'ice', 'light', 'poison']


def select_json(initial_dir='SavedChars'):
    filetypes = (
        ('json files', '*.json'),
        ('All files', '*.*'),
    )

    filename = fd.askopenfilename(
        title="Open a monster file",
        initialdir=initial_dir,
        filetypes=filetypes,
        multiple=True)
    return filename


def open_json(filepath):
    with open(filepath, 'r') as file:
        return file.read()


def reorder(event):
    notebook = event.widget
    try:
        index = notebook.index(f"@{event.x},{event.y}")
        notebook.insert(index, child=notebook.select())

    except tk.TclError:
        pass


def beautify_tabname(tab_name):
    split = tab_name.split("₩")
    if len(split) == 1:
        return split[0]
    return f'{split[0]} ({split[1]})'


def get_monster_image(name):
    try:
        img = Image.open(f'images\\{name}.png')
        x, y = 200, 200
        w, h = img.size
        if w > x or h > y:
            img.thumbnail((x, y), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(image=img)

        return img_tk
    except FileNotFoundError:
        return None


def safe_get(dictionary, key):
    value = None
    try:
        value = dictionary[key]
    finally:
        return value


def get_resist_color(value):
    match value:
        case -1:
            return "VB", RED
        case 0:
            return " ", GREY
        case 1:
            return "RS", BLACK
        case 2:
            return "IM", GREEN
        case 3:
            return "AB", MANA_BLUE


def generate_popup_from_event(event, name, wdh=300, ht=100):
    x_root = event.x_root
    y_root = event.y_root
    popup = generate_popup(x=x_root, y=y_root, name=name, ht=ht, wdh=wdh)
    return popup


def generate_popup(x, y, name, wdh=300, ht=100):
    popup = tk.Toplevel()
    popup.geometry(f'{wdh}x{ht}+{x - 20}+{y +20}')
    popup.title(name)
    popup.resizable(False, False)
    return popup


def fabricate_pair(master, label_text, width=3, var=None):
    one = tk.Label(master, text=label_text)
    two = tk.Entry(master, justify='right', width=width)
    if var:
        two.config(textvariable=var)
    else:
        two.insert(0, "0")
    return one, two


def save_file_json(default_name, payload):
    f = fd.asksaveasfile(initialfile=f'{default_name}.json',
                         defaultextension=".txt",
                         initialdir="SavedChars",
                         filetypes=[("All Files", "*.*"),
                                    ("JSON", "*.json"),
                                    ("Text Documents", "*.txt")])

    json_obj = payload.to_json()
    f.write(json_obj)
    f.close()


def check_tab(tab_name):
    if tab_name not in tab_contents:
        tab_contents.add(tab_name)
        return tab_name
    split = tab_name.split('₩')
    if len(split) == 1:
        return check_tab(f'{split[0]}₩{1}')
    return check_tab(f'{split[0]}₩{int(split[1]) + 1}')


def convert_dict_to_str_beauty(dictionary):
    out = f"Zenit: {dictionary['zenit']}, Inventory points: {dictionary['invpts']}"
    for x in dictionary['lootable']:
        out += f', {x}'
    return out
