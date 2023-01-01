from argparse import ArgumentParser
from keyboard import send, write, add_hotkey
from time import sleep
from .MyLibs.POENinja import POENinja


parser = ArgumentParser()
parser.add_argument("--limit", type=int, default=10, help="Minimum value a beast must be worth to be searched for")
parser.add_argument("--harvest", action="store_true", help="If harvest beasts should be included")
args = parser.parse_args()


db = POENinja.get_beasts("Sanctum")
beasts = [beast for beast in db if db[beast] >= args.limit]
if not args.harvest: beasts = [beast for beast in beasts if not beast.startswith("Wild")]
if not args.harvest: beasts = [beast for beast in beasts if not beast.startswith("Vivid")]
if not args.harvest: beasts = [beast for beast in beasts if not beast.startswith("Primal")]
print(beasts)

# Add a hotkey for early exit
def clear():
    global beasts
    beasts = []
add_hotkey("end", clear)


def search():
    global beasts
    send("ctrl+f")
    beast = beasts.pop()
    write(f"{beast}|c={db[beast]}")
    send("enter")


# Add a hotkey to search for a beast
add_hotkey("shift+f1", search)


while beasts:
    sleep(0.01)
sleep(0.1)