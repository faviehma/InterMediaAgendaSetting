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
import xlsxwriter

# This exports the topics in an Excel file, so that one can name the topics.



os.chdir("C:\\Users\\fabia\\Documents\\GitHub\\Scraping\\ProcessedData\\result3\\")

with open("topicmodel_1.model","rb") as file:
    mgp = pickle.load(file)


word_dist=mgp.cluster_word_distribution

mostFreqTopicWords = []

for dic in word_dist:

    sortedDic={k: v for k, v in sorted(dic.items(), key=lambda item: item[1], reverse=True)}
    res={}
    for x in list(sortedDic)[0:20]:
        res[x]=sortedDic[x]
    mostFreqTopicWords.append(res)

workbook = xlsxwriter.Workbook('data.xlsx')
worksheet = workbook.add_worksheet()
row=0
for item in mostFreqTopicWords:
    col=0
    row += 1
    worksheet.write(row, col, str(row-1))
    worksheet.write(row,col+1, mgp.cluster_doc_count[row-1])
    col +=1
    for elem in item:
        worksheet.write(row, col+1, elem)
        col += 1

workbook.close()
