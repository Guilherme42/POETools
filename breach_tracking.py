from keyboard import add_hotkey
from datetime import datetime
from os.path import exists
from win32gui import GetWindowText, GetForegroundWindow
from .MyLibs.MyTk import MyTk, RoundLabel


root = MyTk()

height = 20
width = 40
x_spacing = 50
y_spacing = 0
geometry = (0, 0)
colors = [("#FF0000", "#00FFFF"), ("#FFFFFF", "#000000"), ("#0000FF", "#FFFF00"), ("#000000", "#FFFFFF"), ("#800080", "#7FFF7F")]
canvasses = []
labels = []


for fill, outline in colors:
    canvas = RoundLabel(root, width, height, fill=fill, outline=outline, bg=root.transparentcolor)
    label = canvas.create_text(width//2, height//2, fill=outline, text="0/0")
    x = x_spacing * len(canvasses)
    y = y_spacing * len(canvasses)
    canvas.place(x=x, y=y)
    geometry = (max(geometry[0], x + width), max(geometry[1], y + height))
    canvasses.append(canvas)
    labels.append(label)


def load() -> None:
    if exists("breaches.log"):
        last_line = ""
        with open("breaches.log") as breaches:
            last_line = breaches.readlines()[-1]
        loaded = [item.split("/") for item in last_line.split("#")[-1].strip().split(" ")]
        for i in range(len(canvasses)):
            if len(loaded) >= i:
                canvasses[i].itemconfigure(labels[i], text=f"{loaded[i][0]}/{loaded[i][1]}")

def dump() -> None:
    text = f"# {datetime.now()} # "
    for i in range(len(canvasses)):
        text += canvasses[i].itemcget(labels[i], "text") + " "
    with open("breaches.log", "a") as breaches:
        breaches.write(text.strip() + "\n")

def add_breach(canvas, label) -> None:
    title = GetWindowText(GetForegroundWindow())
    if title != "Path of Exile": return
    text = canvas.itemcget(label, "text")
    bosses, total = text.split("/")
    canvas.itemconfigure(label, text=f"{bosses}/{int(total)+1}")
    dump()

def add_boss(canvas, label) -> None:
    title = GetWindowText(GetForegroundWindow())
    if title != "Path of Exile": return
    text = canvas.itemcget(label, "text")
    bosses, total = text.split("/")
    canvas.itemconfigure(label, text=f"{int(bosses)+1}/{total}")
    dump()


for i in range(len(canvasses)):
    add_hotkey(f"ctrl+{i+1}", add_breach, args=[canvasses[i], labels[i]])
    add_hotkey(f"shift+{i+1}", add_boss, args=[canvasses[i], labels[i]])


load()
root.geometry(f"{geometry[0]+1}x{geometry[1]+1}")
root.mainloop()