#https://www.pathofexile.com/trade/search/Sanctum?q={%22query%22:{%22status%22:{%22option%22:%22online%22},%22type%22:%22Winged%20Divination%20Scarab%22,%22stats%22:[{%22type%22:%22and%22,%22filters%22:[],%22disabled%22:false}]},%22sort%22:{%22price%22:%22asc%22}}

from cloudscraper import CloudScraper, create_scraper
import json as Json
from pprint import pprint

class POE:

    scraper: CloudScraper = create_scraper()

    session_id: str = "782afa2da0e005690a986bf77a50acbe"

    league: str = "Sanctum"

    exchange_url: str = "https://www.pathofexile.com/api/trade/exchange/{}"

    @classmethod
    def search(cls, json: Json) -> Json:
        db = cls.scraper.post(cls.exchange_url.format(cls.league), json=json).json()["result"]
        return [[db[item]["listing"]["offers"][0]["exchange"]["amount"] / db[item]["listing"]["offers"][0]["item"]["amount"], db[item]["listing"]["offers"][0]["item"]["stock"]] for item in db]


if __name__ == "__main__":
    json = {
        "query": {
            "status": {
                "option": "online"
            },
            "have": [
                "divine"
            ],
            "minimum": 1,
            "want": [
                "fragmented-delirium-orb"
            ]
        },
        "sort": {
            "have": "asc"
        },
        "engine": "new"
    }
    db = POE.search(json)
    print(db)