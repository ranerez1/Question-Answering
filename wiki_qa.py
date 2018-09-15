import requests
import re
import rdflib
from lxml import html
import codecs
import wikipedia
import sys

relation_dict ={}
question_entity =""
question_relation =""
question_wiki_page =""
g = rdflib.Graph()

# who is the <relation> of [the] <entity>
# what is the <relation> of [the] <entity>
# when was <entity> born

def extractEntities(question):

    global question_entity
    global question_relation
    global question_wiki_page

    entities = []
    relations = []
    if(inputValidator(question) == 0):
        return

    tmp = question.split(' ')
    words=[]
    for i in tmp:
        words.append(i.lower())

    leng = len(words)

    if((words[0] == "who") or (words[0] == "what")):
        start_rel = 3
        stop_rel = 0
        for w in words:
            if(w == "of"):
                break
            stop_rel+=1
        while(start_rel< stop_rel):
            relations.append(words[start_rel])
            start_rel+=1
        stop_rel+=1
        if(words[stop_rel] == "the"):
            stop_rel+=1
        while (stop_rel<leng):
            entities.append(words[stop_rel])
            stop_rel+=1

    elif(words[0] == "when"):
        #when action
        start_rel = 2
        stop_rel = 0
        for w in words:
            if(w=="born"):
                break
            stop_rel+=1
        while(start_rel< stop_rel):
            entities.append(words[start_rel])
            start_rel+=1
        relations.append("born")

    else:
        print("Invalid Question Format \n")
    entity = '_'.join(entities)
    relation ='_'.join(relations)
    url = getWikiPage(entity)
    question_entity = entity
    question_relation = relation
    question_wiki_page = url


def getWikiPage(term):
    pg = wikipedia.page(term)
    return pg.url

def inputValidator(question):
    question_words = ['who','when','what']
    for q in question_words:
        if q in question:
            return 1
    return 0


#The function scrapes wikipedia's infobox for the input link
# The function deals with single and multiple field values
# Stores key:value pairs in dictionary [TODO] Remove the dictionary

def getInfoBox(link,entity):
    global relation_dict
    r = requests.get(link,'utf-8')
    doc = html.fromstring(r.content)
    rows= doc.xpath("//*[@id='mw-content-text']/div/table[1]/tr[position()>2]")
    counter =0
    for row in rows:
        table_headers = rows[counter].xpath("th//text()")
        if(len(table_headers)!=0):
            values = rows[counter].xpath("td/text() | td//a[not(contains(@href,'#cite'))]/text() | td/span/text()")
            #for value in values:
             #   print(value)
              #  value = value.replace(' ','_')
               # print(value)

            multi_values = rows[counter].xpath("td/div/ul//text()")
            #print(table_headers)
            new_list =[]
            for i in table_headers:
                t = i.replace(' ','_')
                new_list.append(t)
            relation = '_'.join(new_list)

            relation = data_cleaner(relation)
            relation = relation.lstrip(' ').rstrip(' ')
            relation = relation.lstrip('_').rstrip('_')

            if(len(multi_values)>0): # Dealing with multiple values in the field (like Gal Gadot's Occupation)
                clean_list =[]
                for item in multi_values:
                    item = data_cleaner(item)

                    if(len(item)>1):
                        relation =relation.rstrip('s')
                        clean_list.append(item)
                        relation_dict.update({relation : clean_list})
                        write_ontology(question_entity,relation,item)
            else:
                field_val = '_'.join(values)
                field_val = data_cleaner(field_val)
                field_val = field_val.lstrip(' ').rstrip(' ')
                field_val = field_val.lstrip('_').rstrip('_')
                if(len(field_val)>0):
                    relation_dict.update({relation:field_val})
                    write_ontology(question_entity,relation,field_val)

        counter+=1



def write_ontology(entity, relation, value):
    el = rdflib.URIRef("http://example.org/"+entity)
    re = rdflib.URIRef("http://example.org/"+relation.lower())
    value = value.replace(' ', '_')
    va = rdflib.URIRef("http://example.org/"+value)
    g.add((el, re, va))
    g.serialize(destination="ontology.nt", format ="nt")


def returnAnswer(question):
    q = "SELECT ?answer WHERE { <http://example.org/" + question_entity + "> <http://example.org/" + question_relation + "> ?answer .}"
    new_file = codecs.open("query.sparql","w+","utf-8")
    new_file.write(q)
    x = g.query(q)
    results =[]
    for item in x:
        d = str(item.asdict()['answer'].toPython())
        d= d.replace('_',' ')
        d = d.replace("http://example.org/",'')
        results.append(d)
        print(d)

def data_cleaner(str):
    str = re.sub('[\[\]]', '', str)
    str = re.sub('<[^<]+?>', ' ', str)
    str = re.sub('(?i)\{\{cite .*\}\}', '', str)
    str = re.sub('&nbsp;', '', str)
    str = re.sub('\( \)', '', str)
    str = re.sub('\n', '', str)
    str = re.sub("[\(\[].*?[\)\]]", "", str)
    str =re.sub("\u00A0",'_',str)
    str = re.sub("_\u2022_",'',str)
    return str

# Program needs to run with a string argument containing the question

if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Invalid Question")
    question = sys.argv[1]
    extractEntities(question)
    getInfoBox(question_wiki_page,question_entity)
    returnAnswer(question)