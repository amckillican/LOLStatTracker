from riotwatcher import LolWatcher, ApiError
import json
import os

# set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# importing the config file
with open("config.json") as config_file:
    config_info = json.load(config_file)

    lol_watcher = LolWatcher(config_info["APIKEY"])
    my_region = config_info["REGION"]
    sum_name = config_info["SUM_NAME"]
    num_games = config_info["NUM_GAMES"]
    champ_id = config_info["CHAMPIONID"] # can be found in data dragon json file

# top_left = open("top_left.txt", "w+")
# top_right = open("top_right.txt", "w+")

me = lol_watcher.summoner.by_name(my_region, sum_name)
my_ranked_stats = lol_watcher.league.by_summoner(my_region, me['id'])

# checking for api errors
try:
    response = lol_watcher.summoner.by_name(my_region, sum_name)
except ApiError as err:
    if err.response.status_code == 429:
        print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
        print('this retry-after is handled by default by the RiotWatcher library')
        print('future requests wait until the retry-after time passes')
    elif err.response.status_code == 404:
        print('Summoner name not found, check the config file.')
    else:
        raise 
    
wins = my_ranked_stats[0]["wins"]
total_games_played = wins + my_ranked_stats[0]["losses"]

with open("match_data.json") as match_json_file:
    if os.path.getsize("match_data.json") != 0:
        match_json_data = json.load(match_json_file)
    else:
        match_json_data = {}

matchlist = lol_watcher.match.matchlist_by_puuid("NA1", me["puuid"], 0, num_games, type="ranked")

# checking if the match is already in the list
existing = False
for index, matches in enumerate(matchlist):
    for existing_matches in match_json_data:
        if matches == existing_matches:
            existing = True
    
    if existing == False:
        match_json_data[matches] = {}
        
        kills = 0
        assists = 0
        blue_side_kills = 0
        red_side_kills = 0
        total_kills = 0
        my_team = 0
        deaths = 0
        cs = 0
        gametime = 0
        win = False
        
        selected_match = lol_watcher.match.by_id(my_region, matches)["info"]
        participants = selected_match["participants"]
        
        match_json_data[matches]["gametime"] = selected_match["gameDuration"]
        
        for people in participants:
            if people["teamId"] == 100: blue_side_kills += people["kills"]
            if people["teamId"] == 200: red_side_kills += people["kills"]
            if people["summonerName"] == sum_name:
                my_team = people["teamId"]
                kills += people["kills"]
                assists += people["assists"]
                deaths += people["deaths"]
                cs += people["totalMinionsKilled"] + people["neutralMinionsKilled"]
                if people["win"] == True: match_json_data[matches]["win"] = True
                else: match_json_data[matches]["win"] = False
                
                
        
        if my_team == 100: total_kills += blue_side_kills
        if my_team == 200: total_kills += red_side_kills
        
        # resetting the team kills if desired summoner switches teams
        blue_side_kills = 0
        red_side_kills = 0
        my_team = 0
        
        match_json_data[matches]["kills"] = kills
        match_json_data[matches]["deaths"] = deaths
        match_json_data[matches]["assists"] = assists
        match_json_data[matches]["cs"] = cs
        match_json_data[matches]["total_kills"] = total_kills
        
    existing = False
    
# write the match info to the file
with open("match_data.json", "w") as match_json_file:
    match_json_file.write(json.dumps(match_json_data, indent = 2))

kp = 0
kda = 0
wr20g = 0
cspm = 0
win20g = 0
loss20g = 0
sum_kills = 0
sum_assists = 0
sum_total_kills = 0
sum_deaths = 0
sum_cs = 0
sum_gametime = 0

for index, matches in enumerate(match_json_data):
    # check first 20 games for winrate
    if index < 20:
        if match_json_data[matches]["win"] == True: win20g += 1
        if match_json_data[matches]["win"] == False: loss20g += 1
    sum_gametime += match_json_data[matches]["gametime"]
    sum_kills += match_json_data[matches]["kills"]
    sum_deaths += match_json_data[matches]["deaths"]
    sum_assists += match_json_data[matches]["assists"]
    sum_cs += match_json_data[matches]["cs"]
    sum_total_kills += match_json_data[matches]["total_kills"]
    
    kp = round(100*(sum_kills + sum_assists)/sum_total_kills)
    kda = round((sum_kills + sum_assists)/sum_deaths, 2)
    wr20g = round(100*win20g/(loss20g+win20g))
    cspm = round(sum_cs/(sum_gametime/60), 2)

mastery_points = lol_watcher.champion_mastery.by_summoner_by_champion(my_region, me["id"], champ_id)["championPoints"]

top_left_data = {}
top_right_data = {}

top_left_data["WR"] = "Overall WR: {}%\n".format(round(wins / total_games_played*100))
top_left_data["WR20G"] = "WR (20 Games): {}%\n".format(round(wr20g))
top_left_data["RANK"] = "Rank: {} {}\n".format(my_ranked_stats[0]["tier"], my_ranked_stats[0]["rank"])
top_left_data["LP"] = "LP: {}".format(my_ranked_stats[0]["leaguePoints"])

top_right_data["MASTERY"] = "MASTERY POINTS: {}K\n".format(round(mastery_points/1000, 1))
top_right_data["KDA"] = "KDA: {}\n".format(kda)
top_right_data["KP"] = "KP: {}%\n".format(kp)
top_right_data["CS/MIN"] = "CS/MIN: {}".format(cspm)
    
with open("top_left.txt", "w") as top_left, open("top_right.txt", "w") as top_right:
    top_left.write(top_left_data["WR"])
    top_left.write(top_left_data["WR20G"])
    top_left.write(top_left_data["RANK"])
    top_left.write(top_left_data["LP"])
    
    top_right.write(top_right_data["MASTERY"])
    top_right.write(top_right_data["KDA"])
    top_right.write(top_right_data["KP"])
    top_right.write(top_right_data["CS/MIN"])