## Optimizations/organization + readme update coming soon

# LOLStatTracker
The profile stat tracker is a script to read the stats from a league profile. The data will be written to a text file and (in my case) the file will be displayed on an OBS scene (example: https://prnt.sc/_5McJsByVSsA). This will be used in a YouTube series I will be starting to document my progress in learning how to play Samira. project is in the very early stages of planning.

DISCLAIMER: I am by no means a professional programmer/scripter/what have you. This project is being done in my free time and for fun.

## How to Use
### API KEY
First you want to make sure you have a developer account and access to an API token.

It should look something like this:
> RGAPI-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

When you have an API token you can now access the data from the API. Unless you apply for a product you will have to refresh the code every 24 hours.

### Setting up Python
To use this script, I can only guarantee this works on Python 3.11 or newer. You will also need to install [Riot-Watcher](https://github.com/pseudonym117/Riot-Watcher).

### Configuration File
The repository should generate a config file for you. If not, run the python script once and it should appear. There will be an error, that is supposed to happen. Enter your API key, the region you are playing on, your summoner name, how many games from the match history you want to search from (max 100), and the ID of your champion. There is a table in the [Riot developer page](https://developer.riotgames.com/docs/lol) for regions. I recommend copy and pasting your summoner name from your [op.gg](https://www.op.gg/) page in case there are special characters. The champion ID can be found in the [Data Dragon json file](https://ddragon.leagueoflegends.com/cdn/dragontail-13.5.1.tgz)

An example of a config file:
```json
{
	"APIKEY" : "RGAPI-ff68ed49-6478-40c0-9cb8-113f36081163",
	"REGION" : "NA1",
	"SUM_NAME" : "Shad0CS",
	"NUM_GAMES" : 5,
	"CHAMPIONID" : 360 
}
```
This API key will not work if you try it.

### Using the Script
Once you have an API key and the config set, you are ready to get an output file(s), for my setup I wanted two different files to display on an obs scene (shown above). If you want to output to a separate file, add another line near the start of the main.py file:

> {file identifier} = open("{file name}.{format}", "w")

The file identifier must be a unique name from the rest of the file. The file name is whatever you want the file to be named. The format (usually ".txt") is the format of the file you want.

For every new file you make, you must close it at the end of the script:

> {file identifier}.close()

If you want to change which file each piece of data is written to, change the names of the output at the end of the main.py file:

> top_right.write("output")

If I want to output to the left side, I change the start to "top_left.":

> top_left.write("output")
