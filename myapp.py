from flask import Flask, request, render_template, url_for
from whoosh import index
from whoosh.qparser import QueryParser
import time

# flask --app myapp.py run

#search function using the prompt
def searchingIndex(search_prompt):
    #stop time for search-duration
    start_time = time.time()
    #open indexdir, read-only
    ix = index.open_dir("indexdir")

    resultList = []
    typoChecker = ""

    #search with whoosh over index
    with ix.searcher() as searcher:
        
        #create query with content of index entries using search_prompt
        query = QueryParser("content", ix.schema).parse(search_prompt)
        #save results
        results = searcher.search(query)

        #initialize whoosh-corrector for content
        corrected_prompt = ""
        corrector = searcher.corrector("content")

        #for every word in searchprompt, we use the first suggestion of the corrector
        for word in search_prompt.split():
            if corrector.suggest(word, limit=1):
                corrected_prompt += corrector.suggest(word, limit=1)[0] + " "
        
        #have to cut the last character (space) to make corrected_prompt comparable to search prompt
        corrected_prompt = corrected_prompt[:-1]

        #typoChecker gets set to a link with the "corrected" term
        if search_prompt != corrected_prompt and corrected_prompt:
            typoChecker = f"Did you mean: <a href='{url_for('search', searchinput=corrected_prompt)}' class='typo'>{corrected_prompt}</a>"

        #iterate over results filling the list with sublist which contain the search-result-information
        for r in results:
            #with highlights() we get already fitting highlights processed by whoosh, we just use them here
            resultList.append([r['link'], r['title'], "[...]" + r.highlights("content") + "[...]"])
    
    stop_time = time.time()
    return resultList, (stop_time-start_time), typoChecker

#create app using flask
app = Flask(__name__)

#starting page
@app.route("/")
def start():
    return render_template("start.html", title="AI and the Quokkas", headline="Quokka Search v. 1.0.1")

#search page
@app.route("/search")
def search():
    #get indexcontent, searchinfo
    indexContent, time, typo = searchingIndex(request.args.get('searchinput'))
    searchInf = f"There are {len(indexContent)} results for '{request.args.get('searchinput')}' in {round(time, 3)} seconds"
    #check if typochecker has any suggestions
    if typo:
        searchInf = searchInf + "<br />" + typo
    #load template for search using parameters
    return render_template("search.html", title="AI and the Quokkas", headline="Quokka Search v. 1.0.1", searchinfo=searchInf, resultList=indexContent)