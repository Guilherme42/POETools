from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import SessionNotCreatedException
from .webdriver import WebDriver


class MyChrome(Chrome):

    def __init__(self, url: str, headless: bool = False, *args, **kwargs) -> None:
        options = ChromeOptions()
        if headless: options.add_argument("--headless")
        super().__init__(chrome_options=options, *args, **kwargs)
        self.get(url)


try:
    MyChrome("https://www.google.com", headless=True)
except SessionNotCreatedException as e:
    if "This version of" in str(e):
        version = str(e).split("Current browser version is ")[1].split()[0]
        WebDriver.update(version)