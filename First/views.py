from django.shortcuts import render
from django.http import HttpResponse
import random
import os
import requests, json
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

# Create your views hundered

def custom_accuracy(y_test,y_pred,thresold):
    right = 0
    l = len(y_pred)
    for i in range(0,l):
        if(abs(y_pred[i]-y_test[i]) <= thresold):
            right += 1
    return ((right/l)*100)

def predict_score():
    global lin, sc
    dataset = pd.read_csv('C://Users/singh/Desktop/Django/projects/First/First/odi.csv')
    X = dataset.iloc[:,[7,8,9,12,13]]
    Y = dataset.iloc[:,14]

    ######### training using 75% data and testing using remaining 25% data ###########

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.25, random_state = 0)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    ########### Using RandomForest Algorithm as it shows the best result with 79% accuracy ##################
    lin = RandomForestRegressor(n_estimators=100,max_features=None)
    lin.fit(X_train,y_train)

    y_pred = lin.predict(X_test)
    score = lin.score(X_test,y_test)*100
    print("R-squared value:" , score)
    # print("Custom accuracy:" , custom_accuracy(y_test,y_pred,20))



def home(request):
    # predict_score()
    # print (lin.predict(sc.transform(np.array([[150, 0, 17, 65, 78]]))))
    global match
    global live_score_url
    match_url="https://cricapi.com/api/matches?apikey=ZSTtSDmD3eU8nGyPeXNNJEaAU1F3"
    response=requests.get(match_url)
    data=json.loads(response.text)
    match=data['matches']

    #spliting the string to get the date
    for i in range(len(match)):
        match_date = match[i]["dateTimeGMT"].split("T")[0]
        match[i]["date"] = match_date

    list_of_live_score = []
    for i in match:
        i["team_1"] = i.pop("team-1")
        i["team_2"] = i.pop("team-2")

####################### Live score section#############################
        if i['matchStarted'] and (i['type'] == "ODI" or i['type'] == "Tests" or i['type'] == "Twenty20"):
            live_score_url='https://cricapi.com/api/cricketScore?apikey=ZSTtSDmD3eU8nGyPeXNNJEaAU1F3&unique_id='
            live_score_url_final=live_score_url+str(i['unique_id'])
            response=requests.get(live_score_url_final)
            live_score_data=json.loads(response.text)
            live_score_data["team_1"] = live_score_data.pop("team-1")
            live_score_data["team_2"] = live_score_data.pop("team-2")
            list_of_live_score.append(live_score_data)

    #################Calender section############################


    ###########################previous match details###############################
    list_of_match_details_id=[]

    for match_detail in match:
        days=0
        x=0
        month=0
        y=0
        if (match_detail['type'] == "ODI" or match_detail['type'] == "Tests" or match_detail['type'] == "Twenty20"):
            date=match_detail['date']
            days=date[8]+date[9]
            months=date[5]+date[6]
            months=int(months)
            days=int(days)

            today_day=datetime.now()
            x=today_day.day
            y=today_day.month


            if months<=y:
                if days<=x:
                    list_of_match_details_id.append(match_detail['unique_id'])
    global list_of_matches
    list_of_matches=[]
    for id in list_of_match_details_id:
        url = "https://cricapi.com/api/fantasySummary?apikey=ZSTtSDmD3eU8nGyPeXNNJEaAU1F3&unique_id="+ str(id)
        response = requests.get(url)
        data = json.loads(response.text)
        count=0
        data['unique_id']=id
        for team in data['data']['team']:
            if count==0:
                data['team_1']=team['name']
                count=count+1
            else:
                data['team_2']=team['name']
        list_of_matches.append(data)
    global id_search
    id_search = 1
    if list_of_match_details_id == []:
        not_update=" Previous matches details have not been updated yet!!! "
    else:
        not_update=''

    context={
        "match_date" : match_date,
        "matches":match,
        "live_score":list_of_live_score,
        "id1":id_search,
        "previous_matches":list_of_matches,
        "not_update_previous_matches_details":not_update
    }
    return render(request,"home.html",context)

def match_calender(request):
    global calender_data
    calender_url="https://cricapi.com/api/matchCalendar?apikey=ZSTtSDmD3eU8nGyPeXNNJEaAU1F3"
    response=requests.get(calender_url)
    data=json.loads(response.text)
    calender_data=data['data']

    context={
        "calender_data":calender_data,
        "id1": 1
    }


    return render(request,'match-calender.html',context)

def search(request,id):
    print(id)
    if id==1:
        query=request.GET.get("text","off")
        pid = []
        url = 'https://cricapi.com/api/playerFinder?apikey=ZSTtSDmD3eU8nGyPeXNNJEaAU1F3&name='+ query

        resp = requests.get(url)
        data = json.loads(resp.text)
        player = data['data']

        for i in player:
            key_list = list(i.keys())
            val_list = list(i.values())
            pid.append(val_list[key_list.index("pid")])

        list_data = []

        for unique_id in pid:
            url2 = "https://cricapi.com/api/playerStats?apikey=ZSTtSDmD3eU8nGyPeXNNJEaAU1F3&pid=" + str(unique_id)
            response = requests.get(url2)
            data_player = json.loads(response.text)

            list_data.append(data_player)

    else:
        url2 = "https://cricapi.com/api/playerStats?apikey=ZSTtSDmD3eU8nGyPeXNNJEaAU1F3&pid=" + str(id)
        response = requests.get(url2)
        data_player = json.loads(response.text)
        list_data = [data_player]


    context={
        "player_data":list_data,
        "id1":1
     }

    return render(request,"search.html",context)


def batting_record(data,match_type):
    dict = {}
    SR = (data['data']['batting'][match_type]['SR'])
    Ave = (data['data']['batting'][match_type]['Ave'])
    Runs = (data['data']['batting'][match_type]['Runs'])
    Inns = (data['data']['batting'][match_type]['Inns'])
    fifty = (data['data']['batting'][match_type]['50'])
    hundered = (data['data']['batting'][match_type]['100'])
    if Inns == '' or Inns == '-':
        Inns = "0"
    if Runs == '' or Runs == '-':
        Runs = '0'
    if Inns != '0':
        Inn = float(int(Runs) / int(Inns))
    else:
        Inn = 0
    if SR == "" or SR == '-':
        SR = "0"
    strikeRate = float(SR)
    if Ave == "" or Ave == '-':
        Ave = '0'
    Avg = float(Ave)
    runs = int(Runs)
    if fifty == '' or fifty == '-':
        fifty = '0'
    if hundered == '' or hundered == '-':
        hundered = '0'
    fifties = int(fifty)
    hundereds = int(hundered)
    if strikeRate > 120:
        strikeRate += 10
    if Avg >= 50:
        Avg += 10
    if Avg > 32 and Avg < 50:
        Avg += 5
    if Inn > 30:
        Inn += 10

    strikeRate = (strikeRate / 200) * 100
    if fifties > 25:
        fifties = fifties / 8
    else:
        fifties = fifties / 10
    if hundereds > 25:
        hundereds = hundereds / 8
    else:
        hundereds = hundereds / 10
    total = (strikeRate + Avg + Inn + fifties + hundereds) / 5
    dict["name"] = data['name']
    dict['playingRole']=data['playingRole']
    dict["total"] = str(total)
    dict['pid']=data['pid']
    return dict
   # print(dict)
def bowling_record(data,match_type):
    dict={}
    Econ = (data['data']['bowling'][match_type]['Econ'])
    Ave = (data['data']['bowling'][match_type]['Ave'])
    Runs = (data['data']['bowling'][match_type]['Runs'])
    Inns = (data['data']['bowling'][match_type]['Inns'])
    Wkts = (data['data']['bowling'][match_type]['Wkts'])
    Balls = (data['data']['bowling'][match_type]['Balls'])
    if Econ=='' or Econ=='-':
        Econ='0'
    if Ave==''or Ave=='-':
        Ave='0'
    if Runs=='' or Runs=='-':
        Runs='0'
    if Inns==''or Inns=='-':
        Inns='0'
    if Wkts=='' or Wkts=='-':
        Wkts='0'
    if Balls==''or Balls=='-':
        Balls='0'
    avg=float(Ave)
    if avg<35:
        avg=avg+5
    econ=(float(Econ)/6)*100
    if econ<5:
        econ=econ+5

    Inns = int(Inns)
    if Inns == 0:
        Inns = Inns + 1

    inns=(int(Wkts)/int(Inns))*100
    if inns<200:
        inns=inns+10
    run=(int(Runs)/int(Balls))*100
    total=(avg+econ+inns+run)/4
    dict["name"] = data['name']
    dict['playingRole']=data['playingRole']
    dict["total"] = str(total)
    dict['pid'] = data['pid']
    return dict


def player_accuracy(data,match_type):
    if data['playingRole']=="Top-order batsman" or data['playingRole']=="Opening batsman" or data['playingRole']=="Middle-order batsman":
        player_record_demo=batting_record(data,match_type)
    elif data['playingRole']=="Bowler":
        player_record_demo=bowling_record(data,match_type)
    elif data['playingRole']=="Wicketkeeper batsman":
        player_record_demo=batting_record(data,match_type)
    elif data['playingRole']=="Allrounder" or data['playingRole']== "Bowling allrounder" or data['playingRole']== "Batting allrounder":
        player_record_demo1=batting_record(data,match_type)
        player_record_demo2=bowling_record(data,match_type)
        player_record_demo ={}
        player_record_demo['name']=player_record_demo1['name']
        player_record_demo['playingRole']=player_record_demo1['playingRole']
        player_record_demo['total']=(float(player_record_demo1['total'])+float(player_record_demo2['total']))/2
        player_record_demo['pid'] = player_record_demo1['pid']
    else:
        player_record_demo=batting_record(data,match_type)


    return player_record_demo



def detail_player_anylize(data,match_type):
    if data.get('data').get('batting').get('match_type'):
        player_accuracy_details=player_accuracy(data,match_type)
    else:
        firstclass='firstClass'
        player_accuracy_details=player_accuracy(data,firstclass)
    return player_accuracy_details

def anylize_player(squad,match_type):
    list_of_detail_player=[]
    for team in squad:
        for player_id in team['players']:
            player_url = "https://cricapi.com/api/playerStats?apikey=ZSTtSDmD3eU8nGyPeXNNJEaAU1F3&pid=" + str(player_id['pid'])
            response = requests.get(player_url)
            data_player = json.loads(response.text)
            list_of_detail_player.append(detail_player_anylize(data_player,match_type))
    #print(list_of_detail_player)
    return list_of_detail_player


def custom_team(request,id):
    url="https://cricapi.com/api/fantasySquad?apikey=ZSTtSDmD3eU8nGyPeXNNJEaAU1F3&unique_id="+str(id)
    response=requests.get(url)
    data=json.loads(response.text)
    squad=data["squad"]
    final_squad=anylize_player(squad,"tests")#id['match_type']

    context={
        "current_match":final_squad,
        "id1":1
    }
    return render(request,'player_efficiency.html',context)
