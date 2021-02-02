# MangaParser
Scripts for scraping manga via https://manganelo.com, https://mangakakalot.com, https://mangasee123.com

## Requirements
You need to have python 3 installed to run this script. Also, requests and requests-html modules are needed for the script to run, install it with pip install requests and pip install requests-html

You can also install the required packages with requirement.txt file, just use pip install -r requirements.txt

## Supported Websites
* https://manganelo.com ,
* https://mangakakalot.com ,
* https://mangasee123.com 
	
## Usage
use _MangaseeParser, _ManganeloParser or _MangaseeParser class to get a manga
each class have an coroutine get(<nameManga>, [chap]) and return an _Item or _Chapter if [chap] is given

## class _Item
* async _Item.getChapters([chap]) ---> _Chapter[] : list of chapter
* async _Item.getLatest() ---> _Chapter : the latest chapter
* async _Item.getInfo() : retrieve the informations about the manga

## class _Chapter

* async _Chapter.getImages() --> str[] : list of url for the images

