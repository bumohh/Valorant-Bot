import interactions
import discord
import asyncio
import logging
from variables import discord_token
import time
import discord_methods
import config_methods as config
import network_handler as network
import task_handler as taskHandler


logging.basicConfig(filename='logs\debug-'+str(time.time())+'.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

bot = interactions.Client(discord_token)

handler = taskHandler.TaskHandler()

#discord events
@bot.event
async def on_ready():
    handler.__init__(asyncio.create_task(discord_methods.updater()))
    pass
            
    
#bot commands
@bot.command(
    name="add_valorant_account",
    description="Auto Valorant account rank role adder.",
    options = [
        interactions.Option(
            name="region",  
            description="Example NA",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="name",
            description="Example nhmln",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="tag",
            description="Example NA1",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)

#discord command methods
async def adder_command(ctx: interactions.CommandContext,region: str, name: str, tag: str):
    try:
        #player_name, player_tag, player_cur_rank, player_elo, player_high_rank = fetchDataForUser(region, name, tag)
        logging.debug("starting adder_command function")
        
        data = network.fetchDataForUser(region, name, tag)
        
        player_name = data["data"]["name"]
        player_tag = data["data"]["tag"]
        player_cur_rank = data["data"]["current_data"]["currenttierpatched"]
        discord_id = int(ctx.author.id)
        discord_methods.save_data(data, discord_id, region)
        
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
        handler.startNewTask(asyncio.create_task(discord_methods.updater()))
    except ValueError as e:
        await ctx.send(str(e))
    
config.internalSoftReset()
bot.start()