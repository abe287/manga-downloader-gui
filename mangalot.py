from urllib import response
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse
import time
from tinymongo import TinyMongoClient
from threading import Thread

class mangakakalot():
    # Get manga details
    def get_details(download_link):
        domain = urlparse(download_link).netloc

        response = requests.get(download_link)
        soup = BeautifulSoup(response.content, 'lxml') 

        image_url = soup.find("div", attrs={"class":"manga-info-pic"}).find("img")['src']

        chapters = len(soup.find("div", attrs={"class":"chapter-list"}).find_all("div"))

        title = soup.find("h1").text

        details = {
            "domain": domain,
            "image_url": image_url,
            "title": title,
            "chapters": chapters
        }

        return details


details = mangakakalot.get_details(download_link = "https://mangakakalot.com/manga/ho920718")
print(details)