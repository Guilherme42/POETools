from tkinter import Label
from .mytk import MyTk
from .roundlabel import RoundLabel


root = MyTk()

canvas = RoundLabel(root, 40, 20, fill="#FF0000", outline="#00FFFF", bg=root.transparentcolor)
canvas.create_text(20, 10, fill="#00FFFF", text="1")
canvas.place(x=0, y=0)
RoundLabel(root, 40, 20, fill="#FFFFFF", outline="#000000", bg=root.transparentcolor).place(x= 50, y=0)
RoundLabel(root, 40, 20, fill="#0000FF", outline="#FFFF00", bg=root.transparentcolor).place(x=100, y=0)
RoundLabel(root, 40, 20, fill="#000000", outline="#FFFFFF", bg=root.transparentcolor).place(x=150, y=0)
RoundLabel(root, 40, 20, fill="#800080", outline="#7FFF7F", bg=root.transparentcolor).place(x=200, y=0)

root.geometry("241x21")
root.mainloop()