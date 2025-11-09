from re import match
from time import sleep
from pyautogui import click
from pyperclip import paste
from typing import Optional, List, Tuple


class Found(Exception): pass


min_quantity: Optional[int] = 85
min_rarity: Optional[int] = None
min_pack: Optional[int] = None


mods: List[Tuple[List[str], int]] = [
    # Minus maximum res makes death much more likelly
    ([r"Players have -[0-9]+% to all maximum Resistances"], 0),
    # No regen will make my death to DOT almost garanteed
    ([r"Players cannot Regenerate Life, Mana or Energy Shield"], 0),
    ([r"Players have [0-9]+% less Recovery Rate of Life and Energy Shield"], 0),
    # Critical chance makes attacks that bypass stun more likely
    ([r"Monsters have [0-9]+% increased Critical Strike Chance "], 0),
    # Makes the monsters much more damaging
    ([r"Monsters gain [0-9]+% of their Physical Damage as Extra Chaos Damage"], 0),
    ([r"Monsters deal [0-9]+% extra Physical Damage as Cold", r"Monsters deal [0-9]+% extra Physical Damage as Fire", r"Monsters deal [0-9]+% extra Physical Damage as Lightning", r"[0-9]+% increased Monster Damage", r"Unique Boss deals [0-9]+% increased Damage"], 2),
    ([r"Area has patches of Shocked Ground which increase Damage taken by [0-9]+%"], 0),
    # This bricks the build as it is dependent on igniting
    ([r"Monsters have [0-9]+% chance to Avoid Elemental Ailments"], 0),
    # Makes flasks last a lot less
    ([r"Buffs on Players expire [0-9]+% faster"], 0),
    ([r"Players cannot gain Flask Charges"], 0),
    ([r"Players gain [0-9]+% reduced Flask Charges"], 0),
    # Temporal chains makes doing the map much slower
    ([r"Players are Cursed with Temporal Chains"], 0),
    # Not good against DOT
    # ([r"Monsters Poison on Hit"], 0),
    # Reduced aura effect makes death much more likelly
    # ([r"Players have [0-9]+% reduced effect of Non-Curse Auras from Skills"], 0),
    # Consecrated ground makes monsters regen a lot, might make them unkillable
    # ([r"Area has patches of Consecrated Ground"], 0),
    # Burning ground deals a lot of damage
    # ([r"Area has patches of Burning Ground"], 0),
    # ([r"[0-9]+% increased Monster Damage"], 0),
    # Not overcap in res
    # ([r"Players are Cursed with Elemental Weakness"], 0),
    # Makes the enemies much more tanky
    # ([r"Monsters gain [0-9]+% of Maximum Life as Extra Maximum Energy Shield"], 0),
    # ([r"[0-9]+% more Monster Life"], 0),
    # ([r"\+[0-9]+% Monster Elemental Resistances"], 0),
]


previous = text = ""
while True:
    # Wait for a clipboard update
    while text == previous:
        text = paste().split("\n")
        sleep(0.1)
    previous = text
    # Check if it is a POE map
    if "Item Class: Maps" not in text[0]: continue
    # Check if the quantity is above the minimum
    quantity = next((x for x in text if "Item Quantity" in x), None)
    quantity = int(quantity.split(" ")[2].strip("+%")) if quantity is not None else None
    if (quantity is not None and min_quantity is not None and quantity < min_quantity) or (quantity is None and min_quantity is not None):
        print(f"Not enough quantity {quantity}/{min_quantity}")
        continue
    # Check if the rarity is above the minimum
    rarity = next((x for x in text if "Item Rarity" in x), None)
    rarity = int(rarity.split(" ")[2].strip("+%")) if rarity is not None else None
    if (rarity is not None and min_rarity is not None and rarity < min_rarity) or (rarity is None and min_rarity is not None):
        print(f"Not enough rarity {rarity}/{min_rarity}")
        continue
    # Check if the pack size is above the minimum
    pack = next((x for x in text if "Monster Pack Size" in x), None)
    pack = int(pack.split(" ")[3].strip("+%")) if pack is not None else None
    if (pack is not None and min_pack is not None and pack < min_pack) or (pack is None and min_pack is not None):
        print(f"Not enough pack size {pack}/{min_pack}")
        continue
    # Check if the map mods are unacceptable
    section = False
    bad = False
    for line in text:
        if "---" in line: section += 1
        elif section == 4:
            for rule in mods:
                count = sum([int(match(mod, line) is not None) for mod in rule[0]])
                if count > rule[1]:
                    bad = True
                    print(f"Discarded due to {rule[0]}")
    # Move the map over
    if not bad: click()
