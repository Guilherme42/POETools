from cloudscraper import CloudScraper, create_scraper
import json as Json
from enum import Enum, unique


@unique
class Queries(Enum):

    Currency          = "https://poe.ninja/api/data/currencyoverview?league={}&type=Currency"
    Fragment          = "https://poe.ninja/api/data/currencyoverview?league={}&type=Fragment"
    Oils              = "https://poe.ninja/api/data/itemoverview?league={}&type=Oil"
    Incubators        = "https://poe.ninja/api/data/itemoverview?league={}&type=Incubator"
    Scarabs           = "https://poe.ninja/api/data/itemoverview?league={}&type=Scarab"
    Fossils           = "https://poe.ninja/api/data/itemoverview?league={}&type=Fossil"
    Resonators        = "https://poe.ninja/api/data/itemoverview?league={}&type=Resonator"
    Essence           = "https://poe.ninja/api/data/itemoverview?league={}&type=Essence"
    DivinationCards   = "https://poe.ninja/api/data/itemoverview?league={}&type=DivinationCard"
    Prophecies        = "https://poe.ninja/api/data/itemoverview?league={}&type=Prophecy"
    SkillGems         = "https://poe.ninja/api/data/itemoverview?league={}&type=SkillGem"
    BaseTypes         = "https://poe.ninja/api/data/itemoverview?league={}&type=BaseType"
    HelmetEnchants    = "https://poe.ninja/api/data/itemoverview?league={}&type=HelmetEnchant"
    UniqueMaps        = "https://poe.ninja/api/data/itemoverview?league={}&type=UniqueMap"
    Maps              = "https://poe.ninja/api/data/itemoverview?league={}&type=Map"
    UniqueJewels      = "https://poe.ninja/api/data/itemoverview?league={}&type=UniqueJewel"
    UniqueFlasks      = "https://poe.ninja/api/data/itemoverview?league={}&type=UniqueFlask"
    UniqueWeapons     = "https://poe.ninja/api/data/itemoverview?league={}&type=UniqueWeapon"
    UniqueArmors      = "https://poe.ninja/api/data/itemoverview?league={}&type=UniqueArmour"
    UniqueAccessories = "https://poe.ninja/api/data/itemoverview?league={}&type=UniqueAccessory"
    Beasts            = "https://poe.ninja/api/data/itemoverview?league={}&type=Beast"
    DeliriumOrb       = "https://poe.ninja/api/data/itemoverview?league={}&type=DeliriumOrb"


class Query:

    scraper: CloudScraper = create_scraper()

    @classmethod
    def query(cls, qtype: Queries, league: str) -> dict:
        return Json.loads(cls.scraper.get(qtype.value.format(league)).text)


if __name__ == "__main__":
    print(Query.query(Queries.Beasts, "Sanctum"))