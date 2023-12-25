import tkinter as tk

import test_strings
from util_methods import global_images

super_images = {
    "t": "superiority/track",
    '-': "superiority/minus",
    '+': "superiority/plus",
    'm': "superiority/mark",
    'p': "superiority/pass"
}


class Superiority(tk.Frame):
    coordinates = {
        -5: (130, 28),
        -4: (262, 28),
        -3: (394, 28),
        -2: (525, 28),
        -1: (658, 28),
        0: (797, 28),
        1: (951, 28),
        2: (1083, 28),
        3: (1215, 28),
        4: (1347, 28),
        5: (1480, 28)
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = 0

        track = tk.Canvas(self, width=1500, height=170)
        track.place(x=101, y=0)
        path = global_images.get(super_images['t'])
        track.create_image(1500, 0, image=path, anchor='ne')
        p = tk.Label(self, image=global_images.get(super_images['p']), cursor='target')
        tk.Button(self, image=global_images.get(super_images['-']),
                  command=self.minus, width=100, height=100).place(x=10, y=25)

        p.place(x=770, y=-2)
        p.bind("<Button-1>", self.reset)
        tk.Button(self, image=global_images.get(super_images['+']),
                  command=self.plus, width=100, height=100).place(x=1590, y=25)
        self.shield = tk.Label(self, image=global_images.get(super_images['m']))
        self.place_shield()
        tk.Label(self, text=test_strings.superiority_hit).place(in_=track, x=0, rely=1)

    def plus(self):
        self.position += 1
        if self.position > 5: self.position = 5
        self.place_shield()

    def minus(self):
        self.position -= 1
        if self.position < -5: self.position = -5
        self.place_shield()

    def reset(self, *args):
        self.position = 0
        self.place_shield()

    def place_shield(self):
        x, y = self.coordinates.get(self.position)
        self.shield.place(x=x, y=y)
