from requests import get
from typing import List, Set
import pprint as pp
import re
import argparse

ap = argparse.ArgumentParser(description="Script to generate suitable regex strings to highlight vendorable scarabs.")
ap.add_argument("-t", "--treshold", type=float, action="store", default=1, help="Cuttoff value for scarab price. Any below this will be highlighted")
ap.add_argument("-l", "--limit", type=int, action="store", default=250, help="")
ap.add_argument("-d", "--debug", action="store_true", help="Enables debug session", default=False)
ap.add_argument("-dg", action="store", required=False, default=".")
ap.add_argument("-fk", "--force-keep", action="store", nargs="*", required=False, default=[], help="List of scarabs to force to be kept. Case sensitive, accepts regex.")
args = ap.parse_args()

# Print Debug info when DEBUG flag is active
DEBUGGER = args.debug

DEBUG = lambda x: pp.pprint(x) if DEBUGGER else None

def DEBUG_GREP(grepstr: str):
    if args.debug:
        pass

DEBUG("---------> Debug session active <----------")

# Constant values
treshold = args.treshold
LIMIT = int(args.limit)

# Dynamically get the name of the current league
league = get("https://poe.ninja/poe1/api/data/index-state").json()["economyLeagues"][0]["name"]

# Get the updated price of each scarab in chaos
db = get(f"https://poe.ninja/poe1/api/economy/exchange/current/overview?league={league}&type=Scarab").json()
DEBUG(db)
names = {item["id"]: item["name"] for item in db["items"]}
names = {id: f"^{name}$" for id, name in names.items()}
prices = {names[item["id"]]: item["primaryValue"] for item in db["lines"]}

# Find the scarabs that are too cheap to be worth selling
forced  = [name for name, value in prices.items() if any(re.search(p, name[1:-1]) is not None for p in args.force_keep)]
sell    = [name for name, value in prices.items() if value < treshold and name not in forced]
keep    = [name for name, value in prices.items() if name not in sell]

def get_all_regexes(includes: List[str], excludes: List[str]) -> dict:
    # Concatenate all the names of the scarabs to exclude so it is easier to check if a sub-string is present
    full_exclude = ",".join(excludes)
    # Save all the regexes that uniquely select the scarabs to keep
    regexes = {}
    # Get the shortest string in the name of each highlight scarab that is not present in the names of the scarabs to exclude
    for name in includes:
        for size in range(len("Scarab") + 2, len(name) + 1):
            for start in range(len(name) - size + 1):
                match = name[start:start+size]
                if "Scarab" in match and match not in full_exclude:
                    regexes.setdefault(name, []).append(match)
        if name not in regexes: raise Exception(f"No regex found for '{name}'")
    DEBUG(regexes)
    return regexes

def get_best_regexes(includes: List[str], excludes: List[str]) -> Set[str]:
    # Create dict with all possible regexes for each scarab
    regexes = get_all_regexes(includes=includes, excludes=excludes)
    # Check how many scarabs would be selected by each regex
    regex_count = {}
    for name, data in regexes.items():
        for regex in data:
            regex_count[regex] = regex_count.get(regex, 0) + 1
    # Assign a weight/score for each regex based on how many scarabs they select and how long they are
    regex_score = {regex: len(regex) - count - (5 if regex.startswith("^Scarab") or regex.startswith("Scarab") or regex.endswith("Scarab") or regex.endswith("Scarab$") else 0) for regex, count in regex_count.items()}
    # Find the best regex for all scarabs by finding the scarab with the worst best regex and setting that as the regex for that scarab
    # Then all the other scarabs that also have that regex will use that regex, repeat untill all scarabs have regexes
    to_assing = includes[:]
    regex_assigns = {}
    while to_assing:
        regex_tmp = {name: min(regexes[name], key=lambda x: regex_score[x]) for name in to_assing}
        _, worst_regex = max(regex_tmp.items(), key=lambda x: regex_score[x[1]])
        for name in to_assing[:]:
            if worst_regex in regexes[name]:
                regex_assigns[name] = worst_regex
                to_assing.remove(name)
    # Uniquefy the regexes to avoid repetition
    return set(regex_assigns.values())

# Validates if the regex created will highlight any scarabs that should be kept
def validate_regex(regex: str, scarabs_to_be_kept: List[str]) -> bool:
    # Clean regex str to use with python's re
    DEBUG(f"before: {regex}")
    regex = regex.replace('"', '')
    invert_return = regex[0] == '!'
    regex = regex[1:] if invert_return else regex
    DEBUG(f"after: {regex}")

    # Remove all ^ and $ from scarab names.
    keep_pre = [name.replace('^','').replace('$','') for name in scarabs_to_be_kept]
    DEBUG(keep_pre)
    # Filter list to see if there are any scarabs that should be kept that are being highlighted erroneously.
    keep = [name for name in keep_pre if re.search(regex, name)]
    DEBUG(keep)
    return len(keep) == len(keep_pre)

# Create the full regex string based on the individual regexes
# "!^(r1|(r21|Scarab (r221|of (r222))).*)|.*(r31|Scarab (r321|of (r322))|r33 Scarab|r34 Scarab ).*|.*(r41|(r42) Scarab)$"
def format_regex(items: Set[str], negate: bool) -> str:
    regexes = list(items)
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
    regex = f"{regex_r1}|{regex_r2}{'.*' if has_end and regex_r2 else ''}|{'.*' if has_start and regex_r3 else ''}{regex_r3}{'.*' if has_start and regex_r3 else ''}|{'.*' if has_start and regex_r4 else ''}{regex_r4}".strip("|")
    DEBUG(regex)
    regex = f"\"{'!' if negate else ''}{'^' if has_start else ''}{'(' if has_start or has_end else ''}{regex}{')' if has_start or has_end else ''}{'$' if has_end else ''}\""
    return regex


# Calculate the total regex lenght for highlighting the desired scarabs and highlighting the not of the undisired regexes
normal_regexes = get_best_regexes(sell, keep)
normal_regex = format_regex(normal_regexes, False)
inverted_regexes = get_best_regexes(keep, sell)
inverted_regex = format_regex(inverted_regexes, True)

# Select the regexes with the smallest total characters
regexes, negate = (normal_regexes, False) if len(normal_regex) <= len(inverted_regex) else (inverted_regexes, True)

# Print the regex in parts to abide by the POE regex character limit
print("\033[31;1mRegex to Paste:\033[0m")
last_regexes = []
for reg in regexes:
     test_reg = format_regex(set(last_regexes + [reg]), negate)
     re.compile(test_reg)
     if len(test_reg) > LIMIT:
         regex = format_regex(set(last_regexes), negate)
         re.compile(regex)
         print(f"\033[33;1m{regex}\033[0m")
         last_regexes = [reg]
     else:
         last_regexes.append(reg)
if last_regexes:
    regex = format_regex(set(last_regexes), negate)
    re.compile(regex)
    print(f"\033[33;1m{regex}\033[0m")
print("\033[31;1m---------------------\033[0m")

# Sanity check that shows which scarabs are forced to be kept. 
# Useful to debug regex matches
if forced:
    forced = [f[1:-1] for f in forced]
    print("\033[34;1mScarabs forced to be kept:")
    print("\033[32m-","\n-".join(forced), "\033[0m\n", sep="")

DEBUG(sorted(prices.items(),key = lambda x : x[1]))
# validate_regex(regex, keep)
