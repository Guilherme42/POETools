from pprint import pprint
from .MyLibs.POENinja import POENinja, Queries


# Get the price of lifeforce
db = POENinja.get_currency("Sanctum")
lifeforce = {name.split()[0]: value for name, value in db.items() if "Lifeforce" in name}


#-------------------------------------------------------------------------------------------------#


# Calculate the cost of converting a single essence into another
essence_cost = 30 * lifeforce["Primal"]

# Get the costs of each essence
db_essence = POENinja.get_essence("Sanctum")

# Group the essences by tier
essence_tiers = list(set([name.split()[0] for name in db_essence]))
db_essence = {tier: {name: value for name, value in db_essence.items() if name.startswith(tier)} for tier in essence_tiers}

# Get which essences in each tier are worth converting
worthy = {}
for tier, essences in db_essence.items():
    # Get which essences are worth converting in this tier
    convertable = []
    for name, value in essences.items():
        # Calculate the average value of the essences in this tier, excluding the one being considered
        # An essence can't be converted to itself
        others = [ovalue for oname, ovalue in essences.items() if name != oname]
        if not others: continue
        average_value = sum(others) / len(others)
        # If it is worthy, add it to the list of convertable essences
        if value < average_value - essence_cost:
            convertable.append([name, value, average_value - essence_cost - value])
    # Sort the convertable essences by margin
    if convertable:
        worthy[tier] = [item for item in sorted(convertable, key=lambda x: x[2], reverse=True)]

# Pad print the convertable essences
width = max([len(item[0]) for tier in worthy for item in worthy[tier]])
print("Essences:")
for tier, essences in worthy.items():
    print(f"\t{tier}")
    for name, value, margin in essences:
        print(f"\t\t{name:{width}} - Cost = {value:5.2f} | Margin = {margin:5.2f}")


#-------------------------------------------------------------------------------------------------#


# Calculate the cost of converting a single delirium orb into another
deli_cost = 30 * lifeforce["Primal"]

# Get the costs of each delirium orb
db_deli = POENinja.get_delirium_orbs("Sanctum")

# Get which delirium orbs are worth converting
convertable = []
for name, value in db_deli.items():
    # Calculate the average value of the delirium orbs, excluding the one being considered
    # A delirium orb can't be converted to itself
    others = [ovalue for oname, ovalue in db_deli.items() if name != oname]
    if not others: continue
    average_value = sum(others) / len(others)
    # If it is worthy, add it to the list of convertable delirium orbs
    if value < average_value - deli_cost:
        convertable.append([name, value, average_value - deli_cost - value])
# Sort the convertable delirium orbs by margin
convertable = [item for item in sorted(convertable, key=lambda x: x[2], reverse=True)]

# Pad print the convertable delirium orbs
width = max([len(item[0]) for item in convertable])
print("\n\nDelirium Orbs:")
for name, cost, margin in convertable:
    print(f"\t{name:{width}} - Cost = {value:5.2f} | Margin = {margin:5.2f}")