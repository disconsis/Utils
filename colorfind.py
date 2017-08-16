#!/usr/bin/python3
# TODO: fix opacity

from tkinter import (Tk, IntVar, StringVar, Entry, Button, Label, Scale,
                     HORIZONTAL, FLAT)

root = Tk()

color = ["R", "G", "B"]
var = [0, 0, 0]
slid = [0, 0, 0]


def slid_change(w):
    hex_str = '#'
    for i in range(3):
        hex_str += str(hex(round(var[i].get())))[2:].zfill(2)
    hex_var.set(hex_str)
    color_disp.config(bg=hex_str)


def disp_change():
    if len(hex_var.get()) == 6 \
            or (len(hex_var.get()) == 7 and hex_var.get()[0] == "#"):
        try:
            int(hex_var.get()[-6:], 16)
        except ValueError:
            return
        except Exception as err:
            print(err)
            return
        color_disp.config(bg="#"+hex_var.get()[-6:])
        var[3].set(100)
        for i in range(3):
            var[i].set(int(hex_var.get()[-6:][i*2:i*2+2], 16))


for i in range(3):
    var[i] = IntVar()
    slid[i] = Scale(root, variable=var[i], orient=HORIZONTAL, from_=0, to_=255,
                    label=color[i], showvalue=0, command=slid_change)
    slid[i].pack()

hex_var = StringVar()
hex_disp = Entry(root, relief=FLAT, textvariable=hex_var)
hex_disp.pack()

Button(root, text="displayThis", command=disp_change).pack()

color_disp = Label(root, width=20, height=20)
color_disp.pack()

root.mainloop()
