from requests_html import AsyncHTMLSession, HTML
import re

session = AsyncHTMLSession()

#---------------------- CHAPTER CLASS --------------------------
CHAP_IMG_QUERY = ".img-fluid"

class _Chapter:

    def __init__(self, number, date, url, title=None):
            self.number = number
            self.date = date
            self.url = url
            self.title = title
            
    async def getImages(self):
            self.images = []
            resp = await session.get(self.url)
            await resp.html.arender(keep_page=True,sleep=.1)
            page = resp.html.page
            try:
                btn = await page.querySelector('.fa-arrows-alt-v')
                await btn.click()
            except:
                pass
            content = await page.content()
            to_parse = HTML(html=content)
            imgs = to_parse.find(CHAP_IMG_QUERY)
            for img in imgs:
                self.images.append(img.attrs['src'])
                
            return self.images


    def __str__(self):
        return str({"title":self.title,"number":self.number, "date":self.date, "url":self.url})


#-------------------- Item(manga/manhwa ...)-----------
CHAPS_QUERY = "a.list-group-item"
CHAP_DATE_QUERY = "span.float-right"
INFO_QUERY = ".list-group-flush"
#DESCRIPTION_QUERY = ".panel-story-info-description"
POSTER_QUERY = ".img-fluid"

class _Item:
    def __init__(self, url):
            self.url = url
            self.chapters = []
            
    async def getChapters(self, epis=None):
            if not epis:
                    self.chapters = []
                    r = await session.get(self.url)
                    await r.html.arender(keep_page=True,sleep=.1)
                    page = r.html.page
                    try:
                        btn = await page.querySelector('.fa-chevron-down')
                        await btn.click()
                    except:
                        pass
                    content = await page.content()
                    to_parse = HTML(html=content)
                    chapter_group = to_parse.find(CHAPS_QUERY)
                    for chapter in chapter_group:
                            other = self._parse(chapter)
                            self.chapters.append(_Chapter(*other))

                    return self.chapters
            else:
                    url = f"{self.url}-chapter-{epis}.html"
                    url = re.sub("(manga)/", "read-online/", url)
                    chap = _Chapter(number=epis, url=url, date=None)
                    return chap
                
    async def getLatest(self):
            r = await session.get(self.url)
            await r.html.arender(sleep=.1)
            chapter = r.html.find(CHAPS_QUERY, first=True)
            other = self._parse(chapter)
            return _Chapter(*other)

    def _parse(self, chapter):
            chap_num = float(chapter.find('span',first=True).text.split()[1])
            chap_num = int(chap_num) if chap_num.is_integer() else chap_num
            chap_url = chapter.absolute_links.pop().replace("-page-1","")
            chap_url = chap_url.replace('example.org', 'mangasee123.com')
            chap_date = chapter.find(CHAP_DATE_QUERY, first=True).text
            return chap_num, chap_date, chap_url

    async def getInfo(self):
            r = await session.get(self.url)
            info = r.html.find(INFO_QUERY, first=True)
            self.name = info.find("li:first-child", first=True).text
            self.description = info.find("li:last-child", first=True).text.split(':')[-1]
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
SEARCH_MATCH_QUERY = ".SeriesName"
SEARCH_PATH = "/search/?name="

class _MangaseeParser:
    BASE_URL = "https://mangasee123.com"
    def __init__(self, baseUrl=None):
            self.baseUrl = baseUrl if baseUrl else self.BASE_URL

    async def get(self, name, chap=None):
            name = name.strip().replace(" ", "-")
            url = self.baseUrl+SEARCH_PATH+name
            r = await session.get(url)
            await r.html.arender(sleep=.2)
            match = r.html.find(SEARCH_MATCH_QUERY, first=True)
            if not match:
                    return None
            match_url = match.find('a', first=True).attrs['href']
            item = _Item(self.baseUrl+match_url)
            if not chap:
                    return item
            else:
                    return await item.getChapters(chap)
