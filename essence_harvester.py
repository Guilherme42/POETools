from requests import get
from typing import List, Set
import pprint as pp
import re
import argparse

ap = argparse.ArgumentParser(description="Essence reroll with harvest.")
ap.add_argument("-t", "--treshold", type=float, action="store", default=1, help="Cuttoff value for scarab price. Any below this will be highlighted")
ap.add_argument("-l", "--limit", type=int, action="store", default=250, help="")
ap.add_argument("-d", "--debug", action="store_true", help="Enables debug session", default=False)
ap.add_argument("-p", "--print_prices", action="store_true", default=False, help="Prints latest price list.")
ap.add_argument("-f", "--flip", action="store", type=int, help="Prints a regex with the cheapest N scarabs to put into Faustus' search bar to flip them.", default=None)
ap.add_argument("-fk", "--force-keep", action="store", nargs="*", required=False, default=[], help="List of scarabs to force to be kept. Case insensitive, accepts regex.")
args = ap.parse_args()

# Dynamically get the name of the current league
league = get("https://poe.ninja/poe1/api/data/index-state").json()["economyLeagues"][0]["name"]

# Get the updated price of each scarab in chaos
db = get(f"https://poe.ninja/poe1/api/economy/exchange/current/overview?league={league}&type=Essence").json()
names = {item["id"]: item["name"] for item in db["items"]}
names = {id: f"^{name.lower()}$" for id, name in names.items()}
prices = {names[item["id"]]: item["primaryValue"] for item in db["lines"]}

def calc_EV(prices: dict, essence: str) -> float:
    target_essence_price = prices[f'^{essence}$'] if essence[-1] != '$' else prices[essence]
    sum = 0
    for p in prices.items():
        sum += (p[1] - target_essence_price)
    sum = sum/(len(prices)-1)
    return sum

# Constant values
RED     = '\033[31m'
REDB    = '\033[31;1m'
REDBB   = '\033[31;1,4m'
REG     = '\033[33;1m'
GRE     = '\033[32m'
FORCED  = '\033[34;1mforced - '
NFORCED = '\033[34;1m'
END     = '\033[0m'


def print_all(prices: dict):
    longest_essence_name_len = len(max(prices, key=len)[1:-1])
    prices_sort = sorted(prices.items(), key = lambda x: x[1], reverse=True)
    for essence,_ in prices_sort:
        EV = calc_EV(prices, essence)
        color = RED if EV <= 0 else GRE
        print(f'{essence[1:-1]: <{longest_essence_name_len}}\t\t{color}{EV}{END}')

print_all(prices)