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

playtraces = db.playtraces_season11_72hrs


# creates playtraces
for match in db.matches_season11_72hrs.find():
    match_id = match['gameId']
    # check if playtrace already in db
    if playtraces.find_one({'id':{'$regex':'{}_.*'.format(match_id)}}):
        continue
    # get timeline data
    timeline_r = requests.get("https://na1.api.riotgames.com/lol/match/v3/timelines/by-match/%s?api_key=%s" 
                             % (match_id, api_key))
    timeline_data = json.loads(timeline_r.content)
    timeline_data['gameId'] = match_id
    players = match['participantIdentities']
    # get playtraces associated with each player
    for player in players:
        # bots don't have summoner id
        try:
            summoner_id = player['player']['summonerId']
        except:
            continue
        participant_id = player['participantId']
        playtrace_id = "{}_{}".format(match_id, summoner_id)
        print("checking {}".format(playtrace_id))
        role = match['participants'][participant_id-1]['timeline']['role']
        lane = match['participants'][participant_id-1]['timeline']['lane']
        champion_id = match['participants'][participant_id-1]['championId']
        highest_tier = match['participants'][participant_id-1]['highestAchievedSeasonTier']
        summoner_level = match['yulia_player_lvls'][participant_id-1]
        # construct playtraces_data
        playtraces_data = {
            'id': playtrace_id,
            "gameId": match_id,
            "summonerId": summoner_id,
            "playtrace": [],
            "role": role,
            "lane": lane,
            "championId": champion_id,
            "highestAchievedSeasonTier": highest_tier,
            "summonerLvl": summoner_level,
            "hours_delta": match['hours_delta'],
            "mapId": match['mapId'],
            "gameMode": match['gameMode'],
            "gameType": match['gameType'],
            "gameVersion": match['gameVersion'],
            "queueId": match['queueId']
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
                # create _ASSIST, _KILL and _DEATH event types
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
        # make sure that the playtrace is not in the db
        if not playtraces.find_one({'id': playtrace_id}):
            playtraces.insert_one(playtraces_data)
                    
        time.sleep(4)
                    
                    
                    
                    
                    
                    
                    