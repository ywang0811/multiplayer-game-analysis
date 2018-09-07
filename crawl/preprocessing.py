#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 14:08:07 2017

@author: yuliabarannikova
"""

import requests
import json
import time

# get key from developer.riotgames.com
api_key = ""

from pymongo import MongoClient

client = MongoClient()

db = client.league_of_legends

playtraces_gt_27 = db.playtraces_gt_27


# creates playtraces
for i in db.matches_gt_27.find():
    match_id = i['gameId']
    if playtraces_gt_27.find_one({'id':{'$regex':'{}_.*'.format(match_id)}}):
        continue
    timeline_r = requests.get("https://na1.api.riotgames.com/lol/match/v3/timelines/by-match/%s?api_key=%s" 
                             % (match_id, api_key))
    timeline_data = json.loads(timeline_r.content)
    timeline_data['gameId'] = match_id
    players = i['participantIdentities']
    for player in players:
        summoner_id = player['player']['summonerId']
        participant_id = player['participantId']
        playtrace_id = "{}_{}".format(match_id, summoner_id)
        print("checking {}".format(playtrace_id))
        playtraces_data = {
            'id': playtrace_id,
            "gameId": match_id,
            "summonerId": summoner_id,
            "playtrace": []
                }
        if 'frames' not in timeline_data:
            print(timeline_data)
            continue
        for frame in timeline_data['frames']:
            for event in frame['events']:
                if "creatorId" in event:
                    if event['creatorId'] == participant_id:
                        playtraces_data['playtrace'].append(event)
                elif "participantId" in event:
                    if event['participantId'] == participant_id:
                        playtraces_data['playtrace'].append(event)
                elif "killerId" in event:
                    if event['killerId'] == participant_id:
                        playtraces_data['playtrace'].append(event)
                    if 'assistingParticipantIds' in event and participant_id in event['assistingParticipantIds']:
                        assist_event = event.copy()
                        assist_event['type'] = event['type'] + "_ASSIST"
                        playtraces_data['playtrace'].append(assist_event)
                    if 'victimId' in event and event['victimId'] == participant_id:
                        death_event = event.copy()
                        death_event['type'] = event['type'].replace("KILL","DEATH")
                        playtraces_data['playtrace'].append(death_event)
                else:
                    print (event)
        if not playtraces_gt_27.find_one({'id': playtrace_id}):
            playtraces_gt_27.insert_one(playtraces_data)
                    
        time.sleep(2)
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    