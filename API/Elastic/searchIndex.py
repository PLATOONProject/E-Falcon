
from elasticsearch import Elasticsearch



es = Elasticsearch(['http://node3.research.tib.eu:9200'])




def search_elastic(term,k=1):
    indexName = "platoonentities2"
    results=[]
    exact_match=[]
    ###################################################
    elasticResults=es.search(index=indexName, body={
            "query": {
                        "fuzzy": {
                          "label": {
                            "value": term.title(),
                            "fuzziness": "AUTO"
                          }
                        }
                      },"size":15
            }
           )
    for result in elasticResults['hits']['hits']:
            results.append([result["_source"]["label"],result["_source"]["uri"],result["_score"]])


    
    if len(results)==0:
        indexName = "platoonentities"
        results=[]
        exact_match=[]
        ###################################################
        elasticResults=es.search(index=indexName, body={
                  "query": {
                    "bool": {
                      "must": [
                        {
                          "match": {
                            "label": {
                                    "query": term.title(),
                                     "minimum_should_match": "50%"
                                  }
                          }
                        },
                        {
                          "match": {
                            "lang": "en"
                          }
                        }
                      ]
                    }
                  },"size":15
                }
               )
        for result in elasticResults['hits']['hits']:
                results.append([result["_source"]["label"],result["_source"]["uri"],result["_score"]])
            
        
        
        
    results= sorted(results, key = lambda x: (-x[2]))
        
    return results[:k]


