from requests_html import AsyncHTMLSession
import re

session = AsyncHTMLSession()

#---------------------- CHAPTER CLASS --------------------------
CHAP_IMG_QUERY = ".container-chapter-reader img"
class _Chapter:

    def __init__(self, number, date, url, title=None):
            self.number = number
            self.date = date
            self.url = url
            self.title = title
            
    async def getImages(self):
            self.images = []
            resp = await session.get(self.url)
            imgs = resp.html.find(CHAP_IMG_QUERY)
            for img in imgs:
                self.images.append(img.attrs['src'])
            
            return self.images


    def __str__(self):
        return str({"title":self.title,"number":self.number, "date":self.date, "url":self.url})


#-------------------- Item(manga/manhwa ...)-----------
CHAPS_QUERY = ".row-content-chapter li"
CHAP_DATE_QUERY = "span.chapter-time"
INFO_QUERY = ".story-info-right"
DESCRIPTION_QUERY = ".panel-story-info-description"
POSTER_QUERY = ".info-image img"

class _Item:
    def __init__(self, url):
            self.url = url
            self.chapters = []
            
    async def getChapters(self, epis=None):
            if not epis:
                    self.chapters = []
                    r = await session.get(self.url)
                    chapter_group = r.html.find(CHAPS_QUERY)
                    for chapter in chapter_group:
                            other = self._parse(chapter)
                            self.chapters.append(_Chapter(*other))

                    return self.chapters
            else:
                    url = re.sub("(manga)/", "chapter/", self.url)
                    url = f"{url}/chapter_{epis}"
                    chap = _Chapter(number=epis, url=url, date=None)
                    return chap
                
    async def getLatest(self):
            r = await session.get(self.url)
            chapter = r.html.find(CHAPS_QUERY, first=True)
            other = self._parse(chapter)
            return _Chapter(*other)

    def _parse(self, chapter):
            link = chapter.find('a', first=True)
            chap_num = float(re.search(r"chapter ([0-9]+\.*[0-9]*)", link.text,re.IGNORECASE).group(1))
            chap_num = int(chap_num) if chap_num.is_integer() else chap_num
            chap_url = link.attrs['href']
            chap_title = link.attrs['title'].split(':')[-1].strip()
            chap_date = chapter.find(CHAP_DATE_QUERY, first=True).text
            return chap_num, chap_date, chap_url, chap_title

    async def getInfo(self):
            r = await session.get(self.url)
            info = r.html.find(INFO_QUERY, first=True)
            self.name = info.find('h1', first=True).text
            vals = []
            for val in info.find('tr'):
                text = val.text.split(':')[-1].strip()
                vals.append(text)
            (self.alternative, self.author, self.status, self.genres) = vals
            self.genres = list(map(str.strip, self.genres.split('-')))
            self.description = r.html.find(DESCRIPTION_QUERY, first=True).text.split(":")[-1]
            self.poster = r.html.find(POSTER_QUERY, first=True).attrs['src']
            
    def __len__(self):
            return len(self.chapters)

    def __iter__(self):
            for chap in self.chapters:
                    yield chap

    def repr(self):
        return f"<Item url:{self.url}>"

    def str(self):
        return self.repr()
                    
#----------------------- Main Parser ----------------------------------------_
SEARCH_MATCH_QUERY = ".search-story-item"

class _ManganeloParser:
    BASE_URL = "https://manganelo.com"
    def __init__(self, baseUrl=None):
            self.baseUrl = baseUrl if baseUrl else self.BASE_URL

    async def get(self, name, chap=None):
            name = name.strip().replace(" ", "_")
            url = self.baseUrl+'/search/story/'+name
            r = await session.get(url)
            match = r.html.find(SEARCH_MATCH_QUERY, first=True)
            if not match:
                    return None
            match_url = match.find('a', first=True).attrs['href']
            item = _Item(match_url)
            if not chap:
                    return item
            else:
                    return await item.getChapters(chap)
