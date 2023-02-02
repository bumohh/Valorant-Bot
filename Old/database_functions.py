import sqlite3
import logging

#database functions
def initDatabase(address : str):
    connection = sqlite3.connect(address)
    return connection

def saveDatabaseChanges(connection : sqlite3.Connection):
    connection.commit()
    
def deinitDatabase(connection : sqlite3.Connection):
    connection.close()
    
def initTable(connection : sqlite3.Cursor):
    connection.execute('''CREATE TABLE IF NOT EXISTS valorant_players (player_region TEXT, player_name TEXT, player_tag TEXT, player_cur_rank TEXT, player_puuid INTEGER, discord_id INTEGER)''')
    
def fetchUsersFromDB():
    try:
        logging.debug("starting fetchusersfromdb function")
        connection = initDatabase("database.db")
        db = connection.cursor()

        db.execute("SELECT * FROM valorant_players ORDER BY discord_id")
        data_list=db.fetchall()
        deinitDatabase(connection)
        return data_list
    except:
        return []
    
def fetchUserUsingpuuid(connection : sqlite3.Connection, player_puuid) :
    #0region #1name #2tag #3rank #4puuid #5discord_id
    connection.execute("SELECT * FROM valorant_players WHERE player_puuid=?", (player_puuid,))
    data = connection.fetchone()
    return data

def fetchUserUsingDiscordAndpuuid(connection : sqlite3.Connection, discord_id, player_puuid):
    #0region #1name #2tag #3rank #4puuid #5discord_id
    connection.execute("SELECT * FROM valorant_players WHERE discord_id=? AND player_puuid=?", (discord_id, player_puuid,))
    data = connection.fetchone()
    return data

def updateUserRankWith(connection : sqlite3.Connection, discord_id, player_puuid, player_cur_rank):
    connection.execute("UPDATE valorant_players SET player_cur_rank=? WHERE discord_id=? AND player_puuid=?", (player_cur_rank, discord_id, player_puuid,))
    
def insertUser(connection : sqlite3.Connection, region, player_name, player_tag, player_cur_rank, player_puuid, discord_id):
    connection.execute("INSERT INTO valorant_players (player_region, player_name, player_tag, player_cur_rank, player_puuid, discord_id) VALUES (?,?,?,?,?,?)", (region, player_name, player_tag, player_cur_rank, player_puuid, discord_id,))