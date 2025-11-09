from requests import get
from typing import Set
import re
import sys


# Constant values
treshold = 1 if len(sys.argv) < 2 else float(sys.argv[1])
DEBUGGER = False

# Print Debug info when DEBUG flag is active
DEBUG = lambda x: print(x) if DEBUGGER else None

# Dynamically get the name of the current league
league = get("https://poe.ninja/poe1/api/data/index-state").json()["economyLeagues"][0]["name"]

# Get the updated price of each scarab in chaos
db = get(f"https://poe.ninja/poe1/api/economy/exchange/current/overview?league={league}&type=Scarab").json()
DEBUG(db)
names = {item["id"]: item["name"] for item in db["items"]}
names = {id: f"^{name}$" for id, name in names.items()}
prices = {names[item["id"]]: item["primaryValue"] for item in db["lines"]}

# Find the scarabs that are too cheap to be worth selling
sell = [name for name, value in prices.items() if value < treshold]
keep = [name for name, value in prices.items() if value >= treshold]

# Get the shorter list
highlight, exclude, negate = (sell, keep, False) if len(sell) <= len(keep) else (keep, sell, True)

# Concatenate all the names of the scarabs to exclude so it is easer to check if a sub-string is present
full_exclude = ",".join(exclude)

# Save all the regexes that uniquely select the scarabs to keep
regexes = {}

# Get the shortest string in the name of each highlight scarab that is not present in the names of the scarabs to exclude
for name in highlight:
    for size in range(len("Scarab"), len(name)+1):
        for start in range(len(name)-size+1):
            if name[start:start+size] not in full_exclude and "Scarab" in name[start:start+size]:
                regexes.setdefault(name, []).append(name[start:start+size])
    if name not in regexes: raise Exception(f"No regex found for '{name}'")

# Check how many scarabs would be selected by each regex
regex_count = {}
for name, data in regexes.items():
    for regex in data:
        regex_count[regex] = regex_count.get(regex, 0) + 1

# Assign a weight/score for each regex based on how many scarabs they select and how long they are
regex_score = {regex: len(regex) - count - (5 if regex.startswith("^Scarab") or regex.startswith("Scarab") or regex.endswith("Scarab") or regex.endswith("Scarab$") else 0) for regex, count in regex_count.items()}

# Find the best regex for all scarabs
# This is done by finding the scarab with the worst best regex and fixing that
# Then all the other scarabs that also have that regex will use that regex
# Repeat untill all scarabs have regexes
to_assing = highlight[:]
regex_assigns = {}
while to_assing:
    regex_tmp = {name: min(regexes[name], key=lambda x: regex_score[x]) for name in to_assing}
    worst_name, worst_regex = max(regex_tmp.items(), key=lambda x: regex_score[x[1]])
    for name in to_assing[:]:
        if worst_regex in regexes[name]:
            regex_assigns[name] = worst_regex
            to_assing.remove(name)

# Uniquefy the regexes to avoid repetition
all_regexes = set(regex_assigns.values())

# Group the regexes based on if they involve the start of the line or not
full_regexes = []
start_regexes = []
midle_regexes = []
end_regexes = []
for regex in all_regexes:
    if regex.startswith("^") and regex.endswith("$"): full_regexes.append(regex)
    elif regex.startswith("^"): start_regexes.append(regex)
    elif regex.endswith("$"): end_regexes.append(regex)
    else: midle_regexes.append(regex)

# Create the full regex string based on the individual regexes
# "!^(<full lines>|(<starts without Scarab>|Scarab (<starts without "of">|of (<starts with "of">))).*)|.*(<midle without Scarab at the start or the end>|Scarab (<>|of ())|<> Scarab).*|.*(<>|() Scarab)$"
# "!^(r1|(r21|Scarab (r221|of (r222))).*)|.*(r31|Scarab (r321|of (r322))|r33 Scarab|r34 Scarab ).*|.*(r41|(r42) Scarab)$"
def gen_regex(all_regexes: Set[str], negate: bool) -> str:
    regexes = list(all_regexes)
    DEBUG(sorted(regexes))
    # Regexes that match a full line
    r1 = [item for item in regexes if item.startswith("^") and item.endswith("$")]
    for item in r1: regexes.remove(item)
    r1 = [item.strip("^$") for item in r1]
    DEBUG(f"r1={r1}")
    # Regexes that match the start of a line but don't start with "Scarab "
    r21 = [item for item in regexes if item.startswith("^") and not item.strip("^").startswith("Scarab ")]
    for item in r21: regexes.remove(item)
    r21 = [item.strip("^") for item in r21]
    DEBUG(f"r21={r21}")
    # Regexes that match the start of a line and start with "Scarab " but don't start with "Scarab of "
    r221 = [item for item in regexes if item.startswith("^") and item.strip("^").startswith("Scarab ") and not item.strip("^").startswith("Scarab of ")]
    for item in r221: regexes.remove(item)
    r221 = [item.strip("^").replace("Scarab ", "") for item in r221]
    DEBUG(f"r221={r221}")
    # Regexes that match the start of a line and start with "Scarab of "
    r222 = [item for item in regexes if item.startswith("^") and item.strip("^").startswith("Scarab of ")]
    for item in r222: regexes.remove(item)
    r222 = [item.strip("^").replace("Scarab of ", "") for item in r222]
    DEBUG(f"r222={r222}")
    # Regexes that don't match the end of a line of the line and doesn't start with "Scarab " neither ends with " Scarab"
    r31 = [item for item in regexes if not item.endswith("$") and not item.startswith("Scarab ") and not item.endswith(" Scarab") and not item.endswith(" Scarab ")]
    for item in r31: regexes.remove(item)
    DEBUG(f"r31={r31}")
    # Regexes that don't match the end of a line of the line and start with "Scarab " but don't start with "Scarab of "
    r321 = [item for item in regexes if not item.endswith("$") and item.startswith("Scarab ") and not item.startswith("Scarab of ")]
    for item in r321: regexes.remove(item)
    r321 = [item.replace("Scarab ", "") for item in r321]
    DEBUG(f"r321={r321}")
    # Regexes that don't match the end of a line of the line and start with "Scarab of "
    r322 = [item for item in regexes if not item.endswith("$") and item.startswith("Scarab of ")]
    for item in r322: regexes.remove(item)
    r322 = [item.replace("Scarab of ", "") for item in r322]
    DEBUG(f"r322={r322}")
    # Regexes that don't match the end of a line of the line and ends with " Scarab"
    r33 = [item for item in regexes if not item.endswith("$") and item.endswith(" Scarab")]
    for item in r33: regexes.remove(item)
    r33 = [item.replace(" Scarab", "") for item in r33]
    DEBUG(f"r33={r33}")
    # Regexes that don't match the end of a line of the line and ends with " Scarab "
    r34 = [item for item in regexes if not item.endswith("$") and item.endswith(" Scarab ")]
    for item in r34: regexes.remove(item)
    r34 = [item.replace(" Scarab ", "") for item in r34]
    DEBUG(f"r34={r34}")
    # Regexes that match the end of a line of the line and doesn't ends with " Scarab"
    r41 = [item for item in regexes if item.endswith("$") and not item.strip("$").endswith(" Scarab")]
    for item in r41: regexes.remove(item)
    DEBUG(f"r41={r41}")
    # Regexes that match the end of a line of the line and ends with " Scarab"
    r42 = [item for item in regexes if item.endswith("$") and item.strip("$").endswith(" Scarab")]
    for item in r42: regexes.remove(item)
    r42 = [item.strip("$").replace(" Scarab", "") for item in r42]
    DEBUG(f"r42={r42}")
    if regexes: raise Exception(f"Regexes list not empty at the end of group parsing '{regexes}'")
    has_start = len(r1 + r21 + r221 + r222) > 0
    has_end = len(r41 + r42) > 0
    regex_r1 = f"{'|'.join(r1)}"
    DEBUG(regex_r1)
    regex_r21 = f"{'|'.join(r21)}"
    regex_r22 = f"Scarab {'(' if r221 and len(r221 + r222) > 1 else ''}{'|'.join(r221)}{'|' if bool(r221) + bool(r222) > 1 else ''}of {'(' if len(r222) > 1 else ''}{'|'.join(r222)}{')' if len(r222) > 1 else ''}{')' if r221 and len(r221 + r222) > 1 else ''}" if r221 or r222 else ""
    regex_r2  = f"{regex_r21}{'|' if regex_r21 and regex_r22 else ''}{regex_r22}"
    DEBUG(regex_r2)
    regex_r31 = f"{'|'.join(r31)}"
    regex_r32 = f"Scarab {'(' if r321 and len(r321 + r322) > 1 else ''}{'|'.join(r321)}{'|' if r321 and r322 else ''}of {'(' if len(r322) > 1 else ''}{'|'.join(r322)}{')' if len(r322) > 1 else ''}{')' if r321 and  len(r321 + r322) > 1 else ''}" if r321 or r322 else ""
    regex_r33 = f"{'(' if len(r33) > 1 else ''}{'|'.join(r33)}{')' if len(r33) > 1 else ''} Scarab" if r33 else ""
    regex_r34 = f"{'(' if len(r34) > 1 else ''}{'|'.join(r34)}{')' if len(r34) > 1 else ''} Scarab " if r34 else ""
    regex_r3  = f"{'(' if bool(regex_r31) + bool(regex_r32) + bool(regex_r33) + bool(regex_r34) > 1 else ''}{regex_r31}{'|' if regex_r31 and (regex_r32 or regex_r33 or regex_r34) else ''}{regex_r32}{'|' if (regex_r31 or regex_r32) and (regex_r33 or regex_r34) else ''}{regex_r33}{'|' if (regex_r31 or regex_r32 or regex_r33) and regex_r34 else ''}{regex_r34}{')' if bool(regex_r31) + bool(regex_r32) + bool(regex_r33) + bool(regex_r34) > 1 else ''}"
    regex_r3  = re.sub(r"\|+", r"|", regex_r3)
    DEBUG(regex_r3)
    regex_r41 = f"{'|'.join(r41)}"
    regex_r42 = f"{'(' if len(r42) > 1 else ''}{'|'.join(r42)}{')' if len(r42) > 1 else ''} Scarab" if r42 else ""
    regex_r4  = f"{regex_r41}{'|' if regex_r41 and regex_r42 else ''}{regex_r42}"
    DEBUG(regex_r4)
    regex = f"{regex_r1}|{regex_r2}|{'.*' if has_start and regex_r3 else ''}{regex_r3}{'.*' if has_start and regex_r3 else ''}|{'.*' if has_start and regex_r4 else ''}{regex_r4}".strip("|")
    DEBUG(regex)
    regex = f"\"{'!' if negate else ''}{'^' if has_start else ''}{'(' if has_start or has_end else ''}{regex}{')' if has_start or has_end else ''}{'$' if has_end else ''}\""
    return regex

#regex = gen_regex(all_regexes, negate)

print("\033[31;1mRegex to Paste:\033[0m")

last_regexes = []
for reg in all_regexes:
     test_reg = gen_regex(last_regexes + [reg], negate)
     re.compile(test_reg)
     if len(test_reg) > 250:
         regex = gen_regex(last_regexes, negate)
         re.compile(regex)
         print(f"\033[33;1m{regex}\033[0m")
         last_regexes = [reg]
     else:
         last_regexes.append(reg)

if last_regexes:
    regex = gen_regex(last_regexes, negate)
    re.compile(regex)
    print(f"\033[33;1m{regex}")

print("\033[31;1m----------------\033[0m")
#print(f"Regex character len: {len(regex)}.\033[0m")
