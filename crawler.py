import requests
from bs4 import BeautifulSoup
from whoosh.index import create_in
from whoosh.fields import *

#Crawl (=get and parse) all HTML pages on a certain server
#that can directly or indirectly be reached from a start URL
#by following links on the pages.
#Do not follow links to URLs on other servers and only process HTML responses.
#Test the crawler with a simple website, e.g., https://vm009.rz.uos.de/crawl/index.html 

#set start_page to our example page
start_page = 'https://vm009.rz.uos.de/crawl/index.html'

#create base link (cut off last part, for example index.html so it can later be replaced with page1.html, etc.)
base_link = start_page[:start_page.rindex('/')+1]

#empty dictionary visited_links and link_stack initialized with start page
visited_links = {}
link_stack = [start_page]

#as long as the link_stack is not empty, a link of the stack gets popped and checked for more links, content, etc.
while link_stack:
    current_link = link_stack.pop()

    r = requests.get(current_link, timeout=3)
    if  199 < r.status_code < 299:
        #parse content with bs4
        soup = BeautifulSoup(r.content, 'html.parser')
        #add link and content to dictionary
        visited_links[current_link] = {
            'title': soup.title.string if soup.title else "",
            'content': soup.get_text() #maybe optimize this to just use main-content
        }

        #iterate over all links on current site (current_link)
        for l in soup.find_all("a"):
            next_link = l['href']
            #simplified check whether link is complete
            if "http" not in next_link:
                next_link = base_link + next_link
            #check whether link is on same domain server (as base_link) (NOT OPTIMAL)
            if (base_link in next_link) and (next_link not in visited_links and next_link not in link_stack):
                link_stack.append(next_link)


#create schema for indexlist with title, content and link
schema = Schema(title=TEXT(stored=True), content=TEXT(stored=True), link=ID(stored=True))

#create an index in the directory indexdir
ix = create_in("indexdir", schema)
writer = ix.writer()

for key in visited_links:
    #do we have to use the 'u' in front of the strings here too?
    writer.add_document(title=visited_links[key]['title'], content=visited_links[key]['content'], link=key)

#commit changes
writer.commit()

#visualization of dictionary visited_links [CAN BE REMOVED LATER]
for link in visited_links:
    print(visited_links[link]['title'], ":", link)