from email import header
from urllib import response
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse
import time
from tinymongo import TinyMongoClient
from threading import Thread

class readm():
    # Get manga details
    def get_details(download_link):
        domain = urlparse(download_link).netloc

        response = requests.get(download_link)
        soup = BeautifulSoup(response.content, 'lxml')

        image_url = soup.find("img", attrs={"class": "series-profile-thumb"})['src']
        image_url = "https://" + domain + image_url

        chapters = soup.find("table", attrs={"class": "ui unstackable single line celled table"}).find("div", string="Chapters").parent.find_all("div")[1].text

        title = soup.find("h1", attrs={"class": "page-title"}).text
        details = {
            "domain": domain,
            "image_url": image_url,
            "title": title,
            "chapters": chapters
        }

        return details

    # Get the links to the chapters of the manga
    def getChapters(link):
        #Get soup of manga page
        src = requests.get(link)
        soup = BeautifulSoup(src.content, 'lxml')

        # Extract links to individual chapters
        chapters = []
        chapter_containers = soup.find_all("div", attrs={"class":"item season_start"})
        for chapter_container in chapter_containers:
            chapters.append("https://readm.org" + chapter_container.find("td", attrs={"class":"table-episodes-title"}).find("a")['href'])
        
        # Remove duplicates (website has some chapters listed twice) and reverse list
        chapters = list(dict.fromkeys(chapters))[::-1]

        return chapters
    
    # Get the title of the chapter and list of images
    def getChapterDetails(chapter):
        src = requests.get(chapter)
        soup = BeautifulSoup(src.content, 'lxml')

        title = soup.find("span", attrs={"class":"light-title"}).text

        image_container = soup.find("div", attrs={"class":"ch-images ch-image-container"}).find("center")
        image_links = image_container.find_all("img")
        image_links = ["https://readm.org/"+x['src'] for x in image_links]

        chapter_details = {"image_links":image_links, "title":title}
        return chapter_details
    
    # Function to download an image to folder
    def downloadImage(image, title, output, i):
        image = requests.get(image)
        if image.status_code == 200:
            os.makedirs(f'{output}/{title}', exist_ok = True)
            open(f"{output}/{title}/{i+1}.jpg", 'wb').write(image.content)
    
    #Download manga
    def download(download_link, manga_title, download_id):
        #Connect to the database to update progress
        connection = TinyMongoClient("database")
        db = connection.database

        #make output folder path
        output= "downloads/" + manga_title

        #Get all the chapters from the webpage
        chapters = readm.getChapters(download_link)

        downloaded = 0
        for chapter in chapters:
            #Get the chapter details (chapter title and list of image links)
            chapter_details = readm.getChapterDetails(chapter)
            title, image_links = chapter_details['title'], chapter_details['image_links']

            #remove bad characters from title (folder name)
            bad_characters = ['<', '>',':','"','/','\\','|','?','*']
            for character in bad_characters: 
                title = title.replace(character, "")

            #Download the images of each chapter to its own folder
            threads = []
            for i, image in enumerate(image_links):
                thread = Thread(target = readm.downloadImage, args = (image, title, output, i,))
                threads.append(thread)
            
            for thread in threads:
                thread.start()
            
            for thread in threads:
                thread.join()

            # Update progress
            downloaded = downloaded + 1
            progress = int(downloaded / len(chapters) * 100)
            db.downloads.update({"_id":download_id},{"progress":progress})
            if progress == 100:
                db.downloads.update({"_id":download_id},{"status":"Complete"})

            time.sleep(1)


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
    
    # Get the links to the chapters of the manga
    def getChapters(link):
        # Get soup of manga page
        src = requests.get(link)
        soup = BeautifulSoup(src.content, 'lxml')

        # Extract links to individual chapters
        chapter_containers = soup.find("div", attrs={"class":"chapter-list"}).find_all("div")
        chapters = [x.find("span").find("a")['href'] for x in chapter_containers]

        # Reverse list of chapters to download in order
        chapters.reverse()

        return chapters
    
    # Get the title of the chapter and list of images
    def getChapterDetails(chapter):
        src = requests.get(chapter)
        soup = BeautifulSoup(src.content, 'lxml')

        title = soup.find_all("span", attrs={"itemprop":"name"})[-1].text

        image_container = soup.find("div", attrs={"class":"container-chapter-reader"})
        image_links = image_container.find_all("img")
        image_links = [x['src'] for x in image_links]

        chapter_details = {"image_links":image_links, "title":title}

        return chapter_details

    # Function to download an image to folder
    def downloadImage(image, title, output, i):
        headers = {"referer": "https://mangakakalot.com/"}
        image = requests.get(image, headers=headers)
        if image.status_code == 200:
            os.makedirs(f'{output}/{title}', exist_ok = True)
            open(f"{output}/{title}/{i+1}.jpg", 'wb').write(image.content)

    #Download manga
    def download(download_link, manga_title, download_id):
        #Connect to the database to update progress
        connection = TinyMongoClient("database")
        db = connection.database

        #make output folder path
        output= "downloads/" + manga_title

        #Get all the chapters from the webpage
        chapters = mangakakalot.getChapters(download_link)

        downloaded = 0
        for chapter in chapters:
            #Get the chapter details (chapter title and list of image links)
            chapter_details = mangakakalot.getChapterDetails(chapter)
            title, image_links = chapter_details['title'], chapter_details['image_links']

            #remove bad characters from title (folder name)
            bad_characters = ['<', '>',':','"','/','\\','|','?','*']
            for character in bad_characters: 
                title = title.replace(character, "")

            #Download the images of each chapter to its own folder
            threads = []
            for i, image in enumerate(image_links):
                thread = Thread(target = mangakakalot.downloadImage, args = (image, title, output, i,))
                threads.append(thread)
            
            for thread in threads:
                thread.start()
            
            for thread in threads:
                thread.join()

            # Update progress
            downloaded = downloaded + 1
            progress = int(downloaded / len(chapters) * 100)
            db.downloads.update({"_id":download_id},{"progress":progress})
            if progress == 100:
                db.downloads.update({"_id":download_id},{"status":"Complete"})

            time.sleep(1)