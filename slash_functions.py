#External
import requests
import sqlite3
import json
#Internal
import log
from variables import *

# Function that calls the api and returns rank and puuid
def InitialValApiCall(region, ign, tag):
    log.debug("InitialValApiCall in slash_functions.py triggered.")
    headers = {"Authorization": henrikdev_token}
    endpoint = f"https://api.henrikdev.xyz/valorant/v2/mmr/{region}/{ign}/{tag}"
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            log.debug("InitialValApiCall in slash_functions.py finished incorrectly first error.")
            raise ValueError(data["error"])
        log.debug("InitialValApiCall in slash_functions.py finished correctly.")
        return data["data"]["current_data"]["currenttierpatched"],data["data"]["puuid"],data["data"]["current_data"]["images"]["large"],data["data"]["current_data"]["elo"],data["data"]["current_data"]["ranking_in_tier"]
          
    except requests.exceptions.RequestException as e:
        log.debug("InitialValApiCall in slash_functions.py finished incorrectly second error.")
        raise ValueError("Error connecting to API: " + str(e))
    except ValueError as e:
        log.debug("InitialValApiCall in slash_functions.py finished incorrectly third error.")
        raise ValueError(str(e))

def bannerValApiCall(ign, tag):
    
    log.debug("bannerValApiCall in slash_functions.py triggered.")
    headers = {"Authorization": henrikdev_token}
    endpoint = f"https://api.henrikdev.xyz/valorant/v1/account/{ign}/{tag}?force=true"
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            log.debug("bannerValApiCall in slash_functions.py finished incorrectly first error.")
            raise ValueError(data["error"])
        log.debug("bannerValApiCall in slash_functions.py finished correctly.")
        return data["data"]["card"]["wide"], data["data"]["card"]["id"]
          
    except requests.exceptions.RequestException as e:
        log.debug("bannerValApiCall in slash_functions.py finished incorrectly second error.")
        raise ValueError("Error connecting to API: " + str(e))
    except ValueError as e:
        log.debug("bannerValApiCall in slash_functions.py finished incorrectly third error.")
        raise ValueError(str(e))


# Function to check if account has already been added to the user
def duplicateCheck(puuid):
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM valorant_players WHERE puuid=?", (puuid,))
    rows = cursor.fetchall()
    cursor.close()
    connect.close()

    if len(rows) == 0:
        return False
    else:
        return True

# Function to make the first save to the database initiated from the slash command    
def initialDatabaseSave(discord_id, region, ign, tag, rank_full, puuid, verification_status):
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM valorant_players WHERE discord_id=? AND puuid=?", (discord_id, puuid,))
    result = cursor.fetchone()
    if result:
        cursor.execute("UPDATE valorant_players SET region=?, ign=?, tag=?, rank_full=?, verification_status=? WHERE discord_id=? AND puuid=?", (region, ign, tag, rank_full, discord_id, puuid, verification_status,))
    else:
        cursor.execute("""INSERT INTO valorant_players (discord_id, region, ign, tag, rank_full, puuid, verification_status)VALUES (?,?,?,?,?,?,?)""", (discord_id, region, ign, tag, rank_full, puuid, verification_status))
    connect.commit()
    cursor.close()
    connect.close()

def getRowsByDiscord_id(discord_id):
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM valorant_players WHERE discord_id=?", (discord_id,))
    rows = cursor.fetchall()
    cursor.close()
    connect.close()
    return rows

def removeValorantAccountfromDatabase(discord_id):
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute("DELETE FROM valorant_players WHERE discord_id=?", (discord_id,))
    connect.commit()
    cursor.close()
    connect.close()

def updateVerifiedStatusInDatabase(discord_id, verification_status):
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    rows = cursor.execute("SELECT * FROM valorant_players WHERE discord_id=?", (discord_id,)).fetchall()
    for row in rows:
        cursor.execute("UPDATE valorant_players SET verification_status=? WHERE discord_id=?", (verification_status, discord_id))
    connect.commit()
    cursor.close()
    connect.close()



#updateVerifiedStatusInDatabase("184886547693174785","bb532c7f-01b8-5385-9658-b773a2174182","Verified")

def updateBannerVerificationStepOneDatabase(discord_id, ign, tag, step_1_banner, start_time):
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute('''SELECT discord_id FROM val_verification WHERE discord_id = ? AND ign = ? AND tag = ?''', (discord_id, ign, tag))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('''INSERT INTO val_verification(discord_id, ign, tag, step_1_banner, start_time)VALUES (?, ?, ?, ?, ?)''', (discord_id, ign, tag, step_1_banner, start_time))
    connect.commit()
    connect.close()

def updateBannerVerificationStepTwoDatabase(discord_id, ign, tag, step_2_banner):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE val_verification SET step_2_banner = ? WHERE discord_id = ? AND ign = ? AND tag = ?''', (step_2_banner, discord_id, ign, tag))
    conn.commit()
    conn.close()

def getBannerVerificationDataFromDatabase(discord_id, ign, tag):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT step_1_banner, start_time, step_2_banner FROM val_verification WHERE discord_id = ? AND ign = ? AND tag = ?''', (discord_id, ign, tag))
    data = cursor.fetchone()
    conn.close()
    return data

def removeVerificationDataFromDatabase(discord_id, ign, tag):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f"DELETE FROM val_verification WHERE discord_id='{discord_id}' AND ign='{ign}' AND tag='{tag}'")
    conn.commit()
    conn.close()



# Function that calls the api and returns rank and puuid
def testValApiCall(region, ign, tag):
    log.debug("InitialValApiCall in slash_functions.py triggered.")
    headers = {"Authorization": henrikdev_token}
    endpoint = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{ign}/{tag}"
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            log.debug("InitialValApiCall in slash_functions.py finished incorrectly first error.")
            raise ValueError(data["error"])
        log.debug("InitialValApiCall in slash_functions.py finished correctly.")
        return data["data"][""]
          
    except requests.exceptions.RequestException as e:
        log.debug("InitialValApiCall in slash_functions.py finished incorrectly second error.")
        raise ValueError("Error connecting to API: " + str(e))
    except ValueError as e:
        log.debug("InitialValApiCall in slash_functions.py finished incorrectly third error.")
        raise ValueError(str(e))
    

# This function works tried changing the request to match the format of the other functions and the math changed (????) and spat out the wrong calcs why idk you tell me beware you have been warned
def getValMatchDataApiCall(region, ign, tag):
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{ign}/{tag}"

    response = requests.get(url)
    match_data = []

    if response.status_code == 200:
        data = json.loads(response.text)

        match = 0
        while match < 5:
            if data["data"][match]["metadata"]["mode"] == "Custom Game":
                match = match + 1
            else:
                player = 0
                play_name = "nhm ln"
                player_list = data["data"][match]["players"]["all_players"]
                while player < 10:
                    player_list = data["data"][match]["players"]["all_players"][player]["name"]
                    if player_list == play_name:
                        break
                    player = player + 1
                team =     str(data["data"][match]["players"]["all_players"][player]["team"]).lower()
                won =       data["data"][match]["teams"][team]["has_won"]
                score =     data["data"][match]["players"]["all_players"][player]["stats"]["score"]
                kills =     data["data"][match]["players"]["all_players"][player]["stats"]["kills"]
                deaths =    data["data"][match]["players"]["all_players"][player]["stats"]["deaths"]
                assists =   data["data"][match]["players"]["all_players"][player]["stats"]["assists"]
                bodyshots = data["data"][match]["players"]["all_players"][player]["stats"]["bodyshots"]
                headshots = data["data"][match]["players"]["all_players"][player]["stats"]["headshots"]
                legshots =  data["data"][match]["players"]["all_players"][player]["stats"]["legshots"]

                match_data.append({'Match': match+1, 'Score': score, 'Kills': kills, 'Deaths': deaths,
                                'Assists': assists, 'Bodyshots': bodyshots, 'Headshots': headshots,
                                'Legshots': legshots, "Win": won})
                match = match + 1
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
    total_kills = 0
    total_assists = 0
    total_deaths = 0
    headshots = 0
    bodyshots = 0
    legshots = 0
    for match in match_data:
        total_kills += match['Kills']
        total_assists += match['Assists']
        total_deaths += match['Deaths']

    average_kda = round(((total_kills + total_assists) / total_deaths if total_deaths != 0 else 0),2)


    for match in match_data:
        headshots += match['Headshots']
        bodyshots += match['Bodyshots']
        legshots += match['Legshots']

    avg_headshots = headshots / len(data)
    avg_bodyshots = bodyshots / len(data)
    avg_legshots = legshots / len(data)

    wins = 0
    for match in match_data:
        if match['Win']:
            wins += 1

    win_rate = (wins / len(match_data))*100
    return average_kda,avg_headshots,avg_bodyshots,avg_legshots,win_rate