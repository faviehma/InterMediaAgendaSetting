import pandas as pd
import os
import json
from pandas.io.json import json_normalize

#reorders the data to form one dataset and adds the topic labels created in the csv file. assditionally some of the stats on the dataset are retrieved
#Running this code with the Hidrogen application for the Atom editor gives a Jupyter Notebook like experience
source_path = os.getcwd()
os.chdir(source_path+"\\Data")
taggedFiles = [x for x in os.listdir() if x.startswith("labeled_preprocessed")]

#converting single files
def convertDict(taggedFiles):
    result=[]

    for x in taggedFiles:

        with open(x, encoding = "utf-8") as file:
            data = json.load(file)
            file.close()


        for time in data:
            object = {}
            for rank in data[time]:
                object =data[time][rank]
                object["time"] = time
                object["rank"] = rank
                object["publisher"] = x.split("_")[-1].replace(".json","")
                result.append(object)

    return result


with open("combined_data.json", "w", encoding= "utf-8") as file:
    json.dump(convertDict(taggedFiles),file)
    file.close()


with open("combined_data.json", "r", encoding= "utf-8") as file:
    data = json.load(file)
    file.close()


#load topic labels and connect them to the data
os.chdir(source_path+"\\model")

#load zuordnung
topic_zuordnung=pd.read_excel("data.xlsx",sheet_name="Tabelle1")
topic_zuordnung["topicNumOld"]= pd.to_numeric(topic_zuordnung["topicNumOld"])
topic_zuordnung["topicNumNew"]= pd.to_numeric(topic_zuordnung["topicNumNew"],errors='coerce')
topic_zuordnung= topic_zuordnung.drop("Unnamed: 1",1).drop("Unnamed: 4",1).drop("Unnamed: 5",1).drop("Unnamed: 6",1).drop("Unnamed: 7",1).drop("Unnamed: 8",1)

os.chdir(source_path+"\\Data")

#read data as combined df
df=pd.DataFrame(data)
df["time"]=pd.to_datetime(df["time"])
df["topicAcc"]=pd.to_numeric(df["topicAcc"])
df["rank"]= pd.to_numeric(df["rank"])
df["topicNum"]= pd.to_numeric(df["topicNum"])

#combine labels with dataframe
df = df.merge(topic_zuordnung,left_on="topicNum", right_on="topicNumOld")


#uncomment these lines to get stats
"""#get some stats on the data
timepoint_count = df["time"].nunique()
timepoint_count

article_count = df["time"].count()
article_count

df["title_text_merge"]= df["title"]+df["text"]
article_count_unique = df["title_text_merge"].nunique()
article_count_unique

topic_count = df["topicNum"].nunique()
topic_count

topic_count_labeled = df["topicNumNew"].nunique()
topic_count_labeled"""

#drop data without topic label
df =df.dropna(subset=["topicNumNew"])

#uncomment these lines to get stats
"""#get some more stats on the data with topic labels
article_count_labeled = df["time"].count()
article_count_labeled

article_count_labeled_withoutCor= df[df["topicName"] != "corona"]["time"].count()
article_count_labeled_withoutCor


article_count_unique_labeled = df["title_text_merge"].nunique()
article_count_unique_labeled

#read stationary data produced by R (This can only be done after all the R code has been run)
df_stationary = pd.read_csv("time_data_percent_stationary.csv")
df_stationary["time"].unique()

#filter data for stationary topics
stationary_topics = list(df_stationary["topicName"].unique())
df_stat_filtered=df[df.topicName.isin(stationary_topics)]

#get even more stats on stationary data
timepoint_count_stat = df_stat_filtered["time"].nunique()
timepoint_count_stat

article_count_stat = df_stat_filtered["time"].count()
article_count_stat

article_count_unique_stat = df_stat_filtered["title_text_merge"].nunique()
article_count_unique_stat

topic_count_labeled_stat = df_stationary["topicName"].nunique()
topic_count_labeled_stat"""


#export overall topic distribution to create a plot
df.pivot_table(index=["topicName"], values="text", aggfunc="count").fillna(0).sort_values(by="text", ascending=False).to_csv("topic_distribution_overall.csv")

#create df of values which can be fed into the VAR Model
values = df.pivot_table(index=["time","topicName"],columns="publisher", values="topicNum", aggfunc="count", fill_value=0)

values.sort_values(by=['time'], inplace=True, ascending=False)

#create an empty dataframe with a value for every topic at every time point
topics = list(df["topicName"].unique())
dates = pd.date_range('2020-02-01 /01:00', periods=1439, freq='1H')
ind = pd.MultiIndex.from_product([dates, topics], names=["time","topicName"])
empty_df = pd.DataFrame(index = ind)

#fill the empty df with the values and fill NA values with 0
result = pd.merge(empty_df,values, how="left", on=["time","topicName"]).fillna(0)

#write to file for count data
result.to_csv("time_data_count.csv")

#calculate percentages
result = result/20
result = result.fillna(0)
#write percentages
result.to_csv("time_data_percent.csv")
