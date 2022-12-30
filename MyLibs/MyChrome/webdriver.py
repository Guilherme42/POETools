import requests
from xml.etree import ElementTree as ET
from wget import download
from zipfile import ZipFile
from os import remove
from os.path import dirname
from enum import Enum, unique
from platform import system
from typing import List


class OS(Enum):

    Windows = "chromedriver_win32.zip"
    Linux = "chromedriver_linux64.zip"
    Mac = "chromedriver_mac64.zip"


class WebDriver:

    @staticmethod
    def get_os_appropriate_file_name() -> str:
        if system() == "Windows":
            return OS.Windows.value
        if system() == "Linux":
            return OS.Linux.value
        if system() == "Darwin":
            return OS.Mac.value
        raise ValueError(f"Unrecognized system '{system()}'")

    @classmethod
    def get_best_version(cls, versions: List[str], my_version: str) -> str:
        best = versions[0]
        int_best = [int(a) for a in best.split(".")]
        for version in versions:
            int_version = [int(a) for a in version.split(".")]
            for a, b in zip(int_version, int_best):
                if a == b:
                    continue
                if a > b:
                    best = version
                    int_best = int_version
                else:
                    break
        return best

    @classmethod
    def update(cls, my_version: str) -> None:
        print("Current chrome version", my_version)

        # get the chrome driver versions
        url = "https://chromedriver.storage.googleapis.com"
        root = ET.fromstring(requests.get(url).text)

        # Get all versions
        versions = []
        for element in root.iter():
            if element.tag.endswith("Contents"):
                for attribute in element.iter():
                    if attribute.tag.endswith("Key"):
                        if "chromedriver" in attribute.text:
                            versions.append(attribute.text)

        # Filter versions by OS
        os_file = cls.get_os_appropriate_file_name()
        versions = [version.split("/")[0] for version in versions if os_file in version]

        # Filter out the versions higher than the one I have
        versions = [version for version in versions if not any([int(a) > int(b) for a, b in zip(version.split("."), my_version.split("."))])]

        # Get the ideal version based on the Chrome version I have installed
        version = cls.get_best_version(versions, my_version)

        # build the donwload url
        download_url = f"https://chromedriver.storage.googleapis.com/{version}/{os_file}"

        # download the zip file using the url built above
        latest_driver_zip = download(download_url, "chromedriver.zip")

        # extract the zip file
        with ZipFile(latest_driver_zip, "r") as zip_ref:
            zip_ref.extractall(dirname(__file__))

        # delete the zip file downloaded above
        remove(latest_driver_zip)