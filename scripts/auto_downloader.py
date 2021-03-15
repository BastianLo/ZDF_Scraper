#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import youtube_dl
import re
import os

class results:
    def __init__(self, title, date, link, belongs_to = None):
        self.title = title
        self.date = date
        self.link = link
        self.belongs_to = belongs_to

def search(search_string):
    search_string = str(search_string).replace(" ","+")
    url = "https://www.zdf.de/suche?q="+search_string+"&synth=true&sender=Gesamtes+Angebot&from=&to=&attrs=&abName=ab-2021-02-22&abGroup=gruppe-a"

    page = requests.get(url)
    if page.status_code == 200:
        content = page.content
    soup = BeautifulSoup(content, "html.parser")
    temp = soup.find(id="aria-search-block")
    result_boxes = temp.findChildren(recursive=False)

    search_results = []
    for box in result_boxes:
        children = box.findChildren()
        belongs_to = None
        for child in children:
            if child.name == "a":
                title = child.text.replace("-","").replace("\n","").strip()
            if child.has_attr('class') and child['class'][0] == 'teaser-cat-brand-ellipsis':
                belongs_to = child.text.strip()
            if child.has_attr('class') and child['class'][0] == 'special-info':
                date = child.text.strip()
            if child.has_attr('class') and child['class'][0] == 'teaser-title-link':
                link = "https://www.zdf.de/"+child['href']
        search_results.append(results(title,date,link,belongs_to))
    return search_results

def download(link, req_block):
    page = requests.get(link)
    if page.status_code == 200:
        content = page.content
    soup = BeautifulSoup(content, "html.parser")

    full_block = soup.find("div", {"class": "sb-page"})
    temp = full_block.findChildren(recursive=False)
    blocks = []

    for item in temp:
        if item.has_attr('class') and (item['class'][0] == 'b-content-teaser-list' or item['class'][0] == 'b-cluster'):
            blocks.append([item,""])

    for block in blocks:
        header = block[0].findChild("header", recursive=False)
        block[1] = header.text.strip()

    indexes = []
    for item in blocks:
        print("lel "+item[1].strip(),req_block.strip())
        if(item[1].strip() == req_block.strip()):
            index = blocks.index(item)
            print(index)
            indexes.append(index)


    for index in indexes:
        html = blocks[index][0]
        name = blocks[index][1]
        print("Searching in:",name)
        children = html.findChildren()
        for child in children:
            if child.has_attr('class') and 'teaser-title-link' in child['class']:
                link = "https://www.zdf.de"+child["href"]

                name_no_special = re.sub('\W',' ',name)
                ydl_opts = {'outtmpl': "downloads/"+link.split('/')[-1]+"/"+name_no_special+"/"+child.text.strip()+".mp4"}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])

if __name__ == '__main__':
    if os.path.isfile('series.txt'): 
        file = open('series.txt', 'r')
        lines = file.readlines()
        for line in lines:
            items = line.split(";")
            req_series = items[0]
            req_block = items[1]
            download(req_series, req_block)


