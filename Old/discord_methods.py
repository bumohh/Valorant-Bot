import discord
import requests
import database_functions as database
import logging
import interactions
import config_methods as config
import network_handler as network
import asyncio


#discord methods
def save_data(ctx : interactions.CommandContext, data : requests.Response.json, region: str):
    logging.debug("starting save data function")
    player_name = data["data"]["name"]
    player_tag = data["data"]["tag"]
    player_cur_rank = data["data"]["current_data"]["currenttierpatched"]
    player_puuid = data["data"]["puuid"]
    discord_id = int(ctx.author.id)
    
    connection = database.initDatabase("database.db")
    db = connection.cursor()
    database.initTable(db)
    
    data = database.fetchUserUsingpuuid(db, player_puuid)
    
    if data:
        if data[-1]!=discord_id:
            logging.info("User is already registered under another discord id, try again.")
            database.deinitDatabase(connection)
            return
    
    data = database.fetchUserUsingDiscordAndpuuid(db, discord_id, player_puuid)
    
    if data: 
        if data[-1]==discord_id:
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
    
async def updateDiscordRank(ctx: interactions.CommandContext, data : requests.Response.json):
    
    logging.info("updating discord rank")
    
    player_name = data["data"]["name"]
    player_tag = data["data"]["tag"]
    player_cur_rank = data["data"]["current_data"]["currenttierpatched"]
    if player_cur_rank == None :
            rank_name = "Unranked"
            player_cur_rank = "Unranked"
    else:
        rank_name = ' '.join(player_cur_rank.split()[:-1])
        
    await ctx.send(f"Player {player_name} #{player_tag}'s role has been updated to {player_cur_rank}.")
    
    ranks = {
        "Iron": discord.Colour.from_rgb(139, 94, 60),
        "Bronze": discord.Colour.from_rgb(205, 127, 50),
        "Silver": discord.Colour.from_rgb(192, 192, 192),
        "Gold": discord.Colour.from_rgb(255, 215, 0),
        "Platinum": discord.Colour.from_rgb(229, 228, 226),
        "Diamond": discord.Colour.from_rgb(185, 242, 255),
        "Immortal": discord.Colour.from_rgb(100, 65, 165),
        "Radiant": discord.Colour.from_rgb(245, 166, 35),
        "Unranked": discord.Colour.default()
    }
        
    if rank_name in ranks:
        color = ranks[rank_name].value
        role = discord.utils.get(ctx.guild.roles, name="Valorant | "+player_cur_rank)
        if role is None:
            await ctx.guild.create_role(name="Valorant | "+player_cur_rank, color=color)
        role = discord.utils.get(ctx.guild.roles, name="Valorant | "+player_cur_rank)
        await ctx.author.add_role(role)

# async def updateDiscordRank(discord_id : int):
#     #WIP
#     a = await discord.guild.utils.find(lambda m: m.id == discord_id, interactions.guild.Guild)
#     logging.debug("member : " + a)


async def updateDiscordRankInternal(member: discord.Member):
    logging.info("updating discord rank")
    intents = discord.Intents.default()
    intents.members = True
    client = discord.Client(intents=intents)
    guild = client.get_guild(1056830364275982347)
    member = guild.get_member(184886547693174800)


    # player_cur_rank = data["data"]["current_data"]["currenttierpatched"]
    # if player_cur_rank == None :
    #         rank_name = "Unranked"
    #         player_cur_rank = "Unranked"
    # else:
    #     rank_name = ' '.join(player_cur_rank.split()[:-1])
    rank_name = "Bronze"
    player_cur_rank = "Bronze 2"
        
    member = discord.utils.get(guild.members, id=184886547693174800)

    ranks = {
        "Iron": discord.Colour.from_rgb(139, 94, 60),
        "Bronze": discord.Colour.from_rgb(205, 127, 50),
        "Silver": discord.Colour.from_rgb(192, 192, 192),
        "Gold": discord.Colour.from_rgb(255, 215, 0),
        "Platinum": discord.Colour.from_rgb(229, 228, 226),
        "Diamond": discord.Colour.from_rgb(185, 242, 255),
        "Immortal": discord.Colour.from_rgb(100, 65, 165),
        "Radiant": discord.Colour.from_rgb(245, 166, 35),
        "Unranked": discord.Colour.default()
    }
        
    if rank_name in ranks:
        color = ranks[rank_name].value
        role = discord.utils.get(interactions.guild.Guild.roles, name="Valorant | "+player_cur_rank)
        if role is None:
            await interactions.guild.Guild.create_role(name="Valorant | "+player_cur_rank, color=color)
        role = discord.utils.get(interactions.guild.Guild.roles, name="Valorant | "+player_cur_rank)
        await member.add_role(role)

