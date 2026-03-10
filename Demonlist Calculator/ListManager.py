import base64
import json
import os
import time

import requests
from colorama import Fore, Back , Style

white = Fore.WHITE + Style.BRIGHT
accent = Fore.LIGHTRED_EX + Style.BRIGHT
green = Fore.LIGHTGREEN_EX + Style.BRIGHT
red = Fore.LIGHTRED_EX + Style.BRIGHT
grey = Fore.LIGHTBLACK_EX
prefix = f"{accent}listmanager@{os.getlogin().lower()}{white}:~$ "

completed = Back.GREEN + " " + Back.RESET + " "
failed = Back.LIGHTRED_EX + " " + Back.RESET + " "

helpText = """
help, ?              $ show this help menu
quit, q, exit        $ exit the application
clear, cls           $ clear the terminal
addlevel, add        $ add level to list file
editlevel, edit      $ edit/replace level in list file
viewlist, view, list $ display list file
submit               $ submit a list record
calculate, calc      $ calculate records and list points
user                 $ show user information
"""

def submitRecord(level, player):
    # Read current file data
    with open(file) as f:
        try: fileData = json.load(f)
        except: fileData = []

    # Append level data
    for x in fileData:
        if (str(x['name']).lower() == level.lower()):
            victors = x['victors']
            victors.append(player)

    with open(file, mode='w') as f:
        f.write(json.dumps(fileData, indent=2))

def getPlace(x):
    return x['place']

def addLevel(file, name, place, creators, verifier, video, id):
    # Combine level data
    levelData = {"name": name, "place": place, "id": id, "creators": creators, "verifier": verifier, "video": video, "victors" : []}

    # Read current file data
    with open(file) as f:
        try: fileData = json.load(f)
        except: fileData = []

    # Append level data
    for x in fileData:
        if int(x['place']) >= int(place):
            x['place'] = str(int(x['place']) + 1)
    fileData.append(levelData)
    fileData.sort(key=lambda x: int(x['place']))

    with open(file, mode='w') as f:
        f.write(json.dumps(fileData, indent=2))

def moveLevel(file, level, type, count):
    type = type.lower()
    place = ""
    with open(file) as f:
        try: fileData = json.load(f)
        except: fileData = []

    for x in fileData:
        if (str(x['name']).lower() == level.lower()): place = x['place']

    if (type != 'none'):
        for r in range(int(count)):
            for x in fileData:
                if (type == 'up'):
                    if int(x['place']) <= int(place) - 1:
                        x['place'] = str(int(x['place']) + 1)
                    if (str(x['name']).lower() == level.lower()): x['place'] = str(int(place) - 1)
                else:
                    if int(x['place']) <= int(place) + 1:
                        x['place'] = str(int(x['place']) - 1)
                    if (str(x['name']).lower() == level.lower()): x['place'] = str(int(place) + 1)

    fileData.sort(key=lambda x: int(x['place']))
    with open(file, mode='w') as f:
        f.write(json.dumps(fileData, indent=2))


def delLevel(file, level):
    # Read current file data
    with open(file) as f:
        try: fileData = json.load(f)
        except: fileData = []

    # Append level data
    for x in fileData:
        if (str(x['name']).lower() == level.lower() or str(x['place']).lower() == level.lower()): fileData.remove(x)

    with open(file, mode='w') as f:
        f.write(json.dumps(fileData, indent=2))

def viewList():
    # I love nested if statements
    i = 1
    try:
        with open(file, "r") as f:
            fileData = json.load(f)
            while i <= len(fileData):
                for x in fileData:
                    if x['place'] == str(i): print(f"#{x['place']} {x['name']} | ID: {x['id']} | By {x['creators']} | Verified by {x['verifier']} | Video: {x['video']}")
                i+=1
    except:
        print(f"{failed}File is missing or incorrectly formatted")

def addBadge(player, badge):
    try:
        with open('./data/leaderboard.json', "r") as f:
            fileData = json.load(f)
            for x in fileData:
                if player == x['player']:
                    badges = x['badges']
                    if not badge in badges:
                        badges.append(badge)
                        print(completed + "Awarded " + badge + " badge to " + player + ".")
                    else: print(failed + "Player already has badge.")
        with open('./data/leaderboard.json', mode='w') as f:
            f.write(json.dumps(fileData, indent=2))
    except:
        print(f"{failed}An error occurred.")

def commandCalculate():
    # This might be the worst code ever written
    completions = []
    with open(file, "r") as f:
        fileData = json.load(f)
        for x in fileData:
            levelName = x['name']
            levelPlace = x['place']
            for x in x['victors']:
                points = round(250 / ((int(levelPlace) + 4) * 0.2))
                completions.append({"player" : x, "level" : levelName, "place" : levelPlace, "points" : points})
        for x in completions:
            print(f"{x['player']} beat {x['level']} at place {x['place']} for {x['points']} list points")
        with open('./data/records.json', mode='w') as f:
            f.write(json.dumps(completions, indent=2))
        leaderboard = []
        if os.path.isfile('./data/leaderboard.json'):
            with open('./data/leaderboard.json', "r") as f:
                lbData = json.load(f)
        for x in completions:
            if os.path.isfile('./data/leaderboard.json'):
                for d in lbData:
                    if d['player'] == x['player']:
                        badges = d['badges']
            else:
                badges = []
            if not {"player": x['player'], "points": 0, "badges": badges} in leaderboard: leaderboard.append({"player": x['player'], "points": 0, "badges": badges})
        for l in leaderboard:
            for x in completions:
                l['points'] = sum(int(x['points']) for x in completions if x['player'] == l['player'])
        sorted_leaderboard = sorted(leaderboard, key=lambda x: x['points'], reverse=True)
        with open('./data/leaderboard.json', mode='w') as f:
            f.write(json.dumps(sorted_leaderboard, indent=2))
        i = 0
        for x in sorted_leaderboard:
            i = i + 1
            print(f"#{i} {x['player']} | List Points: {x['points']}")
        print(completed + "Calculated list points.")

def commandSubmit():
    level = input(f"{grey}(1/2) {white}Enter level name $ ")
    player = input(f"{grey}(2/2) {white}Enter player name $ ")
    print()
    final = input(f'{grey}Submit {player}s record to list? (Y/N) ')
    if final.lower() == "y": submitRecord(level, player)
    else: pass

def commandMoveLevel():
    level = input(f"{grey}{white}(1/3) Enter level name $ ")
    newPlace = input(f"{grey}(2/3) {white}Move {level} up or down? $ ")
    count = input(f"{grey}(3/3) {white}How many spots? $ ")
    final = input(f'{grey}Move "{level}" to {newPlace}? (Y/N) ')
    if final.lower() == "y": moveLevel(file, level, newPlace, count)
    else: pass

def commandEditLevel():
    print("Welcome to the Edit Level Wizard!")
    print(f"{grey}Follow the steps to edit a level in the list file.")
    print()
    oldlevel = input(f"{grey}(1/7) {white}Enter old level name or position $ ")
    name = input(f"{grey}(2/7) {white}Enter level name $ ")
    place = input(f"{grey}(3/7) {white}Enter level position $ ")
    id = input(f"{grey}(4/7) {white}Enter level ID $ ")
    creators = input(f"{grey}(5/7) {white}Enter creator(s) $ ")
    verifier = input(f"{grey}(6/7) {white}Enter verifier $ ")
    video = input(f"{grey}(7/7) {white}Enter verification video url $ ")
    print()
    final = input(f'{grey}Overwrite "{oldlevel}" with "{name}"? (Y/N) ')
    if final.lower() == "y":
        delLevel(file, oldlevel)
        addLevel(file, name, place, creators, verifier, video, id)
    else: pass

def commandAddLevel():
    print("Welcome to the Add Level Wizard!")
    print(f"{grey}Follow the steps to add a level to the list file.")
    print()
    name = input(f"{grey}(1/6) {white}Enter level name $ ")
    place = input(f"{grey}(2/6) {white}Enter level position $ ")
    id = input(f"{grey}(3/6) {white}Enter level ID $ ")
    creators = input(f"{grey}(4/6) {white}Enter creator(s) $ ")
    verifier = input(f"{grey}(5/6) {white}Enter verifier $ ")
    video = input(f"{grey}(6/6) {white}Enter verification video url $ ")
    print()
    final = input(f"{grey}Add level to list? (Y/N) ")
    if final.lower() == "y":
        addLevel(file, name, place, creators, verifier, video, id)
        print(completed + white + f'Added "{name}" to the list, use the "calc" command to recalculate list points.')
    else: pass

def commandAddBadge():
    player = input(f"{grey}(1/2) {white}Enter player name $ ")
    badge = input(f"{grey}(2/2) {white}Enter badge name $ ")
    print()
    final = input(f'{grey}Award "{badge}" badge to {player}? (Y/N) ')
    if final.lower() == "y": addBadge(player, badge)
    else: pass

def commandManager(command):
    if command.lower() == "help" or command == "?": print(helpText)
    elif command.lower() == "q" or command.lower() == "quit" or command.lower() == "exit": quit(0)
    elif command.lower() == "cls" or command.lower() == "clear": os.system("cls")
    elif command.lower() == "add" or command.lower() == "addlevel": commandAddLevel()
    elif command.lower() == "edit" or command.lower() == "editlevel": commandEditLevel()
    elif command.lower() == "move" or command.lower() == "movelevel": print(failed + "Command is disabled")
    elif command.lower() == "view" or command.lower() == "viewlist" or command.lower() == "list": viewList()
    elif command.lower() == "badge" or command.lower() == "addbadge": commandAddBadge()
    elif command.lower() == "submit": commandSubmit()
    elif command.lower() == "calc" or command.lower() == "calculate": commandCalculate()
    elif command.lower() == "user": print(f"{grey}User:{white} {user} ({os.getlogin()})")
    else: print(f"{failed}Command not found")

version = 2.1
if not os.path.isdir("./data/"): os.system("mkdir .\\data\\")
file = '.\\data\\list.json'
os.system(f"title List Manager {version} - Enterprise Edition")
os.system(f"echo. >> {file}")

# cloudflare killed pastebin auth
auth = True

print("Authenticating...")
mods = requests.get("https://classidash.com/demonlist/adminKeys").text.splitlines()

for x in mods:
    try:
        decodedKey = str(base64.b64decode(x.split(":")[0] + "="))[1:].strip("'")
        if decodedKey == os.getlogin() + "," + os.environ['COMPUTERNAME']:
            auth = True
            key = x.split(':')[0]
            user = x.split(':')[1]
            print(completed + f"Authenticated! Welcome {user}")
    except:
        auth

if auth == False:
    print(failed + "Authentication Failed. Exiting...")
    time.sleep(3)
    quit("Authentication Failed.")

if auth:
    print(helpText)
    while True:
        inp = input(prefix)
        commandManager(inp)
