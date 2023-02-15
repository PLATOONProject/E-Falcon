# -*- coding: utf-8 -*-


import csv




datasources_classes=dict()


def read_datasource_classes(file):
    f = open(file, 'r',encoding="utf-8" )
    reader = csv.reader(f,delimiter=',')
    rows=list(reader)
    f.close()
    rows.pop(0)
    
    for row in rows:
        if row[0] not in datasources_classes:
            datasources_classes[row[0]]=[]
        datasources_classes[row[0]].append(row[1])





f = open("sourcedescriptiondatasource.csv", 'r',encoding="utf-8" )
reader = csv.reader(f,delimiter=',')
rows=list(reader)
f.close()
rows.pop(0)

platoon_datasets=rows


read_datasource_classes("datasources_classespilot1a.csv")
read_datasource_classes("datasources_classespilot2a.csv")
read_datasource_classes("datasources_classespilot2b.csv")
read_datasource_classes("datasources_classespilot3a.csv")
read_datasource_classes("datasources_classespilot3b.csv")
read_datasource_classes("datasources_classespilot3c.csv")
read_datasource_classes("datasources_classespilot4a.csv")



with open('platoon_datasources.csv', mode='w', newline='', encoding='utf-8') as results_file:
    writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["dataSource","dataSourceTitle","Classes"])
    for row in platoon_datasets:
        if row[0] in datasources_classes:
            writer.writerow([row[0],row[1],datasources_classes[row[0]]])
    






