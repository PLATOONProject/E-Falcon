# -*- coding: utf-8 -*-

from tqdm import tqdm
import json

files = ['.\\data\\PLATOON_classes_labels - owl_Class.csv',
'.\\data\\PLATOON_classes_labels - owl_class(skos_altLabel).csv',
'.\\data\\PLATOON_classes_labels - owl_class(rdfs_altLabel).csv',
'.\\data\\PLATOON_classes_labels - owl_ObjectProperty.csv',
'.\\data\\PLATOON_classes_labels - owl_DatatypeProperty.csv',
'.\\data\\PLATOON_classes_labels - owl_FunctionalProperty.csv',
'.\\data\\PLATOON_classes_labels - voaf_Vocabulary.csv',
'.\\data\\PLATOON_classes_labels - owl_Ontology .csv',
]
entities_index_main=[]

for file_path in files:
    with open (file_path ,encoding="utf-8") as f:
        disambiguation_pages=f.readlines()


    disambiguation_pages_dict=dict()
    for row in disambiguation_pages:
        disambiguation_pages_dict[row.replace('\n','')]=''

    with open (file_path ,encoding="utf-8") as f:
        lines=f.readlines()

    seen=dict()

    for line in tqdm(lines):
        line=line.split(',')
        if line[0]!="class":
            label=','.join(line[2:-1]).strip()

            uri=line[0]
            label=line[1]
        
            if label.__contains__("@"):
                lang=label.split('@')[1].replace('\n','').replace('\"','')
            else:
                lang=""    

            label=label.split('@')[0].replace('"','')  
            
            type = file_path.split('-')[1].replace('.csv','').replace(' ','')
        
            if uri+lang not in seen:
                    seen[uri+lang]=label
            else:
                if seen[uri+lang]==label:
                    continue
            entities_index_main.append({"_index":"platoonentities","_source":{"uri":uri[0:],"label":label ,"lang":lang, "type":type }})               
                
with open ('.\\output\\wikientitymainlabel.json', 'w', encoding="utf-8") as f:
    for row in entities_index_main:
        f.write(json.dumps(row))
        f.write('\n')