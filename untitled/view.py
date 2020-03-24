from django.http import HttpResponse
import pandas as pd
import numpy as np
import random
import uuid
import json
from django.http import JsonResponse
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(stop_words='english')
from sklearn.cluster import DBSCAN
from pymongo import MongoClient
from random import randint
import os
from django.conf import settings
import random
import json
from django.views.decorators.csrf import csrf_exempt
from random import randint
from datetime import datetime
# try:
conn = MongoClient("mongodb+srv://rahul:rahul@cluster0-g8qek.mongodb.net/test?retryWrites=true&w=majority")
    # print("Connected successfully!!!")
# except:
#     print("Could not connect to MongoDB")

# database name: mydatabase
db = conn.test

# Created or Switched to collection names: myTable
collection = db.userprofiles


def makeFinalCluster(userId, df1):
    # df = pd.DataFrame(list(collection.find({"userId": userId})))
    # UserId = df.userId[0]
    # if(list(df1[df1.UserId==userId].UserId)==[]):
    #     try:
    #         domain = list(collection.find({"userId":UserId}))[0]['domain']
    #     except:
    #         domain = "UNKNOWN"
    #     Expertise = "UNKNOWN" if df.expertise[0]["industry"] == [] else df.expertise[0]["industry"]
    #     interests = "UNKNOWN" if df.interests[0] == [] else '/'.join(df.interests[0])
    #     df1 = df1.append({"UserId": UserId, "Interest": interests, "Domain":domain, "Expertise": Expertise,"Entrepreneur_rating": np.nan, "Influencer_rating": np.nan, "Expert_rating": np.nan,"Investor_rating": np.nan}, ignore_index=True)
    #     df1.to_csv('recom1.csv',index=False)
    stringData = []
    for i in range(len(df1)):
        stringData.append(list(df1.Interest)[i].split('/'))

    documents = []
    for i in range(len(stringData)):
        documents.append(" ".join(stringData[i]))

    X = vectorizer.fit_transform(documents)
    db = DBSCAN(eps=0.3, min_samples=5).fit(X)
    clusterData = pd.DataFrame({'UserId': df1.UserId, 'Interest': df1.Interest, 'labels': db.labels_})
    return df1,clusterData





def addUserToDataFrame(userId, df1):
    df = pd.DataFrame(list(collection.find({"userId": userId})))
    UserId = df.userId[0]
    if(list(df1[df1.UserId==userId].UserId)==[]):
        try:
            domain = list(collection.find({"userId":UserId}))[0]['domain']
        except:
            domain = "UNKNOWN"
        Expertise = "UNKNOWN" if df.expertise[0]["industry"] == [] else df.expertise[0]["industry"]
        interests = "UNKNOWN" if df.interests[0] == [] else '/'.join(df.interests[0])
        df1 = df1.append({"UserId": UserId, "Interest": interests, "Domain":domain, "Expertise": Expertise,"Entrepreneur_rating": np.nan, "Influencer_rating": np.nan, "Expert_rating": np.nan,"Investor_rating": np.nan}, ignore_index=True)
        df1.to_csv('recom1.csv',index=False)




















def largest(queryResult):
  l =[list(queryResult.Investor_rating)[0],list(queryResult.Entrepreneur_rating)[0],list(queryResult.Influencer_rating)[0],list(queryResult.Expert_rating)[0]]
  m = max(l)
  ind = l.index(m)
  if ind==0:
    return "Entrepreneur_rating"
  if ind==1:
    return "Investor_rating"
  if ind==2:
    return "Entrepreneur_rating"
  else:
    return "Entrepreneur_rating"

def suggestForUnknownUsers(df1):
    size1 = 2 if len(list(df1[df1.Domain=="entrepreneur"]["UserId"]))>=2 else len(list(df1[df1.Domain=="entrepreneur"]["UserId"]))
    size2 = 2 if len(list(df1[df1.Domain=="investor"]["UserId"]))>=2 else len(list(df1[df1.Domain=="investor"]["UserId"]))
    size3 = 2 if len(list(df1[df1.Domain=="expert"]["UserId"]))>=2 else len(list(df1[df1.Domain=="expert"]["UserId"]))
    size4 = 2 if len(list(df1[df1.Domain=="influencer"]["UserId"]))>=2 else len(list(df1[df1.Domain=="influencer"]["UserId"]))
    top = list(df1[df1.Domain=="entrepreneur"]["UserId"].sample(size1))
    top.extend(list(df1[df1.Domain=="investor"]["UserId"].sample(size2)))
    top.extend(list(df1[df1.Domain=="expert"]["UserId"].sample(size3)))
    top.extend(list(df1[df1.Domain=="influencer"]["UserId"].sample(size4)))
    print("top---------")
    print(len(top))
    return top


@csrf_exempt

def recommend(userId):
    file_ = open(os.path.join(settings.BASE_DIR, 'recom1.csv'))
    df1 = pd.read_csv(file_)
    df1,clusterData = makeFinalCluster(userId, df1)
    queryResult = df1[df1['UserId'] == userId]
    # print(queryResult)
    print("check",list(queryResult.Entrepreneur_rating)[0])
    if not np.isnan(list(queryResult.Entrepreneur_rating)[0]):#and list(queryResult.Influencer_rating)[0] != np.nan and list(queryResult.Expert_rating)[0] != np.nan and list(queryResult.Investor_rating)[0] != np.nan):
        print("rating basis")
        parameter = largest(queryResult)
        print(parameter)
        top = list(df1[df1[parameter]==(df1[['Entrepreneur_rating','Influencer_rating', 'Expert_rating', 'Investor_rating']]).apply(max, axis = 1)].iloc[:10]["UserId"])
        #df1[[parameter, 'UserId']].sort_values(parameter, ascending=False).nlargest(10, parameter)
        return list(top.UserId)[:10]
    # if (list(queryResult.Domain)[0] == 'entrepreneur' and list(queryResult.Entrepreneur_rating)[0] == np.nan and
    #         list(queryResult.Influencer_rating)[0] == np.nan and list(queryResult.Expert_rating)[0] == np.nan and
    #         list(queryResult.Investor_rating)[0] == np.nan):
    #     topInvestor = df1[['Investor_rating', 'UserId']].sort_values('Investor_rating', ascending=False).nlargest(10,
    #                                                                                                               'Investor_rating')
    #     print("entrepreneur")
    #     return list(topInvestor.UserId)
    # if (list(queryResult.Domain)[0] == 'investor' and list(queryResult.Entrepreneur_rating)[0] == np.nan and
    #         list(queryResult.Influencer_rating)[0] == np.nan and list(queryResult.Expert_rating)[0] == np.nan and
    #         list(queryResult.Investor_rating)[0] == np.nan):
    #     topInvestor = df1[['Entrepreneur_rating', 'UserId']].sort_values('Entrepreneur_rating',
    #                                                                      ascending=False).nlargest(10,
    #                                                                                                'Entrepreneur_rating')
    #     print("investor")
    #     return list(topInvestor.UserId)
    # if (list(queryResult.Domain)[0] == 'expert' and list(queryResult.Entrepreneur_rating)[0] == np.nan and
    #         list(queryResult.Influencer_rating)[0] == np.nan and list(queryResult.Expert_rating)[0] == np.nan and
    #         list(queryResult.Investor_rating)[0] == np.nan):
    #     topInvestor = df1[['Entrepreneur_rating', 'UserId']].sort_values('Entrepreneur_rating',
    #                                                                      ascending=False).nlargest(10,
    #                                                                                                'Entrepreneur_rating')
    #     print("expert")
    #     return list(topInvestor.UserId)
    # if (list(queryResult.Domain)[0] == 'influencer' and list(queryResult.Entrepreneur_rating)[0] == np.nan and
    #         list(queryResult.Influencer_rating)[0] == np.nan and list(queryResult.Expert_rating)[0] == np.nan and
    #         list(queryResult.Investor_rating)[0] == np.nan):
    #     topInvestor = df1[['Entrepreneur_rating', 'UserId']].sort_values('Entrepreneur_rating',
    #                                                                      ascending=False).nlargest(10,
    #                                                                                                'Entrepreneur_rating')
    #     print("influencer")
    #     return list(topInvestor.UserId)
    #
    # elif (list(queryResult.Domain)[0] == 'UNKNOWN' and list(queryResult.Entrepreneur_rating)[0] == np.nan and
    #       list(queryResult.Influencer_rating)[0] == np.nan and list(queryResult.Expert_rating)[0] == np.nan and
    #       list(queryResult.Investor_rating)[0] == np.nan):
    elif (list(queryResult.Interest)[0] != "UNKNOWN"):
        print("interests")
        top = clusterData[clusterData.labels == list(clusterData[clusterData.UserId == userId].labels)[0]]
        return list(top.UserId)[:10]
    elif (list(queryResult.Interest)[0] == "UNKNOWN"):
        print("not interests")
        # print(suggestForUnknownUsers(df1))
        return suggestForUnknownUsers(df1)
    else:
        print("case not found")


def recommendation(request):
    userId = request.GET["userId"]
   # file_ = open(os.path.join(settings.BASE_DIR, 'recom1.csv'))
    #df1 = pd.read_csv(file_)
    user = []
    for i in list(collection.find({})):
        user.append(i["userId"])
    size = len(user) if len(user)<8 else 8
    users = random.sample(user, size)
    dic = dict() ## {}
    data = []
    for i in users:
        print(i)
        #print("Data[] Loop Start:", data)
        try:
            dic['firstName']=list(collection.find({"userId":i}))[0]["about"]['firstName']
        except:
            dic['firstName'] = "UNKNOWN"
        try:
            dic['lastName']=list(collection.find({"userId":i}))[0]["about"]['lastName']
        except:
            dic['lastName'] = "UNKNOWN"
        try:
            dic['companyName']=list(collection.find({"userId":i}))[0]["about"]['companyName']
        except:
            dic['companyName'] = "UNKNOWN"
        try:
            dic['designation']=list(collection.find({"userId":i}))[0]["about"]['designation']
        except:
            dic['designation'] = "UNKNOWN"
        try:
            dic['location']=list(collection.find({"userId":i}))[0]["about"]['location']
        except:
            dic['location'] = "UNKNOWN"
        try:
            dic['userId']=list(collection.find({"userId":i}))[0]["userId"]
        except:
            dic['userId'] = "UNKNOWN"
        try:
            dic['picture']=list(collection.find({"userId":i}))[0]['picture']
        except:
            dic['picture'] = "UNKNOWN"
        data.append(dic.copy())
    # data = { i : listOfStr[i] for i in range(0, len(listOfStr) ) }

    return JsonResponse({"status":200,"message":"ok","data": data})







def recommendation1(request):
    userId=request.GET["userId"]
    file_ = open(os.path.join(settings.BASE_DIR, 'recom1.csv'))
    df1 = pd.read_csv(file_)
    addUserToDataFrame(userId, df1)
    users = suggestForUnknownUsers(df1)
    dic = dict() ## {}
    data = []
    for i in users:
        print(i)
        #print("Data[] Loop Start:", data)
        try:
            dic['firstName']=list(collection.find({"userId":i}))[0]["about"]['firstName']
        except:
            dic['firstName'] = "UNKNOWN"
        try:
            dic['lastName']=list(collection.find({"userId":i}))[0]["about"]['lastName']
        except:
            dic['lastName'] = "UNKNOWN"
        try:
            dic['companyName']=list(collection.find({"userId":i}))[0]["about"]['companyName']
        except:
            dic['companyName'] = "UNKNOWN"
        try:
            dic['designation']=list(collection.find({"userId":i}))[0]["about"]['designation']
        except:
            dic['designation'] = "UNKNOWN"
        try:
            dic['location']=list(collection.find({"userId":i}))[0]["about"]['location']
        except:
            dic['location'] = "UNKNOWN"
        try:
            dic['userId']=list(collection.find({"userId":i}))[0]["userId"]
        except:
            dic['userId'] = "UNKNOWN"
        try:
            dic['picture']=list(collection.find({"userId":i}))[0]['picture']
        except:
            dic['picture'] = "UNKNOWN"
        data.append(dic.copy())
    # data = { i : listOfStr[i] for i in range(0, len(listOfStr) ) }
    return JsonResponse({"data": data})



def interest(request):
    userId=request.GET["userId"]
    print(userId)
    data= []
    # data = [df1.to_dict(orient='records')[randint(1, 2000)] for i in range(8)]
    df2 = pd.read_csv('interest.csv')
    df3 = pd.read_csv('userName.csv')
    # df1.to_dict(orient='records')[0]["FirstName"] = "rahul"
    print("check")
    print(len(df2))
    df = df2[pd.Series(userId not in df2['LikedByUser'][k].split('#') for k in range(len(df2['LikedByUser'])))]
    df = df[pd.Series(userId not in df2['DisLikedByUser'][k].split('#') for k in range(len(df2['LikedByUser'])))]
    print("check2")
    if(len(df)==0):
        print(len(df))
        return JsonResponse({"data": data})
    elif(len(df)<=8):
        for i in range(len(df)):
            dict1 = df.to_dict(orient='records')[i]
            dict2 = df3.to_dict(orient='records')[randint(1, len(df3) - 1)]
            dict1.update(dict2)
            data.append(dict1)

        return JsonResponse({"data": data})

    print(len(df))
    for i in range(8):
        dict1 = df.to_dict(orient='records')[randint(1, len(df)-1)]
        dict2 = df3.to_dict(orient='records')[randint(1, len(df3)-1)]
        dict1.update(dict2)
        data.append(dict1)

    # data = df2.to_dict(orient='records')[randint(1, 2000)] for i in range(8)

    return JsonResponse({"data": data})

def likedInterestData(request):
    userId=request.GET['userId']
    print(type(userId))
    data= []
    # data = [df1.to_dict(orient='records')[randint(1, 2000)] for i in range(8)]
    df2 = pd.read_csv('interest.csv')
    df3 = pd.read_csv('userName.csv')
    print(df2.head())
    df = df2[pd.Series(userId in df2['LikedByUser'][k].split('#') for k in range(len(df2['LikedByUser'])))]
    print(df.head())
    # df1.to_dict(orient='records')[0]["FirstName"] = "rahul"
    list1 = df.to_dict(orient='records')
    for i in list1:
        i.update(df3.to_dict(orient='records')[randint(1,len(df3)-1)])
        data.append(i)



    # data = df2.to_dict(orient='records')[randint(1, 2000)] for i in range(8)
    print("Json data :", data)
    return JsonResponse({"data": data})

def likeInterest(request):
    file = open(os.path.join(settings.BASE_DIR, 'interest.csv'))
    if request.method == 'POST':
        # print(get_response(request))
        print(request.POST)
        userId = request.POST.get('userId')
        interestId = request.POST.get('id')

        # print(userId)
        print(type(interestId))

        df = pd.read_csv(file)
        print("hello")
        print(len(df))
        print(df[df['Id'] == interestId])

        df.at[df.index[df['Id'] == interestId].tolist()[0],'LikedByUser']= df[df.Id==interestId]['LikedByUser'].tolist()[0]+'#'+userId
        print(df[df['Id'] == 109140928]['LikedByUser'])
        df.to_csv('interest.csv', index=False)
        return HttpResponse(200)
def disLikeInterest(request):
    file1 = open(os.path.join(settings.BASE_DIR, 'interest.csv'))
    if request.method == 'POST':
        userId = request.POST.get('userId')
        interestId = request.POST.get('id')

        df = pd.read_csv(file1)

        df.at[df.index[df['Id'] == interestId].tolist()[0], 'DisLikedByUser'] = df[df.Id == interestId]['DisLikedByUser'].tolist()[0] + '#' + userId
        df.to_csv('interest.csv', index=False)

        return HttpResponse(200)



def createInterest(request):
    file = open(os.path.join(settings.BASE_DIR, 'interest.csv'))
    if request.method == 'POST':
        # print(get_response(request))
        print(request.POST)
        userId = request.POST.get('userId')
        Type = request.POST.get('Type')
        Subject = request.POST.get('Subject')
        Industry = request.POST.get('Industry')
        Function = request.POST.get('Function')
        TypeOfService = request.POST.get('TypeOfService')
        AdditionalInfo = request.POST.get('AdditionalInfo')
        TimeLine = request.POST.get('TimeLine')



        now = datetime.now()

        df = pd.read_csv(file)
        df = df.append({"UserId":userId , "Id": uuid.uuid4().int, "LikedByUser": "uuid",
                        "DisLikedByUser": "uuid",
                        "Subject": Subject, "Industry": Industry, "Function": Function,
                        "TypeOfService": TypeOfService, "AdditionalInfo": AdditionalInfo, "Type": Type, "TimeLine": TimeLine,
                        "CreatedTime": now.strftime("%d-%m-%Y %H:%M:%S"), "ExpertiseLevel": random.choice([1,2,3]), "Award": "UNKNOWN",
                        "Image": "UNKNOWN"}, ignore_index=True)
        df.to_csv('interest.csv', index=False)
        return HttpResponse(200)


def index(request):
    return HttpResponse("<h2 align='middle' style='color:green'>Recommendation System</h2><br><br>")
