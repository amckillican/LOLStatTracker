# LOLStatTracker
The profile stat tracker is a script to read the stats from a league profile. The data will be written to a text file and (in my case) the file will be displayed on an OBS scene (example: https://prnt.sc/_5McJsByVSsA). This will be used in a YouTube series I will be starting to document my progress in learning how to play Samira. project is in the very early stages of planning.

DISCLAIMER: I am by no means a professional programmer/scripter/what have you. This project is being done in my free time and for fun.

## How to Use
### API KEY
First you want to make sure you have a developer account and access to an api token.

It should look something like this:
> RGAPI-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

When you have an api token you can now access the data from the api. Unless you apply for a product you will have to refresh the code every 24 hours.

### Configuration File
The repository should generate a config file for you. If not, run the python script once and it should appear. There will be an error, that is supposed to happen.

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
This api key will not work if you try it.

### Using the Script
Once you have an api key and the config set, you are ready to get an output file(s), for my setup I wanted two different files to display on an obs scene (shown above). If you want to output to a separate file, add another line near the start of the main.py file:

> {file identifier} = open("{file name}.{format}", "w")

The file identifier must be a unique name from the rest of the file. The file name is whatever you want the file to be named. The format (usually ".txt") is the format of the file you want.

For every new file you make, you must close it at the end of the script:

> {file identifier}.close()

If you want to change which file each piece of data is written to, change the names of the output at the end of the main.py file:

> top_right.write("output")

If I want to output to the left side, I change the start to "top_left.":

> top_left.write("output")