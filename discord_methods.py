import discord
import requests
import database_functions as database
import logging
import interactions
import config_methods as config
import network_handler as network
import asyncio


#discord methods
def save_data(data : requests.Response.json, discord_id: int, region: str):
    logging.debug("starting save data function")
    player_name = data["data"]["name"]
    player_tag = data["data"]["tag"]
    player_cur_rank = data["data"]["current_data"]["currenttierpatched"]
    player_puuid = data["data"]["puuid"]
    
    connection = database.initDatabase("database.db")
    db = connection.cursor()
    database.initTable(db)
    
    data = database.fetchUserUsingpuuid(db, player_puuid)
    
    if data:
        if data[4]!=discord_id:
            logging.info("User is already registered under another discord id, try again.")
            database.deinitDatabase(connection)
            return
    
    data = database.fetchUserUsingDiscordAndpuuid(db, discord_id, player_puuid)
    
    if data: 
        if data[4]==discord_id:
            logging.info("updating for existing discord user")
            database.updateUserRankWith(db, discord_id, player_puuid, player_cur_rank)
        else :
            logging.info("inserting non-existing discord user")
            database.insertUser(db,region, player_name, player_tag, player_cur_rank, player_puuid, discord_id)
    else:
        logging.info("inserting non-existing discord user because data null")
        database.insertUser(db,region, player_name, player_tag, player_cur_rank, player_puuid, discord_id)
        
    database.saveDatabaseChanges(connection)
    database.deinitDatabase(connection)
    
def updateDBRank(player_cur_rank, discord_id, player_puuid):
    logging.debug("starting updateDBrank function")
    connection = database.initDatabase("database.db")
    db = connection.cursor()
    database.updateUserRankWith(db,discord_id, player_puuid, player_cur_rank)
    database.saveDatabaseChanges(connection)
    database.deinitDatabase(connection)
    
async def updater():
    logging.debug("starting updater function")
    logging.info("starting updates")
    users = database.fetchUsersFromDB()
    config.writeGlobalVariable("count",str(users.__len__()))
    count = users.__len__()
    logging.debug("count = users.__len__() is equal to " + str(count))
    #await asyncio.sleep(60)
    while(int(config.readGlobalVariable("count")) == count):
        await asyncio.sleep(150)
        index = int(config.readGlobalVariable("index"))
        count = int(config.readGlobalVariable("count"))
        if not (index > count):
            updateUsers(index, users)
        else : 
            pass

    
def updateUsers(index : int, users : list(tuple())):
    try:
        #0region #1name #2tag #3rank #4puuid #5discord_id
        logging.info("starting update users function")
        for i in range(5): 
            user = users[int(config.readGlobalVariable("index"))]
            logging.info("fetching data for user in region " + str(user[0]) + ", name and tag as " + str(user[1]) +" #"+ str(user[2]))
            data = network.fetchDataForUser(user[0], user[1], user[2])
            #logging.info("data "+ str(data))
            updateDBRank(data["data"]["current_data"]["currenttierpatched"], user[5], user[4])
            
            count = int(config.readGlobalVariable("count"))
            i = int(config.readGlobalVariable("index"))
            if i == count-1 :
                config.writeGlobalVariable("index", "0")
            else : 
                config.writeGlobalVariable("index", str(i + 1))
            logging.info("going to next user")
    except:
        pass
    
def updateDiscordRank(ctx: interactions.CommandContext):
            
    pass
    