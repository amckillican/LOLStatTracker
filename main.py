from riotwatcher import LolWatcher, ApiError
import json
import os

# set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# importing the config file
with open("config.json") as config_file:
    config_info = json.load(config_file)

    # loading config info
    lol_watcher = LolWatcher(config_info["APIKEY"])
    my_region = config_info["REGION"]
    sum_name = config_info["SUM_NAME"]
    num_games = config_info["NUM_GAMES"]
    champ_id = config_info["CHAMPIONID"] # can be found in data dragon json file

# pulling profile and ranked info from api
me = lol_watcher.summoner.by_name(my_region, sum_name)
my_ranked_stats = lol_watcher.league.by_summoner(my_region, me['id'])

# checking for api errors
try:
    response = lol_watcher.summoner.by_name(my_region, sum_name)
except ApiError as err:
    if err.response.status_code == 429:
        print('We should retry in {} seconds.'.format(
            err.headers['Retry-After']))
        print('this retry-after is handled by default by the RiotWatcher library')
        print('future requests wait until the retry-after time passes')
    elif err.response.status_code == 404:
        print('Summoner name not found, check the config file.')
    else:
        raise

# getting total wins and total games played
wins = my_ranked_stats[0]["wins"]
total_games_played = wins + my_ranked_stats[0]["losses"]

# getting mastery points from api
mastery_points = lol_watcher.champion_mastery.by_summoner_by_champion(my_region, me["id"], champ_id)["championPoints"]

# opening the match data file
with open("match_data.json") as match_json_file:
    # save the data if the file has any
    if os.path.getsize("match_data.json") != 0:
        match_json_data = json.load(match_json_file)
    else:
        # create a dictionary to save the data
        match_json_data = {}

# reading the match data
matchlist = lol_watcher.match.matchlist_by_puuid("NA1", me["puuid"], 0, num_games, type="ranked")

# checking if the match is already in the list
for index, matches in enumerate(matchlist):
    existing = False
    for existing_matches in match_json_data:
        if matches == existing_matches:
            existing = True

    # saving the data for each match
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

        # save the match length
        match_json_data[matches]["gametime"] = selected_match["gameDuration"]

        # read the players in the selected match
        selected_match = lol_watcher.match.by_id(my_region, matches)["info"]
        participants = selected_match["participants"]

        # iterate through each player in the match
        for people in participants:
            # finding total team kills per side
            if people["teamId"] == 100:
                blue_side_kills += people["kills"]
            if people["teamId"] == 200:
                red_side_kills += people["kills"]
            
            # checking for desired summoner
            if people["summonerName"] == sum_name:
                # saving their data for that match
                my_team = people["teamId"]
                kills += people["kills"]
                assists += people["assists"]
                deaths += people["deaths"]
                cs += people["totalMinionsKilled"] + \
                    people["neutralMinionsKilled"]
                if people["win"] == True:
                    match_json_data[matches]["win"] = True
                else:
                    match_json_data[matches]["win"] = False

        # finding total team kills for the desired summoner's team
        if my_team == 100:
            total_kills += blue_side_kills
        if my_team == 200:
            total_kills += red_side_kills

        # writing the desired summoner's match data
        match_json_data[matches]["kills"] = kills
        match_json_data[matches]["deaths"] = deaths
        match_json_data[matches]["assists"] = assists
        match_json_data[matches]["cs"] = cs
        match_json_data[matches]["total_kills"] = total_kills
    else: break

# write the match info to the file
with open("match_data.json", "w") as match_json_file:
    match_json_file.write(json.dumps(match_json_data, indent=2))

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

# loop through each match in the finalized data
for index, matches in enumerate(match_json_data):
    # check first 20 games for winrate
    if index < 20:
        # finding 20 game winrate
        if match_json_data[matches]["win"] == True:
            win20g += 1
        if match_json_data[matches]["win"] == False:
            loss20g += 1
    # sum of desired summoner's stats
    sum_gametime += match_json_data[matches]["gametime"]
    sum_kills += match_json_data[matches]["kills"]
    sum_deaths += match_json_data[matches]["deaths"]
    sum_assists += match_json_data[matches]["assists"]
    sum_cs += match_json_data[matches]["cs"]
    sum_total_kills += match_json_data[matches]["total_kills"]

# calculations for desired summoner's stats
kp = round(100*(sum_kills + sum_assists)/sum_total_kills)
kda = round((sum_kills + sum_assists)/sum_deaths, 2)
wr20g = round(100*win20g/(loss20g+win20g))
cspm = round(sum_cs/(sum_gametime/60), 2)

# writing final data to files to be read by obs
with open("top_left.txt", "w") as top_left, open("top_right.txt", "w") as top_right:
    top_left.write("Overall WR: {}%\n".format(round(wins / total_games_played*100)))
    top_left.write("WR (20 Games): {}%\n".format(round(wr20g)))
    top_left.write("Rank: {} {}\n".format(my_ranked_stats[0]["tier"], my_ranked_stats[0]["rank"]))
    top_left.write("LP: {}".format(my_ranked_stats[0]["leaguePoints"]))

    top_right.write("MASTERY POINTS: {}K\n".format(round(mastery_points/1000, 1)))
    top_right.write("KDA: {}\n".format(kda))
    top_right.write("KP: {}%\n".format(kp))
    top_right.write("CS/MIN: {}".format(cspm))
