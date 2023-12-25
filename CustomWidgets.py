import sys
import tkinter as tk
from tkinter import ttk

from tkhtmlview import HTMLLabel, HTMLScrolledText

from util_methods import dice_range


class LabeledScale(ttk.Frame):
    def __init__(self, label, variable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.var = variable

        ttk.Label(self, text=label, anchor='w').grid(row=0, column=0, sticky='w')
        dice_label = ttk.Label(self, text="d6", width=8, anchor='e')
        dice_label.grid(row=0, column=1)

        def label_foo(val):
            nonlocal dice_label
            value = dice_range[int(self.var.get())]
            dice_label.config(text=value)

        ttk.Scale(self, from_=0, to=3, orient=tk.HORIZONTAL, command=label_foo,
                  variable=self.var).grid(row=1, column=0, columnspan=2)

    def get(self):
        return int(self.var)


class ScrollableHTMLLabel(HTMLLabel):

    def _w_init(self, kwargs):
        HTMLScrolledText._w_init(self, kwargs=kwargs)
        if "background" not in kwargs.keys():
            if sys.platform.startswith("win"):
                self.config(background="SystemButtonFace")
            else:
                self.config(background="#d9d9d9")

        if "borderwidth" not in kwargs.keys():
            self.config(borderwidth=0)

        if "padx" not in kwargs.keys():
            self.config(padx=3)

    def fit_height(self):
        HTMLScrolledText.fit_height()
