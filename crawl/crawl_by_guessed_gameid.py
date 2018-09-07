#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 16:51:07 2018

@author: yuliabarannikova
"""

import requests
import json
import time
import datetime


# get key from developer.riotgames.com
api_key=""

from pymongo import MongoClient

client = MongoClient()

db = client.league_of_legends

matches = db.matches_season11


# manually guess game's id
start = 2778355860
for i in range(10000):
    match_id = start + i
    time.sleep(3)
    match_r = requests.get("https://na1.api.riotgames.com/lol/match/v3/matches/%s?api_key=%s" 
                             % (match_id, api_key))
    # wait if rate limit is exceeded
    if match_r.status_code in (503, 429):
        time.sleep(120)
        match_r = requests.get("https://na1.api.riotgames.com/lol/match/v3/matches/%s?api_key=%s" 
                             % (match_id, api_key))
    if match_r.status_code == 404:
        print("%s is not a valid match" % match_id)
        continue
    match_data = json.loads(match_r.content) 
    try:
        match_date = datetime.datetime.fromtimestamp(match_data['gameCreation']/1000)
    except:
        print(match_data)
    # hours delta is a difference between game creation and current time
    hours_delta = (datetime.datetime.now()-match_date).total_seconds()/3600
    print (hours_delta)
    # only get matches that were played up to 72 hours from now
    if hours_delta > 72:
        continue
    match_data['hours_delta'] = hours_delta
    levels = []
    if 'player' not in match_data['participantIdentities'][0]:
        continue
    for account in match_data['participantIdentities']:
        account_id = account['player']['accountId']
        # get summoner id
        r = requests.get("https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-account/%s?api_key=%s"
                                         % (account_id, api_key))
        summoner = json.loads(r.content)
        if r.status_code == 429:
            time.sleep(60)
            r = requests.get("https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-account/%s?api_key=%s"
                                         % (account_id, api_key))
            summoner = json.loads(r.content)
        if "summonerLevel" not in summoner:
            # certain players do not have summoner levels
            print (summoner)
            experience_lvl = 0
        else:
            experience_lvl = summoner['summonerLevel']
        levels.append(experience_lvl)
    time.sleep(5)
    print (match_id)
    print ("added %s" % i)
    match_data['yulia_player_lvls'] = levels
    # save to db
    db.matches_season11_72hrs.insert_one(match_data)
    
    
    