from tkinter import ttk
import BattleWidget
import CreateNewMonster
import Superiority
from CustomFrames import HelpFrame
from LootFrame import LootFrame, on_loot_focus
from model import Character
from util_methods import *
from util_methods import check_tab


class App:
    def __init__(self, window):
        # setting title
        window.title("FUltima battle tool")
        # setting window size
        width = 1080
        height = 1000
        screenwidth = window.winfo_screenwidth()
        screenheight = window.winfo_screenheight()
        align_str = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        window.geometry(align_str)
        window.resizable(width=False, height=True)

        # initialize images
        self._load_images()

        # create a menu
        menubar = tk.Menu(window)
        window.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=False)
        misc_menu = tk.Menu(menubar, tearoff=False)

        menubar.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='New Creature', command=self.create_mob_window)
        file_menu.add_command(label='Open Creature', command=self.open_mob)
        file_menu.add_command(label='From Fultimator', command=self.convert_and_open)
        file_menu.add_command(label='Exit', command=window.destroy)

        menubar.add_cascade(label='Show/Hide', menu=misc_menu)
        misc_menu.add_command(label='Superiority', command=self.open_superiority)
        misc_menu.add_command(label='Loot', command=self.show_hide_loot)
        misc_menu.add_command(label='Help', command=self.show_hide_help)

        # create tabs
        tab_control = ttk.Notebook(window)
        tab_control.bind("<B1-Motion>", reorder)
        self.tab_control = tab_control
        self.loot = LootFrame()
        self.loot.bind("<Expose>", on_loot_focus)
        self.help = HelpFrame()

        tab_control.add(self.help, text='How to Use Me')
        tab_control.add(self.loot, text='Loot')
        tab_control.pack(expand=1, fill="both")

    def show_hide_help(self):
        self._show_hide(self.help)

    def show_hide_loot(self):
        self._show_hide(self.loot)

    def open_mob(self):
        fp = select_json()
        chars_to_open = []
        for file in fp:
            pl = open_json(file)
            try:
                chars_to_open.append(Character(pl))
            except NameError as e:
                x, y = root.winfo_x() + 300, root.winfo_y() + 300
                popup = generate_popup(x=x, y=y, name="Error!", ht=40)
                tk.Label(popup, text=e.__str__()).pack()
        self.open_and_reorganize(chars_to_open)

    def open_and_reorganize(self, chars_to_open):
        if chars_to_open:
            for i in chars_to_open:
                self.generate_monster_tab(monster=i, tab_control=self.tab_control)
        self.reorganize_tabs()

    def convert_and_open(self):
        fps = select_json(initial_dir='external')
        chars_to_open = []
        for file in fps:
            with open(file, "r", encoding='utf-8') as f:
                fultimator = json.load(f)
                model = Character.from_fultimator(fultimator)
                chars_to_open.append(model)
        self.open_and_reorganize(chars_to_open)

    @staticmethod
    def generate_monster_tab(monster: Character, tab_control):
        tab_name = monster.name
        tab_frame = tk.Frame()
        tab_control.add(tab_frame, text=beautify_tabname(check_tab(tab_name)))
        BattleWidget.MonsterFrame(tab=tab_frame, model=monster, app_ref=tab_control)

    @staticmethod
    def create_mob_window():
        current_x_y = root.winfo_x(), root.winfo_y()
        new_creature = tk.Toplevel(root)
        x, y = 530, 800
        new_creature.geometry(f"{x}x{y}+{current_x_y[0]}+{current_x_y[1]}")
        new_creature.resizable(width=False, height=True)
        new_creature.title("Create You Creature")
        new_creature.minsize(x, x)
        new_creature.maxsize(x, 1280)
        CreateNewMonster.Monster(master=new_creature, width=x, height=9999).pack(fill='y')

    @staticmethod
    def open_superiority():
        current_x_y = root.winfo_x() - 250, root.winfo_y() + 100
        super_track = tk.Toplevel(root)
        x, y = 1700, 300
        super_track.geometry(f"{x}x{y}+{current_x_y[0]}+{current_x_y[1]}")
        super_track.resizable(width=False, height=False)
        super_track.title("Superiority Track")
        Superiority.Superiority(master=super_track, width=x, height=y).pack()

    @staticmethod
    def _load_images():
        for key in ['gear', *RESISTS, 'monster',
                    'plus', 'minus', 'z',
                    'ip', 'shield', *Superiority.super_images.values()]:
            try:
                global_images[key] = tk.PhotoImage(file=f'images/{key}.png')
            except tk.TclError as e:
                # TODO swap to log
                print(e)

    def reorganize_tabs(self):
        self.tab_control.hide(self.help)
        self.tab_control.insert(pos="end", child=self.loot)
        self.tab_control.select(self.tab_control.tabs()[-2])

    def _show_hide(self, param):
        state = self.tab_control.tab(param)
        if state['state'] == 'hidden':
            self.tab_control.select(param)
        else:
            self.tab_control.hide(param)


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_create("MainStyle", parent="clam", settings={
        "TNotebook.Tab": {"configure": {"padding": [60, 10]}, }})

    style.theme_use("MainStyle")

    app = App(root)
    root.mainloop()
