import json
import nltk
from nltk.corpus import stopwords
import string
from nltk.stem.snowball import SnowballStemmer
import os
import pickle
from gsdmm import MovieGroupProcess

#this calculates the topic model and will take some time to process
source_path= os.getcwd()
jsonpath = source_path= os.getcwd()+"Data"


#read preprocessed data and return a set of unique articles
def getSetofTagLists(jsonpath):
    os.chdir(jsonpath)
    publisherfilepaths = [x for x in os.listdir() if  x.startswith("preprocessed_")]
    data=[]
    result = []

    for x in publisherfilepaths:
        print(x)
        with open(x, "r", encoding="utf-8") as file:
            data.append(json.load(file))
            file.close()


    for publisher in data:
        for item in publisher:
            print(item)

            for rank in publisher[item]:
                current = publisher[item][rank]["tokens"]
                if current == []:
                    continue

                result.append(current)
    return set(map(tuple, result))


#initialize topic model
mgp = MovieGroupProcess(K=250, alpha=0.1, beta=0.1, n_iters=70)

tokenizedHeadlines= getSetofTagLists(jsonpath)

vocabulary = list(set([x for headlines in tokenizedHeadlines for x in headlines]))
wordcount = len([x for headlines in tokenizedHeadlines for x in headlines])
vocab_length = len(vocabulary)

#calculate topic model on data
y = mgp.fit(tokenizedHeadlines, vocab_length)

#save
with open("topicmodel_1.model","wb") as file:
    pickle.dump(mgp,file)
    file.close()
