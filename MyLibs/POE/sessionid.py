from os.path import exists, join, dirname
from ..MyChrome import MyChrome


class SESSIONID:

    _sessionid: str = ""

    @classmethod
    def sessionid(cls) -> str:
        if not cls._sessionid: cls.get_sessionid()
        return cls._sessionid

    @classmethod
    def get_sessionid(cls) -> str:
        sessionid = cls.read_sessionid()
        while not cls.test_sessionid(sessionid):
            sessionid = cls.login()
        cls._sessionid = sessionid

    @classmethod
    def read_sessionid(cls) -> str:
        path = join(dirname(__file__), "sessionid")
        if exists(path):
            with open(path) as sessionid_file:
                return sessionid_file.read().strip(" \n")
        return ""

    @staticmethod
    def test_sessionid(sessionid: str) -> bool:
        # TODO: Try doing an API call to validate the SESSION ID
        return bool(sessionid)

    @staticmethod
    def login() -> str:
        # TODO: Open a chrome window to login into the POE site and get a SESSION ID
        driver = MyChrome(url="https://www.pathofexile.com", headless=False)
        from time import sleep
        sleep(100)


if __name__ == "__main__":

    print(SESSIONID.sessionid())