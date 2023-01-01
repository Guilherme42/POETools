from .query import Query, Queries


class POENinja:

    @staticmethod
    def simplify(db: dict) -> dict:
        if "lines" in db and "name" in db["lines"][0]:
            return {line["name"]: line["chaosValue"] for line in db["lines"]}
        if "lines" in db and "currencyTypeName" in db["lines"][0]:
            return {line["currencyTypeName"]: line["chaosEquivalent"] for line in db["lines"]}
        raise ValueError(f"Unrecognized DB {db}")

    @classmethod
    def query(cls, qtype: Queries, league: str) -> dict:
        return cls.simplify(Query.query(qtype, league))

    @classmethod
    def get_currency(cls, league: str) -> dict:
        return cls.query(Queries.Currency, league)

    @classmethod
    def get_essence(cls, league: str) -> dict:
        return cls.query(Queries.Essence, league)

    @classmethod
    def get_beasts(cls, league: str) -> dict:
        return cls.query(Queries.Beasts, league)

    @classmethod
    def get_delirium_orbs(cls, league: str) -> dict:
        return cls.query(Queries.DeliriumOrb, league)



if __name__ == "__main__":
    print(POENinja.get_beasts("Sanctum"))