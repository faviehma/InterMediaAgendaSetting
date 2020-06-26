import json
import nltk
from nltk.corpus import stopwords
import string
from nltk.stem.snowball import SnowballStemmer
import os
from collections import Counter
from datetime import datetime


#This implements a preprocessing pipeline

def preprocessData():
    data = []
    resultdata = []
    punctuation = string.punctuation
    stop_words = stopwords.words('german')
    snowball = SnowballStemmer("german")


    os.chdir("C:\\Users\\fabia\\Documents\\GitHub\\Scraping\\ProcessedData\\final\\Data")
    publisherfilepaths = [x for x in os.listdir() if "preprocessed_" not in x and "combined" not in x and ".json" in x] #all raw data files


    for x in publisherfilepaths:

        with open(x, "r", encoding="utf-8") as file:
            data.append((json.load(file),x))
            file.close()

    uniquetokens =[]


    for headlinedict in data:
        resultdict={}
        start = datetime.strptime("2020-02-01/00:00","%Y-%m-%d/%H:%M")
        end = datetime.strptime("2020-04-01/00:00","%Y-%m-%d/%H:%M")
        print(headlinedict[1])

        for item in headlinedict[0]:
            date =datetime.strptime(item,"%Y-%m-%d /%H")
            if start<date<end:
                resultdict[item]={}
                for rank in headlinedict[0][item]:
                    if int(rank) >20:
                        continue

                    current = headlinedict[0][item][rank]
                    words = (current["title"].lower().replace("-"," ")+" "+current["text"].lower()).replace("-"," ") #cut words with hypens as those are quite common in German news
                    words = [word for word in nltk.word_tokenize(words) if word not in stop_words]
                    words = [word for word in words if word not in punctuation]
                    words = [word for word in words if len(word)>2]
                    stems = [snowball.stem(word) for word in words]

                    current["tokens"] = stems
                    if stems not in uniquetokens: #collect all unique token lists
                        uniquetokens.append(stems)

                    resultdict[item][rank]=current
        resultdata.append((resultdict,headlinedict[1]))


    #This is for deleting words which appear only in one unique article in the whole dataset

    vocabulary = []
    for list in uniquetokens: #collect all words from the unique tokens
        vocabulary += list
    vocabcount=Counter(vocabulary) # count the words to identify words with occurences of 1


    for headlinedict in resultdata:
        for item in headlinedict[0]:
            print(item)
            for rank in headlinedict[0][item]:
                current = headlinedict[0][item][rank]
                current["tokens"]= [word for word in current["tokens"] if vocabcount[word] >1]
        with open("preprocessed_"+headlinedict[1], "w", encoding="utf-8") as file:
            json.dump(headlinedict[0], file)


preprocessData()
