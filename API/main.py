import csv
import spacy
import time
from src import stopwords 
from multiprocessing.pool import ThreadPool
from Elastic import searchIndex

nlp = spacy.load('en_core_web_sm')


stopWordsList=stopwords.getStopWords()
comparsion_words=stopwords.getComparisonWords()
evaluation = False


def get_verbs(question):
    verbs=[]
    entities=[]
    text = nlp(question)
    entities=[x.text for x in text.ents]
    for token in text:
        if (token.pos_=="VERB") and not token.is_stop:
            isEntity=False
            for ent in entities: 
                ent=ent.replace("?","")
                ent=ent.replace(".","")
                ent=ent.replace("!","")
                ent=ent.replace("\\","")
                ent=ent.replace("#","")
                ent = ent.replace("-", " ")
                if token.text in ent:
                    ent_list=ent.split(' ')
                    next_token=text[token.i+1]
                    if ent_list.index(token.text)!= len(ent_list)-1 and next_token.dep_ =="compound":
                        isEntity=True
                        break
            if not isEntity:
                verbs.append(token.text)
    return verbs

def split_base_on_verb(combinations,combinations_relations,question):
    newCombinations=[]
    verbs=get_verbs(question)
    flag=False
    for comb in combinations:
        flag=False
        for word in comb.split(' '):
            if word in verbs:
                flag=True
                combinations_relations.append(word.strip())
                #newCombinations.append(word.strip())
                for term in comb.split(word):
                    if term!="":
                        newCombinations.append(term.strip())
        if not flag:
            newCombinations.append(comb)
        
        
    return newCombinations,combinations_relations


                
            
def get_question_combinatios(question,questionStopWords):
    combinations=[]
    tempCombination=""
    if len(questionStopWords)==0:
        combinations = question.split(' ')
    else:
        for word in question.split(' '):
            if word in questionStopWords:
                if tempCombination != "":
                    combinations.append(tempCombination.strip())
                    tempCombination=""
            else:
                tempCombination=tempCombination+word+" "
        if tempCombination != "":
              combinations.append(tempCombination.strip())  
    return combinations

def check_only_stopwords_exist(question,comb1,comb2,questionStopWords):
    check=question[question.find(comb1)+len(comb1):question.rfind(comb2)]
    doc = nlp(question)
    verbs=[]
    for token in doc:
        if token.tag_ == "VBD" or token.tag_=="VBZ":
            verbs.append(token.text)
    if check==" ":
        return True
    flag=True
    count=1
    for word in check.strip().split(' '):
        if count == 3:
            flag=False
            break
        if word not in questionStopWords:
            flag=False
            break
        if word in questionStopWords and word in verbs:
            flag=False
            break
        if word=="is":
            flag=False
            break
        if word =="and" and (len(comb1.split(' ')) > 1 or  len(comb2.split(' ')) > 1):
            flag=False
            break
        count=count+1
            
    return flag
    
    

    
def merge_comb_stop_words(combinations,combinations_relations,question,questionStopWords):
    final_combinations=[]   
    only_stopwords_exist=True
    i=0
    if len(combinations)==0:
        return final_combinations,combinations_relations
    temp=combinations[i]
    while only_stopwords_exist and i+1<len(combinations):

        if check_only_stopwords_exist(question,temp,combinations[i+1],questionStopWords):
            temp=temp+question[question.find(temp)+len(temp):question.rfind(combinations[i+1])+len(combinations[i+1])]
            i=i+1
        else:
            if temp=="":
                final_combinations.append(combinations[i])
                i=i+1
                if (i<len(combinations)):
                    temp = combinations[i]
                else:
                    break
            else:
                final_combinations.append(temp)
                i=i+1
                if (i<len(combinations)):
                    temp = combinations[i]
                else:
                    break
                    
    if temp!="":
        final_combinations.append(temp)

    return final_combinations,combinations_relations





 
def split_base_on_s(combinations):
    result=[]
    for comb in combinations:
        if "'s" in comb:
            result.extend(comb.split("'s"))
        elif "'" in comb:
            result.extend(comb.split("'"))
        else:
            result.append(comb)
    return result





def process_text_E_R(question,rules,k=1,text=''):
    if not any(x==14 for x in rules):
        rules.append(14)
    entities=[]
    #relations=[]
    sentences=question.split('. ')
    for sentence in sentences:
        if sentence.strip()=="":
            continue
        raw=evaluate([sentence],rules,False,k,text)
        row_results=[]
        for row in raw:
            if len(row[1])>0:
                row_results.append([row[0],row[1][0][1]])
            
        entities.extend(row_results)
        #relations.extend(raw[1])
      

    
    #entities=list(set(entities))
    #relations=list(set(relations))
    return entities



def process_word_E(term,k=1,text=''):
    entities=[]
    raw=evaluate_short([term],k)
    if raw==[]:
        return []
    entities.extend(raw[0])
    return entities



def process_word_E_T(term,k=1,text='',all_types=False,s_type='stype',predicted_type=''):
    entities=[]
    
    raw=evaluate_short([term],predicted_type,False,k,s_type)
    if raw==[]:
        return []
    entities.extend(raw[0])
    #entities=list(set(entities))
    #relations=list(set(relations))
    return entities  

def extract_abbreviation(combinations):
    new_comb=[]
    for com in combinations:
        abb_found=False
        for word in com.strip().split(' '):
            if word.isupper():
                abb_found=True
                new_comb.append(word)
                remain=com.replace(word,"").strip()
                if remain !="":
                    new_comb.append(remain)
        if not abb_found:
            new_comb.append(com)
    return new_comb
                
def split_bas_on_comparison(combinations):
    compare_found=False
    new_comb=[]
    for com in combinations:     
        comp_found=False
        for word in com.split(' '):
            if word in comparsion_words:
                compare_found=True
                comp_found=True
                comp_word=word
        if comp_found:
            com=com.replace("than","").strip()
            new_comb.extend(com.split(comp_word))
        else:
            new_comb.append(com)
    return new_comb,compare_found
            

def check_entities_in_text(text,term):
    doc = nlp(text)
    if len(doc.ents)>0:       
        for ent in doc.ents:
            if ent.text==term or ent.text in term:
                return True

    
def extract_stop_words_question(text):
    stopwords=[]
    doc = nlp(text)
    for token in doc:
        if token.is_stop and token.text!="name":
            stopwords.append((token.text))

    return stopwords

def token_index(doc,token_):
    i=0
    for token in doc:
        if token_ ==token.text:
            return i
        i=i+1
    return -1

def upper_all_entities(combinations,text):
    doc = nlp(text)
    relations=[]
    entities = [x.text for x in doc.ents]
    final_combinations=[]
    for token in doc:
        if  (not token.is_stop) and ( (token.dep_=="compound" and token.pos_!="PROPN") or token.pos_=="VERB" or token.dep_ == "ROOT"):
            isEntity=False
            for ent in entities: 
                ent=ent.replace("?","")
                ent=ent.replace(".","")
                ent=ent.replace("!","")
                ent=ent.replace("\\","")
                ent=ent.replace("#","")
                if token.text in ent:
                    ent_list=ent.split(' ')
                    next_token=doc[token.i+1]
                    if ent_list.index(token.text)!= len(ent_list)-1 and next_token.dep_ =="compound":
                        isEntity=True
                        break
            if not isEntity:
                relations.append(token.text)
    for comb in combinations:
        if len(relations)==0:
            if comb.capitalize() not in final_combinations:
                final_combinations.append(comb.capitalize())
        for relation in relations:
            if relation in comb:
                if comb.lower() not in [x.lower() for x in final_combinations]:
                    final_combinations.append(comb.lower())
                    break 
        if comb.lower() not in [x.lower() for x in final_combinations]:
            final_combinations.append(comb.capitalize())
    return final_combinations



                
                
                
def merge_comb_det(combinations,text):
    doc = nlp(text)
    final_combinations=[]
    for comb in combinations:
        if comb.istitle():
            comb_index=token_index(doc,comb)
            if comb_index==-1:
                comb_index=token_index(doc,comb.lower())
            if doc[comb_index-1].tag_=="DT":
                final_combinations.append(doc[comb_index-1].text.capitalize()+" "+comb)
            else:
                final_combinations.append(comb)
        else:
            final_combinations.append(comb)
    return final_combinations
        



def evaluate_short(raw,e_type='all',evaluation=True,k=1,s_type='sgroup'):
    try:

     
        entities=[]
        
        #combinations_relations=[]
       
    
        question=raw[0]
       
        
        #questionStopWords=extract_stop_words_question(question)
        
        term=question

        entityResults=searchIndex.search_elastic(term,k)    

        if entityResults==-1 or entityResults=="":
            entities.extend(greedy_search_short(term, k, 1))
        else:
            entities.append(tuple((term,entityResults)))
                    
                
        
        return entities
    except:
        raise
        print("error")

def evaluate(raw,rules,evaluation=True,k=1,text=''):
    try:
        #global rules
        #evaluation=True
     
        startTime=time.time()
        oneQuestion=False
        global correctRelations
        #correctRelations=0
        global wrongRelations
        #wrongRelations=0
        global correctEntities
        #correctEntities=0
        global wrongEntities
        #wrongEntities=0
        #global count
        #print(count)
        p_entity=0
        r_entity=0
        p_relation=0
        r_relation=0
        #k=1
        correct=True
        questionRelationsNumber=0
        entities=[]
  
        
      
        #beforeMixRelations=[]
        question=raw[0]
        if question.strip()[-1]!="?":
            question=question+"?"
        #print(question)
        originalQuestion=question
        question=question[0].lower() + question[1:]
        question=question.replace("?","")
        question=question.replace(".","")
        question=question.replace("!","")
        question=question.replace("\\"," ")
        question=question.replace("#","")
        question=question.replace("/"," ")                                  

        questionStopWords = []
        combinations = question.split(' ')
  
        combinations_relations=[]




        if any(x==1 for x in rules):
            questionStopWords=extract_stop_words_question(question)#rule1: Stopwords cannot be entities or relations
  
        if any(x==2 for x in rules):
            combinations=get_question_combinatios(question,questionStopWords) #rule 2: If two or more words do not have any stopword in between, consider them as a single compound word

        
        if any(x==4 for x in rules):
            combinations,combinations_relations=split_base_on_verb(combinations,combinations_relations,originalQuestion)  #rule 4: Verbs cannot be an entity, Verbs act as a division point of the sentence in case of two entities and we do not merge tokens from either side of the verb.
            combinations=split_base_on_s(combinations)  
            
        if any(x==3 for x in rules):        
            combinations,combinations_relations=merge_comb_stop_words(combinations,combinations_relations,question,questionStopWords) #rule 3: Entities with only stopwords between them are one entity
         
                  

        

        
        
            
        if any(x==8 for x in rules):
            combinations,compare_found=split_bas_on_comparison(combinations) #rule 8: Comparison words acts as a point of division in case of two tokens/entities
    
        #if any(x==9 for x in rules):
            #combinations=extract_abbreviation(combinations) #rule 9: Abbreviations are separate entities
        

        
        #combinations=upper_all_entities(combinations,originalQuestion)

        if any(x==12 for x in rules):
            combinations=merge_comb_det(combinations,originalQuestion) #rule 12: Merge the determiner in the combination, if preceding an entity
            
        #Rules applied during/after elastic search
        
        
        #combinations.extend(combinations_relations)
       
     
        for term in combinations:

            if len(term)==0:
                continue
    
            if check_entities_in_text(originalQuestion,term):
                term=term.capitalize()
                
            
            entityResults=searchIndex.search_elastic(term,k)    
  
            if entityResults==-1 or entityResults=="":
                entities.extend(greedy_search(term,questionStopWords,text,k))
            else:
                entities.append(tuple((term,entityResults)))
                
                

                
                
        
        return entities
    except:
        raise
        print("error")


def greedy_search_short(term,k,n):
    entities=[]
    if n>5:
        return entities
    term_splitted=term.split(' ')
    if len(term_splitted) == 1:
        return entities
    else:
        sub_terms=[]
        if len(term_splitted) >2:
            sub_terms.append(' '.join(term_splitted[:-1]))
            sub_terms.append(' '.join(term_splitted[1:]))
        else:
            sub_terms.append(' '.join(term_splitted[:-1]))
            sub_terms.append(term_splitted[-1])
        ##################
        '''
        if e_type!='all' and e_type!=['all'] and e_type[0]!='T':
            try:
                e_type=UMLSCall.getSemanticType(e_type)
            except:
                e_type=UMLSCall.getSemanticType(e_type)
        '''
        ########################
        for sub_term in sub_terms:
            entity_sub_Results=searchIndex.search_elastic(sub_term, k)
            if entity_sub_Results!=-1 and entity_sub_Results!="":
                entities.append(tuple((sub_term.strip(),entity_sub_Results)))
            else:
                    entities.extend(greedy_search_short(sub_term,k,n+1))
    '''if entities==[]:
        if e_type!=-1:
            entity_sub_Results=UMLSCall.getCui(tail_term,[e_type],k,s_type)
        else:
            entity_sub_Results=UMLSCall.getCui(tail_term,'all',k,'sgroup')
        if entity_sub_Results != -1 and entity_sub_Results != "":
            entities.append(tuple((tail_term.strip(), entity_sub_Results)))'''
    return entities

def greedy_search(term,questionStopWords,text,k):
    entities=[]
    term_splitted=split_stopword(term,questionStopWords)
    if term_splitted==term:
        term_splitted=term.split(' ')
        if len(term_splitted) == 1:
            return entities
        if len(term_splitted) > 2:
            tail=term_splitted[-1]
            term_splitted=[' '.join(term_splitted[:-1])]
            term_splitted.append(tail)

    for sub_term in term_splitted:
        if len(sub_term.strip())==1 or sub_term in questionStopWords:
            continue
        entity_sub_Results=searchIndex.search_elastic(sub_term.strip(),k)
        if entity_sub_Results!=-1 and entity_sub_Results!="":
            entities.append(tuple((sub_term.strip(),entity_sub_Results)))
        else:
            entities.extend(greedy_search(sub_term,questionStopWords,text,k))
    return entities

def split_stopword(term,questionStopWords):
    for stopword in questionStopWords:
        if ' '+stopword+' ' in term:
            return term.split(' '+stopword+' ')
    return term

def datasets_evaluate():
    global threading
    threading=True
    
    k=1
    kMax=10
    p_entity=0
    p_relation=0
    global correctRelations
    correctRelations=0
    global wrongRelations
    wrongRelations=0
    global correctEntities
    correctEntities=0
    global wrongEntities
    wrongEntities=0
    startQ=0
    endQ=5000
    errors=0
    global count
    count=1
    
    global results
    results=[]
    p_e=0
    p_r=0

    #questions=read_dataset('datasets/simplequestions.txt')
    
    
    #filepath = 'datasets/'+dataset_file
    questions=wiki_evaluation.read_simplequestions_entities_upper()
    ##global rules
    #rules = [1,2,3,4,5,8,9,10,12,13,14]
    
    if threading:
        pool = ThreadPool(12)
        pool.map(evaluate, questions)
        pool.close()
        pool.join()
    else:
        for question in questions[:]:
            try:
                single_result=evaluate(question)
                print(count)
                count=count+1
                #print( "#####" + str((correctRelations * 100) / (correctRelations + wrongRelations)))
                print("#####" + str((correctEntities * 100) / (correctEntities + wrongEntities)))
                results.append(single_result)
            
            except:
                errors+=1
                print("error"+str(errors))
                continue
     
        
    with open('datasets/results/finaaaaal/FALCON_simple_upper_tets.csv', mode='w', newline='', encoding='utf-8') as results_file:
        writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(results)    
    #print("Correct Relations:",correctRelations)
    #print("Relations:")
    #print((correctRelations*100)/(correctRelations+wrongRelations))
    print("Correct Entities:",correctEntities)
    print("Entities:")
    print((correctEntities*100)/(correctEntities+wrongEntities))
    print(correctEntities+wrongEntities)
    ''''print("p_entity:")
    print(p_entity)
    print("p_relation:")
    print(p_relation)'''
    
    #x=[i for i in range (len(questions))]
    #y=[question[4] for question in questions]

if __name__ == '__main__':
    #datasets_evaluate()
    global count
    count=0
    global threading
    threading=False
    rules = [1,2,4,5,8,9,10,12,13,14]
  


