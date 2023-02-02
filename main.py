# Discord
import discord
from discord import app_commands
from discord.app_commands import Choice
# External
import asyncio
# Internal
import log
import on_ready_functions
import slash_functions
from variables import *


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild = discord.Object(id=guild_id))
            self.synced = True
        log.debug(f"We have logged in as {self.user}.")

        on_ready_functions.initDatabase()
        while True:
            if on_ready_functions.isDatabaseEmpty():
                await asyncio.sleep(1) 
            else:
                # Main on_ready loop grabs database and loops through the data one per every 10 seconds so api call should only be 6 per minute max.
                for data in on_ready_functions.readDatabase():
                    discord_id, region, ign, tag, rank_full, puuid = data
                    log.debug("Calling Regular Valorant API for "+ str(ign)+" #"+str(tag)+".")
                    regularValApiCall_results = on_ready_functions.regularValApiCall(region, puuid)
                    pulled_rank_full = regularValApiCall_results[0]
                    pulled_ign = regularValApiCall_results[1]
                    pulled_tag = regularValApiCall_results[2]
                    if str(pulled_rank_full) != str(rank_full):
                        on_ready_functions.updateDatabase(pulled_rank_full, pulled_ign, pulled_tag, discord_id, puuid)
                    elif str(pulled_ign) != str(ign):
                        on_ready_functions.updateDatabase(pulled_rank_full, pulled_ign, pulled_tag, discord_id, puuid)
                    elif str(pulled_tag) != str(pulled_tag):
                        on_ready_functions.updateDatabase(pulled_rank_full, pulled_ign, pulled_tag, discord_id, puuid)
                    
                    if str(pulled_rank_full) != str(rank_full):
                        log.debug("pulled_rank_full did not equal "+str(pulled_rank_full)+" rank_full " + str(rank_full)+".")
                        # Sorts pulled_rank_full into variables for setting and creating
                        if pulled_rank_full == None :
                                rank_short = "Unranked"
                                pulled_rank_full = "Unranked"
                        else:
                            rank_short = ' '.join(pulled_rank_full.split()[:-1])

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
                        color = ranks[rank_short].value
                        guild = discord.utils.get(client.guilds, id=guild_id)
                        member = discord.utils.get(guild.members, id=int(discord_id))

                        old_role_name = "Valorant | " + rank_full
                        old_role = discord.utils.get(guild.roles, name=old_role_name)
                        
                        role_name = "Valorant | " + pulled_rank_full
                        role = discord.utils.get(guild.roles, name=role_name)
                        if not role:
                            role = await guild.create_role(name=role_name,color=color)
                        
                        await member.remove_roles(old_role)
                        await member.add_roles(role)
                        log.debug("removed old role called "+str(old_role)+" and replaced with "+role+".")
                    
                    await asyncio.sleep(10)

client = aclient()
tree = app_commands.CommandTree(client)

@app_commands.choices(region = [
    Choice(name="NA", value="NA"),
    Choice(name="EU", value="EU"),
    Choice(name="KR", value="KR")
    ]
)

# /val-tracking-add command
@tree.command(guild = discord.Object(id=guild_id), name = 'val-tracking-add', description='Command for Valorant role syncing and tracking.')
async def valTrackingAddCommand(interaction: discord.Interaction, region: str, name: str, tag: str):
    await interaction.response.defer(ephemeral=False)
    discord_id = str(interaction.user.id)
    
    # Rename to read easier
    ign = name
    
    # External helper functions
    initialValApiCall_results = slash_functions.InitialValApiCall(region, ign, tag)
    bannerValApiCall_results = slash_functions.bannerValApiCall(ign, tag)
    pulled_rank_full = initialValApiCall_results[0]
    puuid = initialValApiCall_results[1]
    rank_image = initialValApiCall_results[2]
    
    if slash_functions.duplicateCheck(puuid):
        guild = interaction.guild
        user = interaction.user
        member = guild.get_member(user.id)
        await interaction.followup.send("The Valorant account under " +ign+" #"+tag+" appears to have already be linked to another Discord account.")
    
    else:
        slash_functions.initialDatabaseSave(discord_id, region, ign, tag, pulled_rank_full, puuid)
        
        # Sorts pulled_rank_full into variables for setting and creating
        if pulled_rank_full == None :
                rank_short = "Unranked"
                pulled_rank_full = "Unranked"
        else:
            rank_short = ' '.join(pulled_rank_full.split()[:-1])

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
        
        role_name = "Valorant | " + pulled_rank_full
        color = ranks[rank_short].value
        
        # Sets/Creates the role
        guild = interaction.guild
        user = interaction.user
        member = guild.get_member(user.id)

        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(name=role_name, color=color)
            log.debug(f'Created new role with name {role.name}')
        
        #adds role to user and send msg back to user
        await member.add_roles(role)
        #await interaction.response.send_message("Account: "+str(region)+" "+name+" #"+tag+" has been added user: "+member.name+"#"+member.discriminator+".", ephemeral = True)
        embed = discord.Embed(title="Added Valorant Account:", color=color)
        embed.set_thumbnail(url=f"{rank_image}")
        embed.set_image(url=f"{bannerValApiCall_results}")
        embed.add_field(name="Region:", value=region, inline=True)
        embed.add_field(name="Username:", value=name, inline=True)
        embed.add_field(name="Tag:", value=tag, inline=True)
        embed.add_field(name="Rank:", value=pulled_rank_full, inline=True)
        embed.add_field(name="Added Role:",value=role.name, inline=True)

        await interaction.followup.send(embed=embed)

    # # /val-accounts-overview command
@tree.command(name = 'val-accounts-overview', description="Command to get overview of Valorant accounts associated with your Discord.", guild = discord.Object(id=guild_id))
async def valAccountsOverview(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    discord_id = interaction.user.id
    embed_list = slash_functions.getRowsByDiscord_id(discord_id)

    for user_id, region, name, tag, rank_full, puuid in embed_list:
        rank_image = str(slash_functions.InitialValApiCall(region, name, tag)[2])
        banner_image = str(slash_functions.bannerValApiCall(name, tag))
        # Sorts pulled_rank_full into variables for setting and creating
        if rank_full == None :
                rank_short = "Unranked"
                rank_full = "Unranked"
        else:
            rank_short = ' '.join(rank_full.split()[:-1])

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
        
        role_name = "Valorant | " + rank_full
        color = ranks[rank_short].value
        
        embed = discord.Embed(title="Overview of Valorant Accounts:", color=color)
        embed.set_thumbnail(url=f"{rank_image}")
        embed.set_image(url=f"{banner_image}")
        embed.add_field(name="Region:", value=region, inline=True)
        embed.add_field(name="Username:", value=name, inline=True)
        embed.add_field(name="Tag:", value=tag, inline=True)
        embed.add_field(name="Rank:", value=rank_full, inline=True)
        embed.add_field(name="Added Role:",value=role_name, inline=True)        
        await interaction.followup.send(embed=embed)


# /val-tracking-remove-all command
@tree.command(name = 'val-tracking-remove-all', description='Command to remove all Valorant roles from the user.', guild = discord.Object(id=guild_id))
async def removeRoles(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    user = interaction.user
    discord_id = user.id
    slash_functions.removeValorantAccountfromDatabase(str(discord_id))
    member = guild.get_member(discord_id)
    roles_to_remove = [role for role in member.roles if 'Valorant | ' in role.name]
    for role in roles_to_remove:
        await member.remove_roles(role)
    await interaction.followup.send("All Valorant accounts attached to " +member.name+" #"+member.discriminator+" have been removed.")

client.run(discord_token)