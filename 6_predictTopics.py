import json
import nltk
from nltk.corpus import stopwords
import string
from nltk.stem.snowball import SnowballStemmer
import os
import pickle
from gsdmm import MovieGroupProcess
import numpy as np
import pandas as pd

#this uses the calculated topic model to predict topics

source_path = os.getcwd()
os.chdir(source_path+"\\model")

with open("topicmodel_1.model","rb") as file:
    mgp = pickle.load(file)

#doc_count= pd.DataFrame(mgp.cluster_word_count)
#doc_count.describe()
#doc_count[doc_count[0]!=0].describe()
#doc_count.describe()

os.chdir(source_path+"\\Data")

filesToTag = [x for x in os.listdir() if x.startswith("preprocessed")]

for x in filesToTag:
    predictedTokens = {}
    with open(x, encoding="utf-8") as file:
        data = json.load(file)
        file.close()

    result = data
    for time in data:
        print(x+ " " +time)
        for rank in data[time]:
            tokens = data[time][rank]["tokens"]
            if " ".join(tokens) in predictedTokens:
                prediction = predictedTokens[" ".join(tokens)]
            else:
                prediction = mgp.choose_best_label(data[time][rank]["tokens"])
                predictedTokens[" ".join(tokens)]=prediction

            result[time][rank]["topicNum"]= str(prediction[0])
            result[time][rank]["topicAcc"]= str(prediction[1])


    with open("labeled_"+x, "w", encoding="utf-8") as file:
        json.dump(result,file)
        file.close()
