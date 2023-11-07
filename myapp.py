from flask import Flask, request, render_template
from whoosh import index
from whoosh.qparser import QueryParser
import random # :)

# flask --app myapp.py run

#search function using the prompt
def searchingIndex(search_prompt):
    #open indexdir, read-only
    ix = index.open_dir("indexdir")

    resultList = []
    
    #search with whoosh over index
    with ix.searcher() as searcher:
        #create query with content of index entries using search_prompt
        query = QueryParser("content", ix.schema).parse(search_prompt)
        #save results
        results = searcher.search(query)

        #iterate over results filling the list with sublist which contain the search-result-information
        for r in results:
            resultList.append([r['link'], r['title'], r['main_content']])
    return resultList

#create app using flask
app = Flask(__name__)

#starting page
@app.route("/")
def start():
    return render_template("start.html", title="AIatW Project1", headline="Search Engine v. 0.1.1")

#search page
@app.route("/search")
def search():
    #get indexcontent, searchinfo
    indexContent = searchingIndex(request.args.get('searchinput'))
    searchInf = f"There are {len(indexContent)} results for '{request.args.get('searchinput')}' in {round(random.random(), 3)} seconds"
    #load template for search using parameters
    return render_template("search.html", title="AIatW Project1", headline="Search Engine v. 0.1.1", searchinfo=searchInf, resultList=indexContent)
    