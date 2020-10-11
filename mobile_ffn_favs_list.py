import scrapy
import bs4
from bs4 import BeautifulSoup
import html5lib
import re
from MobileFFNScraper.items import MobileffnscraperItem


class MobileFFNScraper(scrapy.Spider):
    name = 'ffnfavs'

    start_urls = ["https://m.fanfiction.net/u/2429213/ForSaleBabyShoesNeverWorn?a=fs"]
    

    def parse(self, response):
        item =  MobileffnscraperItem()
        self.log('I just visited '+response.url)
        author_page= "https://m.fanfiction.net/u/2429213/ForSaleBabyShoesNeverWorn"
        contents=response.css('#content').get()
        soup=bs4.BeautifulSoup(contents,'html5lib')
        ffs=soup.select('.brb')      
       
        for ff in ffs:
            name= ff.select("a")[1].get_text()
            info=ff.select("div")[0].get_text().split(', ')
            fandom=info[0]
            rating=info[1]
            language=info[2]
            genres=info[3]
            if info[4].startswith('chapters'):
                chapters=int(info[4][9:].strip())
            else:
                chapters=1
            term1=re.compile(r'words*')
            term2=re.compile(r'favs*')
            term3=re.compile(r'follows*')
            words=list(filter(term1.match, info))[0][6:].strip()
            favs=list(filter(term2.match, info))[0][5:].strip()
            try:
                follows=list(filter(term3.match, info))[0][8:].strip()
            except IndexError:
                follows=''
            except:
                follows='ERROR'
            try:
                if chapters > 1 and len(follows)>=1:
                    characters= info[9:]
                elif chapters == 1 and len(follows) == 0 :
                    characters= info[7:]
                else:
                    characters= info[8:]
            except IndexError:
                 characters=''
            reviews=ff.select("a")[0].get_text()
            if ff.select('img.pull-right.mm'):
                status = 'Complete'
            else:
                status = 'On-going'
            if status == 'Complete' and chapters>1:
                 summary = ff.contents[8]
            elif status == 'Complete' and chapters == 1:
                summary = ff.contents[6]
            elif status == 'On-going' and chapters > 1:
                summary = ff.contents[6]
            else:
                summary = ff.contents[4]
            update_date = ff.select('span')[0].get_text()
            try:
                publish_date=ff.select('span')[1].get_text()
            except IndexError:
                publish_date=''
            item = {
                'name': name,
                'fandom':fandom,
                'rating':rating,
                'chapters':chapters,
                'language':language,
                'genres':genres,
                'words':words,
                'favs':favs,
                'follows':follows,
                'characters':characters,
                'reviews':reviews,
                'status': status,
                'summary': summary,
                'update_date': update_date,
                'publish_date': publish_date,
                'info': info
            }
            yield item
        next_page_url=soup.find("a", text=re.compile('Next')).get('href')
        if next_page_url:
            next_page_url=author_page+next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse)
            

