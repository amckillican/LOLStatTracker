from riotwatcher import LolWatcher, ApiError
import json
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# importing the config file
config_file = open("config.json")
config_info = json.load(config_file)

# set from config
lol_watcher = LolWatcher(config_info["APIKEY"])
my_region = config_info["REGION"]
sum_name = config_info["SUM_NAME"]
num_games = config_info["NUM_GAMES"]
champ_id = config_info["CHAMPIONID"] # can be found in data dragon json file

# output files for obs scene
top_left = open("top_left.txt", "w")
top_right = open("top_right.txt", "w")

# desired summoner profile data
me = lol_watcher.summoner.by_name(my_region, sum_name)

# all objects are returned (by default) as a dict
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
    
# checking overall wr, kda, kp, and cs/min
wins = my_ranked_stats[0]["wins"]
total_games_played = wins + my_ranked_stats[0]["losses"]

# checking wr in last 20 games
matchlist = lol_watcher.match.matchlist_by_puuid("NA1", me["puuid"], 0, num_games, type="ranked")

# variables
kills = 0
assists = 0
blue_side_kills = 0
red_side_kills = 0
total_kills = 0
my_team = 0
deaths = 0
win20g = 0
loss20g = 0
cs = 0
gametime = 0
kp = 0
kda = 0
wr20g = 0
cspm = 0

# loop through all matches in the match history
for index, matches in enumerate(matchlist):
    selected_match = lol_watcher.match.by_id(my_region, matches)["info"]
    participants = selected_match["participants"]
    # sum of total game time
    gametime += selected_match["gameDuration"]
    
    # loop through all the people in a match
    for people in participants:
        # add up all blue side kills
        if people["teamId"] == 100: blue_side_kills += people["kills"]
        # add up all red side kills
        if people["teamId"] == 200: red_side_kills += people["kills"]
        # check summoner name
        if people["summonerName"] == sum_name:
            # store side of desired summoner
            my_team = people["teamId"]
            # sum of summoner's kills
            kills += people["kills"]
            assists += people["assists"]
            # sum of summoner's deaths
            deaths += people["deaths"]
            # sum of summoner's cs
            cs += people["totalMinionsKilled"] + people["neutralMinionsKilled"]
            # check first 20 games for winrate
            if index < 20:
                if people["win"] == True: win20g += 1
                if people["win"] == False: loss20g += 1
                
    # sum of summoner's team's kills
    if my_team == 100: total_kills += blue_side_kills
    if my_team == 200: total_kills += red_side_kills
    # resetting the team kills if desired summoner switches teams
    blue_side_kills = 0
    red_side_kills = 0
    my_team = 0
            
# calculations
kp = round(100*(kills + assists)/total_kills)
kda = round((kills + assists)/deaths, 2)
wr20g = round(100*win20g/(loss20g+win20g))
cspm = round(cs/(gametime/60), 2)

# finding champ mastery points
mastery_points = lol_watcher.champion_mastery.by_summoner_by_champion(my_region, me["id"], champ_id)["championPoints"]

# output
top_left.write("Overall WR: {}%\n".format(round(wins / total_games_played*100)))
top_left.write("WR (20 Games): {}%\n".format(wr20g))
top_left.write("Rank: {} {}\n".format(my_ranked_stats[0]["tier"], my_ranked_stats[0]["rank"]))
top_left.write("LP: {}".format(my_ranked_stats[0]["leaguePoints"]))
top_right.write("MASTERY POINTS: {}K\n".format(round(mastery_points/1000, 1)))
top_right.write("KDA: {}\n".format(kda))
top_right.write("KP: {}%\n".format(kp))
top_right.write("CS/MIN: {}".format(cspm))

# closing files
top_right.close()
top_left.close()