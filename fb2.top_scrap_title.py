from bs4 import BeautifulSoup
from urllib.request import urlopen
from requests_html import HTMLSession
from urllib.parse import urljoin
from datetime import datetime
import time
from re import sub
import requests


#now = datetime.now()
#formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

#f = open("george_orwell_1984.txt", "a")
# initialize an HTTP session
session = HTMLSession()

#avidreaders.ru
#url = "http://fb2.top/the-black-widow-454774/read/part-4"

url = "https://fb2.top/the-black-widow-454774"
url2 = "https://fb2.top"
#url = "http://loveread.ec/read_book.php?id=20121&p=1"
#url = "http://loveread.ec/read_book.php?id=21556=&p=1"
#url = "http://loveread.ec/read_book.php?id=56884&p=1"
#id = url.split("=")[-2][:-2]

#getting title of the book and opening file
soup0 = BeautifulSoup(urlopen(url), 'lxml')
#print(soup0.prettify())
#title = soup0.title.get_text().rsplit('|', 1)[0]
title = soup0.title.get_text().rsplit('-', 1)[0]
title1 = soup0.title.get_text().rsplit('-', 1)[1]
print(title1)
print("TITLE >> ",title)
filetitle = title.replace(" ", "_")
#filetitle = (title.replace(" ", "_").replace("_|_", "_"))[:-1]

print("for opening file: ",filetitle)
#f = open('{0}.txt'.format(filetitle), "w+")
#f.write(title)

#section = soup0.find('section')
#print(section.text)


#working with pagination
#res = session.get(url)
#soup = BeautifulSoup(res.html.html, "html.parser")
#pag = soup0.find('div', {'class' : 'navigation'})
#pag = soup0.find('div', {'class' : 'pagination'})

mainpg = soup0.find('div', {'class' : 'card-body'})
#pags = soup0.find_all('li', {'class' : 'mg-1 mt-1'})  # class="mt-1 mg-2" page
pags = mainpg.find_all('a')                                # 'ul', {'class': 'pl-2'})
#pags = soup0.find('ul', {'class': 'pl-2'})             #   div        modal-body
chapters = []
for a in pags:
#    f.write(a.text + "\n")
    link = a.attrs["href"].split("#")
#    link = a.attrs["href"]
    link = link[0]
    print(link)
#    a.attrs["href"] = urljoin(url2, a.attrs["href"])
    a.attrs["href"] = urljoin(url2, link)
# [res.append(x) for x in test_list if x not in res] or res = [*set(l)]
    chapters.append(a['href'])        # 
   
#remove duplicates in chapters
rlink = []
#rlink = [*set(chapters)]     #breaking list order
rlink=list(dict.fromkeys(chapters))
print("no duplicates ",len(rlink))
print(len(chapters))   # actual book started at /read/part-6#6  <section>
#print(chapters[0])
#print(chapters[1])
#print(chapters[2])  # Dedication /read/part-3#3 Epigraph /read/part-4 Foreword /read/part-5
#print(rlink[1])
#print(rlink[5])
#print(rlink[-1])
#print(chapters[-1])

x = range(len(rlink))
for pg in x:
#    soup = BeautifulSoup(urlopen(rlink[pg]), 'lxml')
#    page = soup.find('section')
    print(rlink[pg])
#    print(page.getText())
#    f.write(page.getText() + "\n")

#soup = BeautifulSoup(urlopen(chapters[1]), 'lxml')  # chapters links starting from fulllinks[1]
#pages = soup.find_all('li', {'class' : 'mg-2 mt-1'}) # 'mg-1 mt-1' -part I  and  
#pages = soup.find_all('li')
#print(pages.getText())



#for a in pags :  
#    link = a.attrs["href"]
#    print(link)
#print("another way get pages: ", pgs[-2].text)

"""

#soup0 = BeautifulSoup(urlopen(url), 'lxml')
#print(soup0.title.get_text())
#title = soup0.title.get_text().rsplit('|', 1)[0]

for a in soup.find_all('div', {'class' : 'navigation'}):
    try:
        a.attrs["href"] = urljoin(url, a.attrs["href"])
        if len(a.attrs["href"]) > 80 :
            print(a.attrs["href"])
            resglobal.append(a.attrs["href"])
            print(len(resglobal))
    except:
        pass

    
"""

pag = soup0.find('div', {'class' : 'navigation'})
#print(pag)
#pgs = pag.findAll('a')
#print("another way get pages: ", pgs[-2].text)
#print(pgs[-2].text)
#for a in pag.find_all('a') :
#    print(a.get(['href']))
#    if a.has_key('href'):
#        if a.has_attr('href'):
#            print(a['href'])
#        else :
#            print("current")
#    print(a.text)


#f.write(title)

#f.close()
