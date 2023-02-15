# -*- coding: utf-8 -*-
import requests
import csv
from tqdm import tqdm
from collections import Counter
import ast

headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

def falcon_call_efalcon(text):
    url = 'https://labs.tib.eu/sdm/efalcon/api?mode=long'
    entities_wiki=[]
    payload = '{"text":"'+text+'"}'
    r = requests.post(url, data=payload.encode('utf-8'), headers=headers)
    if r.status_code == 200:
        response=r.json()
        for result in response['entities']:
            entities_wiki.append(result[1])
    else:
        r = requests.post(url, data=payload.encode('utf-8'), headers=headers)
        if r.status_code == 200:
            response=r.json()
            for result in response['entities']:
                entities_wiki.append(result[1])
            
    return entities_wiki





f = open("../datasets/sourcedescriptiondatasources.csv", 'r',encoding="utf-8" )
reader = csv.reader(f,delimiter=',')
rows=list(reader)
f.close()
header=rows.pop(0)

header.append("E-Falcon")
#header.append("P")

results=[]
for row in tqdm(rows):
    falcon_response=falcon_call_efalcon(row[1])
    #gold_standard=ast.literal_eval(row[2])
    #intersection = list((Counter(gold_standard) & Counter(falcon_response)).elements())
    #if len(falcon_response)==0:
    #        p=0
    #else:
    #    p=len(intersection)/len(falcon_response)
        
    result=row
    result.append(falcon_response)
    #result.append(p)
    results.append(result)
    
    
    
with open('../results/platoon_datasources_all_efalcon.csv', mode='w', newline='', encoding='utf-8') as results_file:
    writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    writer.writerows(results)    
    