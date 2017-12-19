"""
Created on Wed Oct 25 13:34:52 2017

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

matches = db.matches
timelines = db.timelines

matches_10_20 = db.matches_10_20
timelines_10_20 = db.timelines_10_20

matches_gt_27 = db.matches_gt_27
timelines_gt_27 = db.timelines_gt_27

matches_other = db.matches_other
timelines_other = db.timelines_other

game = db.matches_gt_27.find_one()



for player in game['participantIdentities']:
    matches_list = []
    accountId = player['player']['accountId']
    # get all matches of this player
    r = requests.get("https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/%s?api_key=%s" 
                     % (accountId, api_key))  
    data = json.loads(r.content)
    for match in data['matches']:
        match_id = match['gameId']
        if not db.matches_other.find_one({'gameId':match_id}) and not db.matches_gt_27.find_one({'gameId':match_id}) and not db.matches_10_20.find_one({'gameId':match_id}):
            print ("new match", match_id)
            levels = [] 
            # get match data
            match_r = requests.get("https://na1.api.riotgames.com/lol/match/v3/matches/%s?api_key=%s" 
                         % (match_id, api_key))
            match_data = json.loads(match_r.content)   
            if 'participantIdentities' not in match_data:
                time.sleep(6)
                match_r = requests.get("https://na1.api.riotgames.com/lol/match/v3/matches/%s?api_key=%s" 
                         % (match_id, api_key))
            match_data = json.loads(match_r.content) 
            for account in match_data['participantIdentities']:
                account_id = account['player']['accountId']
                # get summoner id
                r = requests.get("https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-account/%s?api_key=%s"
                                     % (account_id, api_key))
                summoner = json.loads(r.content)
                if "summonerLevel" not in summoner:
                    print (summoner)
                    print ("Check if bot", account_id)   
                    experience_lvl = 0
                else:
                    experience_lvl = summoner['summonerLevel']
                levels.append(experience_lvl)
            print (levels)
            time.sleep(6)
            match_data['yulia_player_lvls'] = levels
            if all([i in range(10,20) for i in levels]) or all([i in range(10,20) for i in levels[:5]]):
                matches_10_20.insert_one(match_data)
            elif all([i > 27 for i in levels]):
                matches_gt_27.insert_one(match_data)
            else:
                matches_other.insert_one(match_data)
        else:
            time.sleep(5)
            print ("match %s already in db" % match_id)
 
                        
                
                
                
                
                
                
                
                
                