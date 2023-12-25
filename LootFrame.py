import tkinter as tk

import util_methods


def on_loot_focus(*args):
    storage = util_methods.loot_storage
    args[0].widget.load(storage)
    storage['zeni'] = 0
    storage['invpts'] = 0
    storage['lootable'] = ''


class LootFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zeni = tk.IntVar()
        self.invpnt = tk.IntVar()
        self.content = tk.StringVar()

        zeni_fr = tk.LabelFrame(self, labelanchor='ne', text='Zenits')
        inv_fr = tk.LabelFrame(self, labelanchor='ne', text='Inventory \n Points')

        tk.Label(zeni_fr, textvariable=self.zeni).pack()
        tk.Label(inv_fr, textvariable=self.invpnt).pack()

        zeni_fr.pack(side=tk.LEFT, anchor='nw')
        inv_fr.pack(side=tk.RIGHT, anchor='ne')
        tk.Label(self, textvariable=self.content, anchor='nw').pack(side=tk.TOP, fill='both')

        tk.Button(self, text='Clear', command=self._clear, width=50).pack(side=tk.BOTTOM, anchor='sw', pady=70)

    def _clear(self):
        self.zeni.set(0)
        self.invpnt.set(0)
        self.content.set("")

    def load(self, payload):
        new_zeni = payload['zeni'] + self.zeni.get()
        self.zeni.set(new_zeni)
        new_invpnt = payload['invpts'] + self.invpnt.get()
        self.invpnt.set(new_invpnt)
        text = self.content.get() + payload['lootable']
        self.content.set(text)
