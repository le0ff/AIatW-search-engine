#THIS IS A TEST-FILE FOR TESTING THE SEARCH FUNCTION WITH THE INDEX
#later this can be implemented to the myapp.py, I suppose
from whoosh import index
from whoosh.qparser import QueryParser

#read only
ix = index.open_dir("indexdir")
search_prompt = "platypus"

with ix.searcher() as searcher:
    query = QueryParser("content", ix.schema).parse(search_prompt)
    results = searcher.search(query)
    
    # print all results
    for r in results:
        print(r['title'], ":", r['link'])