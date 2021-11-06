import discord
import asyncio
import aiohttp
import random
import aiosqlite
from discord.utils import get
from discord import Intents
from discord.ext import tasks, commands
from rcon import rcon
from dotenv import load_dotenv
import os
load_dotenv()

intents= Intents.default()
intents.members = True
client = commands.Bot(command_prefix="$", intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
    print("PUG BOT IS READY.")
    print(f"Bot is in {len(client.guilds)} guilds with {len(client.users)} combined users.")
@client.event
async def on_guild_join(guild):
    async with aiosqlite.connect('settings.sqlite3') as db:
        await db.execute(f'insert into guildchannels (guildid) values ({guild.id})')
        await db.execute(f'insert into guildsettings (guildid) values ({guild.id})')
        await db.commit()
@client.event
async def on_guild_remove(guild):
    async with aiosqlite.connect('settings.sqlite3') as db:
        await db.execute(f'delete from guildchannels where guildid={guild.id}')
        await db.execute(f'delete from guildsettings where guildid={guild.id}')
        await db.commit()
@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)} ms')
@client.command()
async def help(ctx):
    embed = discord.Embed(
        colour = discord.Colour.orange()
    )
    embed.set_author(name="Help")
    embed.add_field(name="$setchannel (channel type)", value="Adds your channel type to the database for pug running purposes. Do $setchannel for more info.", inline=False)
    embed.add_field(name="$startpug (PUG number/letter)", value = "Automatically and randomly rolls all people in your building channel into two teams. This will also send a DM to all the users selected with the server connect info. Do $startpug for more info.", inline=False)
    embed.add_field(name="$endpug (PUG number/letter)", value="Brings all the people in both team channels to your adding-up/waiting-for-pug channel.", inline=False)
    embed.add_field(name="$pickcaptains", value="Automatically picks two people from your building channel and moves them into your captains VC. You can also do the same thing with $pickcaptain for just one person.", inline=False)
    embed.add_field(name="$pick (Player) (channel/team)", value="Only people in the 'captains' voice chat can use this command. Allows captains to easily move the @-ed player into the channel of your choosing. Do $pick for more info.", inline=False)
    embed.add_field(name="$moveme (channel/team)", value="Only people in the 'captains' voice chat can use this command. Allows captains to easily move themselves into their teams VC once they are done picking their teams.", inline=False)
    embed.add_field(name="$command (pug letter) (command)", value="Allows Pug Runners to send RCON commands from Discord. Do $command for additional info.", inline=False)
    embed.add_field(name="$setserver (pug letter) (address) (password) (rconpassword)", value="Allows Pug Runners to set the TF2 Server for each individual Pug. Do $setserver for more info.", inline=False)
    embed.add_field(name="$sendinfo (pug letter)", value="Manually sends the connect info to the people in the appropriate pug channels. Meant to be used in situations where players are manually picked via $pickcaptains and $pick.", inline=False)
    embed.add_field(name="$settings (setting to change) (true/false)", value="Just typing $settings will return all of your settings, explanations of what they do, and their statuses.", inline=False)
    embed.add_field(name="$setrole (@ your desired role) (division name)", value="Simply @ the role you want to set as your division role and then type the name of the division. Do $setrole for more info and a list of available division names", inline=False)
    embed.add_field(name="$fatkid (number of people to fatkid)", value="Simply choose the number of people you wish to remove from your buildchannel and place into your fat-kid channel (or simply disconnect if you don't have one selected), and it will move them into there.", inline=False)
    embed.add_field(name="$bringin", value="Brings in everyone in the fatkids channel into your build channel.", inline=False)
    embed.add_field(name="$resetmedroles", value="This will reset who has the 'played med' role in your server, if you are using medcheck for your pickcaptains functionality.", inline=False)
    embed.add_field(name="$startbuild (number)", value="This will bring in the selected amount of members from your addingup channel into your buildchannel.", inline=False)
    await ctx.send(embed=embed)
@client.command()
async def setchannel(ctx, type):
    guild = client.get_guild(ctx.guild.id)
    author = guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        if not ctx.author.voice is None:
            channel = ctx.author.voice.channel
            async with aiosqlite.connect('settings.sqlite3') as db:
                if "buildchannel" in type.lower():
                    await db.execute(f"update guildchannels set buildchannel = {channel.id} where guildid='{ctx.guild.id}'")
                    await db.commit()
                    await ctx.send(f"Set '{channel}' as buildchannel")
                elif "addingup" in type.lower():
                    await db.execute(f"update guildchannels set addingup = {channel.id} where guildid='{ctx.guild.id}'")
                    await db.commit()
                    await ctx.send(f"Set '{channel}' as addingup")
                elif "apugblu" in type.lower():
                    await db.execute(f"update guildchannels set blu1 = {channel.id} where guildid='{ctx.guild.id}'")
                    await db.commit()
                    await ctx.send(f"Set '{channel}' as APUGBlu")
                elif "apugred" in type.lower():
                    await db.execute(f"update guildchannels set red1 = {channel.id} where guildid='{ctx.guild.id}'")
                    await db.commit()
                    await ctx.send(f"Set '{channel}' as APUGRed")
                elif "bpugred" in type.lower():
                    await db.execute(f"update guildchannels set red2 = {channel.id} where guildid='{ctx.guild.id}'")
                    await db.commit()
                    await ctx.send(f"Set '{channel}' as BPUGRed")
                elif "bpugblu" in type.lower():
                    await db.execute(f"update guildchannels set blu2 = {channel.id} where guildid='{ctx.guild.id}'")
                    await db.commit()
                    await ctx.send(f"Set '{channel}' as BPUGBlu")
                elif "cpugred" in type.lower():
                    await db.execute(f"update guildchannels set red3 = {channel.id} where guildid='{ctx.guild.id}'")
                    await db.commit()
                    await ctx.send(f"Set '{channel}' as CPUGRed")
                elif "cpugblu" in type.lower():
                    await db.execute(f"update guildchannels set blu3 = {channel.id} where guildid='{ctx.guild.id}'")
                    await db.commit()
                    await ctx.send(f"Set '{channel}' as CPUGBlu")
                elif "captains" in type.lower():
                    await db.execute(f"update guildchannels set captains = {channel.id} where guildid='{ctx.guild.id}'")
                    await db.commit()
                    await ctx.send(f"Set '{channel}' as captains")    
                elif "fatkids" in type.lower():
                    await db.execute(f"update guildchannels set fatkids = {channel.id} where guildid='{ctx.guild.id}'")
                    await db.commit()
                    await ctx.send(f"Set '{channel}' as fatkids")    
                else:
                    await ctx.send('Input not understood, check $setchannel to ensure you input the correct type.')
                print(f'{channel} set to {type} by {author.display_name} in {guild.name}')
        else:
            await ctx.send('You are not in a voice channel!')
    else:
        await ctx.send('You do not have permission to use this command!')
@setchannel.error
async def setchannel_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
        colour = discord.Colour.orange()
    )
        embed.set_author(name="How to Set Channels")
        embed.add_field(name="Use", value="Simply join the channel you would like to set, then specify the type of channel you would like to set after $setchannel.\n Example: $setchannel buildchannel", inline=False)
        embed.add_field(name="Types", value="buildchannel \n APUGBlu \n APUGRed \n BPUGBlu \n BPUGRed \n CPUGBlu \n CPUGRed \n captains \n addingup \n fatkids", inline=False)
        async with aiosqlite.connect('settings.sqlite3') as db:
            cursor = await db.execute(f"select addingup, buildchannel, blu1, red1, blu2, red2, blu3, red3, captains, fatkids from guildchannels where guildid='{ctx.guild.id}'")
            info = await cursor.fetchone()
            addingup = ctx.guild.get_channel(info[0])
            buildchannel = ctx.guild.get_channel(info[1])
            blu1 = ctx.guild.get_channel(info[2])
            red1 = ctx.guild.get_channel(info[3])
            blu2 = ctx.guild.get_channel(info[4])
            red2 = ctx.guild.get_channel(info[5])
            blu3 = ctx.guild.get_channel(info[6])
            red3 = ctx.guild.get_channel(info[7])
            captains = ctx.guild.get_channel(info[8])
            fatkids = ctx.guild.get_channel(info[9])
            embed.add_field(name="Current Set Channels", value=f"**Adding Up** \n{addingup} \n**Build Channel** \n{buildchannel} \n**ABlu** \n{blu1} \n**ARed** \n{red1} \n**BBlu** \n{blu2} \n**BRed** \n{red2} \n**CBlu** \n{blu3} \n**CRed** \n{red3} \n**Captains** \n{captains} \n**Fatkids** \n{fatkids}", inline=False)
        await ctx.send(embed=embed)
    else:
        raise error
@client.command()
async def startpug(ctx, letter):
    guild = client.get_guild(ctx.guild.id)
    author = guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            cursor = await db.execute(f"SELECT skillbased FROM guildsettings WHERE guildid='{guild.id}'")
            check = await cursor.fetchone()
            if check[0] == 0 or check[0] is None:
                if 'a' in letter.lower():
                    cursor = await db.execute(f"select red1, blu1, buildchannel, pug1address, pug1password from guildchannels where guildid='{guild.id}'")
                elif 'b' in letter.lower():
                    cursor = await db.execute(f"select red2, blu2, buildchannel, pug2address, pug2password from guildchannels where guildid='{guild.id}'")
                elif 'c' in letter.lower():
                    cursor = await db.execute(f"select red3, blu3, buildchannel, pug3address, pug3password from guildchannels where guildid='{guild.id}'")
                channels = await cursor.fetchone()
                red = guild.get_channel(channels[0])
                blu = guild.get_channel(channels[1])
                build = guild.get_channel(channels[2])
                members = build.members
                random.shuffle(members)
                length = int(len(members) / 2)
                for member in members[length:]:
                    await member.move_to(red)
                    try:
                        await member.send(f"**YOUR PUG IS STARTING** \nYou will be on the :red_square: **RED** :red_square: team! \nTo connect, put this in your TF2 console: \nconnect {channels[3]};password {channels[4]} \nOr just click on this link!: steam://connect/{channels[3]}/{channels[4]} \nIf you need help, contact <@{ctx.author.id}>")
                    except:
                        pass
                await ctx.send(f' Moving {[s.display_name for s in red.members]} to {red}...')
                for member in members[:length]:
                    await member.move_to(blu)
                    try:
                        await member.send(f"**YOUR PUG IS STARTING** \nYou will be on the :blue_square: **BLU** :blue_square: team! \nTo connect, put this in your TF2 console: \nconnect {channels[3]};password {channels[4]} \nOr just click on this link!: steam://connect/{channels[3]}/{channels[4]} \nIf you need help, contact <@{ctx.author.id}>")
                    except:
                        pass
                await ctx.send(f' Moving {[s.display_name for s in blu.members]} to {blu}...')
            elif check[0] == 1:
                if 'a' in letter.lower():
                    cursor = await db.execute(f"select red1, blu1, buildchannel, pug1address, pug1password, newcomer, amateur, intermediate, main, advanced, challenger, invite from guildchannels where guildid='{guild.id}'")
                elif 'b' in letter.lower():
                    cursor = await db.execute(f"select red2, blu2, buildchannel, pug2address, pug2password, newcomer, amateur, intermediate, main, advanced, challenger, invite from guildchannels where guildid='{guild.id}'")
                elif 'c' in letter.lower():
                    cursor = await db.execute(f"select red3, blu3, buildchannel, pug3address, pug3password, newcomer, amateur, intermediate, main, advanced, challenger, invite from guildchannels where guildid='{guild.id}'")
                channels = await cursor.fetchone()
                red = guild.get_channel(channels[0])
                blu = guild.get_channel(channels[1])
                build = guild.get_channel(channels[2])
                newcomer = guild.get_role(channels[5])
                amateur = guild.get_role(channels[6])
                intermediate = guild.get_role(channels[7])
                main = guild.get_role(channels[8])
                advanced = guild.get_role(channels[9])
                challenger = guild.get_role(channels[10])
                invite = guild.get_role(channels[11])
                members = build.members
                divroles = (newcomer, amateur, intermediate, main, advanced, challenger, invite)
                ncmem = []
                ammem = []
                immem = []
                mainmem = []
                advmem = []
                chalmem = []
                invmem = []
                for member in members:
                    if newcomer in member.roles:
                        ncmem.append(member)
                    elif amateur in member.roles:
                        ammem.append(member)
                    elif intermediate in member.roles:
                        immem.append(member)
                    elif main in member.roles:
                        mainmem.append(member)
                    elif advanced in member.roles:
                        advmem.append(member)
                    elif challenger in member.roles:
                        chalmem.append(member)
                    elif invite in member.roles:
                        invmem.append(member)
                memroles = [(7,invmem), (6,chalmem), (5,advmem), (4,mainmem), (3,immem), (2,ammem), (1,ncmem)]
                for members in memroles:
                    random.shuffle(members[1])
                def shuffle(memberlist):
                    cum = True
                    a = 0
                    rolllist = []
                    while cum:
                        redplayers = []
                        bluplayers = []
                        redskill = 0
                        bluskill = 0
                        a += 1
                        for members in memberlist:
                            for fella in members[1]:
                                num = random.randint(1,101)
                                if num <= 50:   
                                    redskill += members[0]
                                    redplayers.append(fella)
                                else:
                                    bluskill += members[0]
                                    bluplayers.append(fella)
                        if len(bluplayers) == len(redplayers):
                            rolllist.append([redskill,bluskill,(redplayers,bluplayers)])
                        if len(bluplayers) == len(redplayers) and len(bluplayers) != 0 and bluskill == redskill:
                            cum = False
                            return redplayers, bluplayers
                        if a == 500000:
                            skilldif = []
                            for ind,roll in enumerate(rolllist):
                                if len(roll[2][0]) == len(roll[2][1]):
                                    skilldif.append([ind,abs(roll[0]-roll[1])])
                            cum = False
                    print(len(rolllist))
                    print(len(skilldif))
                    minimum = min(skilldif, key=lambda x: x[1])
                    return rolllist[minimum[0]][2][0], rolllist[minimum[0]][2][1]
                redplayers, bluplayers = shuffle(memroles)
                for member in redplayers:
                    await member.move_to(red)
                    try:
                        await member.send(f"**YOUR PUG IS STARTING** \nYou will be on the :red_square: **RED** :red_square: team! \nTo connect, put this in your TF2 console: \nconnect {channels[3]};password {channels[4]} \nOr just click on this link!: steam://connect/{channels[3]}/{channels[4]} \nIf you need help, contact <@{ctx.author.id}>")
                    except:
                        pass
                await ctx.send(f' Moving {[s.display_name for s in red.members]} to {red}...')
                for member in bluplayers:
                    await member.move_to(blu)
                    try:
                        await member.send(f"**YOUR PUG IS STARTING** \nYou will be on the :blue_square: **BLU** :blue_square: team! \nTo connect, put this in your TF2 console: \nconnect {channels[3]};password {channels[4]} \nOr just click on this link!: steam://connect/{channels[3]}/{channels[4]} \nIf you need help, contact <@{ctx.author.id}>")
                    except:
                        pass
                    await ctx.send(f' Moving {[s.display_name for s in blu.members]} to {blu}...')
            print(f'{letter} pugs STARTED in {guild.name} by {author.display_name}')
    else:
        await ctx.send('You do not have permission to use this command!')
@startpug.error
async def startpug_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
        colour = discord.Colour.orange()
    )
        embed.set_author(name="How to Start a Pug")
        embed.add_field(name="Use", value="Simply select the pugs you would like to start when you have the desired amount of people in your building channel or have picked your teams. \n Example: $startpug A", inline=False)
        await ctx.send(embed=embed)
    else:
        raise error

@client.command()
async def endpug(ctx, letter):
    guild = client.get_guild(ctx.guild.id)
    author = guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            if 'a' in letter.lower():
                cursor = await db.execute(f"select red1, blu1, addingup from guildchannels where guildid='{guild.id}'")
                channels = await cursor.fetchone()
                red = guild.get_channel(channels[0])
                blu = guild.get_channel(channels[1])
                adding = guild.get_channel(channels[2])
                await ctx.send(f' Moving {[s.display_name for s in red.members]} to {adding}...')
                for member in red.members:                   
                    await member.move_to(adding)
                await ctx.send(f' Moving {[s.display_name for s in blu.members]} to {adding}...')
                for member in blu.members:
                    await member.move_to(adding)
            elif 'b' in letter.lower():
                cursor = await db.execute(f"select red2, blu2, addingup from guildchannels where guildid='{guild.id}'")
                channels = await cursor.fetchone()
                red = guild.get_channel(channels[0])
                blu = guild.get_channel(channels[1])
                adding = guild.get_channel(channels[2])
                await ctx.send(f' Moving {[s.display_name for s in red.members]} to {adding}...')
                for member in red.members:
                    await member.move_to(adding)
                await ctx.send(f' Moving {[s.display_name for s in blu.members]} to {adding}...')
                for member in blu.members:
                    await member.move_to(adding)
            elif 'c' in letter.lower():
                cursor = await db.execute(f"select red3, blu3, addingup from guildchannels where guildid='{guild.id}'")
                channels = await cursor.fetchone()
                red = guild.get_channel(channels[0])
                blu = guild.get_channel(channels[1])
                adding = guild.get_channel(channels[2])
                await ctx.send(f' Moving {[s.display_name for s in red.members]} to {adding}...')
                for member in red.members:
                    await member.move_to(adding)
                await ctx.send(f' Moving {[s.display_name for s in blu.members]} to {adding}...')
                for member in blu.members:
                    await member.move_to(adding)
            print(f'{letter} pugs ENDED in {guild.name} by {author.display_name}')
    else:
        await ctx.send('You do not have permission to use this command!')

@client.command()
async def pickcaptains(ctx):
    guild = client.get_guild(ctx.guild.id)
    author = guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            cursor = await db.execute(f"select medcheck, meddodge from guildsettings where guildid='{guild.id}'")
            check = await cursor.fetchone()
            if check[0] == 1:
                cursor = await db.execute(f"select buildchannel, captains, playedmed, meddodger from guildchannels where guildid='{guild.id}'")
                channels = await cursor.fetchone()
                build = guild.get_channel(channels[0])
                playedmed = guild.get_role(channels[2])
                potentialcaptains = []
                for member in build.members:
                    if not playedmed in member.roles:
                        potentialcaptains.append(member)
                random.shuffle(potentialcaptains)
                if check[1] == 1:
                    meddodger = guild.get_role(channels[3])
                    for member in potentialcaptains:
                        if meddodger in member.roles:
                            potentialcaptains.remove(member)
                            potentialcaptains.append(member)
                captains = potentialcaptains[-2:]
                captainvc = guild.get_channel(channels[1])
                for captain in captains:
                    await captain.move_to(captainvc)
                    await captain.add_roles(playedmed)
                    try:
                        await captain.remove_roles(meddodger)
                    except:
                        pass
                await ctx.send(f'Your captains are {captains[0].display_name} and {captains[1].display_name}.')
            else:
                cursor = await db.execute(f"select buildchannel, captains, playedmed, meddodger from guildchannels where guildid='{guild.id}'")
                channels = await cursor.fetchone()
                build = guild.get_channel(channels[0])
                potentialcaptains = build.members
                random.shuffle(potentialcaptains)
                if check[1] == 1:
                    meddodger = guild.get_role(channels[3])
                    for member in potentialcaptains:
                        if meddodger in member.roles:
                            potentialcaptains.remove(member)
                            potentialcaptains.append(member)
                captains = potentialcaptains[-2:]
                captainvc = guild.get_channel(channels[1])
                for captain in captains:
                    await captain.move_to(captainvc)
                    try:
                        await captain.remove_roles(meddodger)
                    except:
                        pass
                await ctx.send(f'Your captains are {captains[0].display_name} and {captains[1].display_name}.')
    else:
        await ctx.send('You do not have permission to use this command!')
@client.command()
async def pickcaptain(ctx):
    guild = client.get_guild(ctx.guild.id)
    author = guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            cursor = await db.execute(f"select medcheck, meddodge from guildsettings where guildid='{guild.id}'")
            check = await cursor.fetchone()
            if check[0] == 1:
                cursor = await db.execute(f"select buildchannel, captains, playedmed, meddodger from guildchannels where guildid='{guild.id}'")
                channels = await cursor.fetchone()
                build = guild.get_channel(channels[0])
                playedmed = guild.get_role(channels[2])
                potentialcaptains = []
                for member in build.members:
                    if not playedmed in member.roles:
                        potentialcaptains.append(member)
                random.shuffle(potentialcaptains)
                if check[1] == 1:
                    meddodger = guild.get_role(channels[3])
                    for member in potentialcaptains:
                        if meddodger in member.roles:
                            potentialcaptains.remove(member)
                            potentialcaptains.append(member)
                captains = potentialcaptains[-1:]
                captainvc = guild.get_channel(channels[1])
                for captain in captains:
                    await captain.move_to(captainvc)
                    await captain.add_roles(playedmed)
                    try:
                        await captain.remove_roles(meddodger)
                    except:
                        pass
                await ctx.send(f'Your captain is {captains[0].display_name}.')
            else:
                cursor = await db.execute(f"select buildchannel, captains, playedmed, meddodger from guildchannels where guildid='{guild.id}'")
                channels = await cursor.fetchone()
                build = guild.get_channel(channels[0])
                potentialcaptains = build.members
                random.shuffle(potentialcaptains)
                if check[1] == 1:
                    meddodger = guild.get_role(channels[3])
                    for member in potentialcaptains:
                        if meddodger in member.roles:
                            potentialcaptains.remove(member)
                            potentialcaptains.append(member)
                captains = potentialcaptains[-1:]
                captainvc = guild.get_channel(channels[1])
                for captain in captains:
                    await captain.move_to(captainvc)
                    try:
                        await captain.remove_roles(meddodger)
                    except:
                        pass
                await ctx.send(f'Your captain is {captains[0].display_name}.')
    else:
        await ctx.send('You do not have permission to use this command!')
@client.command()
async def pick(ctx, member: discord.Member, team):
    guild = client.get_guild(ctx.guild.id)
    author = guild.get_member(ctx.author.id)
    async with aiosqlite.connect('settings.sqlite3') as db:
        cursor = await db.execute(f"select captains, red1, blu1, red2, blu2, red3, blu3 from guildchannels where guildid='{guild.id}'")
        channels = await cursor.fetchone()
        captains = guild.get_channel(channels[0])
        if author.voice.channel == captains:
            if 'ared' in team.lower():
                ared = guild.get_channel(channels[1])
                await member.move_to(ared)
                await ctx.send(f'Moved {member.display_name} to {ared}!')
            elif 'ablu' in team.lower():
                ablu = guild.get_channel(channels[2])
                await member.move_to(ablu)
                await ctx.send(f'Moved {member.display_name} to {ablu}!')
            elif 'bred' in team.lower():
                bred = guild.get_channel(channels[3])
                await member.move_to(bred)
                await ctx.send(f'Moved {member.display_name} to {bred}!')
            elif 'bblu' in team.lower():
                bblu = guild.get_channel(channels[4])
                await member.move_to(bblu)
                await ctx.send(f'Moved {member.display_name} to {bblu}!')
            elif 'cred' in team.lower():
                cred = guild.get_channel(channels[5])
                await member.move_to(cred)
                await ctx.send(f'Moved {member.display_name} to {cred}!')
            elif 'cblu' in team.lower():
                cblu = guild.get_channel(channels[6])
                await member.move_to(cblu)
                await ctx.send(f'Moved {member.display_name} to {cblu}!')   
        else:
            await ctx.send('You are not a captain!')
@pick.error
async def pick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
        colour = discord.Colour.orange()
    )
        embed.set_author(name="How to Pick Your Players")
        embed.add_field(name="Use", value="Simply @ the player you want to pick and specify the channel in which you want to move them. You must be in the designated 'captains' channel in order to use this command. \n Example: $pick <@125788547939696640> ARed", inline=False)
        embed.add_field(name="Channels", value="ARed \nABlu \nBRed \nBBlu \nCRed \nCBlu", inline=False)
        await ctx.send(embed=embed)
    else:
        raise error
@client.command()
async def moveme(ctx, team):
    guild = client.get_guild(ctx.guild.id)
    author = guild.get_member(ctx.author.id)
    async with aiosqlite.connect('settings.sqlite3') as db:
        cursor = await db.execute(f"select captains, red1, blu1, red2, blu2, red3, blu3 from guildchannels where guildid='{guild.id}'")
        channels = await cursor.fetchone()
        captains = guild.get_channel(channels[0])
        if author.voice.channel == captains:
            if 'ared' in team.lower():
                ared = guild.get_channel(channels[1])
                await author.move_to(ared)
                await ctx.send(f'Moved {author.display_name} to {ared}!')
            elif 'ablu' in team.lower():
                ablu = guild.get_channel(channels[2])
                await author.move_to(ablu)
                await ctx.send(f'Moved {author.display_name} to {ablu}!')
            elif 'bred' in team.lower():
                bred = guild.get_channel(channels[3])
                await author.move_to(bred)
                await ctx.send(f'Moved {author.display_name} to {bred}!')
            elif 'bblu' in team.lower():
                bblu = guild.get_channel(channels[4])
                await author.move_to(bblu)
                await ctx.send(f'Moved {author.display_name} to {bblu}!')
            elif 'cred' in team.lower():
                cred = guild.get_channel(channels[5])
                await author.move_to(cred)
                await ctx.send(f'Moved {author.display_name} to {cred}!')
            elif 'cblu' in team.lower():
                cblu = guild.get_channel(channels[6])
                await author.move_to(cblu)
                await ctx.send(f'Moved {author.display_name} to {cblu}!')   
        else:
            await ctx.send('You are not a captain!')   
@client.command()
async def sendinfo(ctx, pug):
    guild = client.get_guild(ctx.guild.id)
    author = guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            if 'a' in pug.lower():
                cursor = await db.execute(f"select red1, blu1, pug1address, pug1password from guildchannels where guildid='{guild.id}'")
                info = await cursor.fetchone()
                red = guild.get_channel(info[0])
                blu = guild.get_channel(info[1])
                for member in blu.members:
                    try:
                        await member.send(f"**YOUR PUG IS STARTING** \nYou will be on the :blue_square: **BLU** :blue_square: team! \nTo connect, put this in your TF2 console: \nconnect {info[2]};password {info[3]} \nOr just click on this link!: steam://connect/{info[2]}/{info[3]} \nIf you need help, contact <@{ctx.author.id}>")
                    except:
                        pass
                for member in red.members:
                    try:
                        await member.send(f"**YOUR PUG IS STARTING** \nYou will be on the :red_square: **RED** :red_square: team! \nTo connect, put this in your TF2 console: \nconnect {info[2]};password {info[3]} \nOr just click on this link!: steam://connect/{info[2]}/{info[3]} \nIf you need help, contact <@{ctx.author.id}>")
                    except:
                        pass
                await ctx.send(f'Sent connect info to {[s.display_name for s in blu.members]} and {[s.display_name for s in red.members]}')
            elif 'b' in pug.lower():
                cursor = await db.execute(f"select red2, blu2, pug2address, pug2password from guildchannels where guildid='{guild.id}'")
                info = await cursor.fetchone()
                red = guild.get_channel(info[0])
                blu = guild.get_channel(info[1])
                for member in blu.members:
                    try:
                        await member.send(f"**YOUR PUG IS STARTING** \nYou will be on the :blue_square: **BLU** :blue_square: team! \nTo connect, put this in your TF2 console: \nconnect {info[2]};password {info[3]} \nOr just click on this link!: steam://connect/{info[2]}/{info[3]} \nIf you need help, contact <@{ctx.author.id}>")
                    except:
                        pass
                for member in red.members:
                    try:
                        await member.send(f"**YOUR PUG IS STARTING** \nYou will be on the :red_square: **RED** :red_square: team! \nTo connect, put this in your TF2 console: \nconnect {info[2]};password {info[3]} \nOr just click on this link!: steam://connect/{info[2]}/{info[3]} \nIf you need help, contact <@{ctx.author.id}>")
                    except:
                        pass
                await ctx.send(f'Sent connect info to {[s.display_name for s in blu.members]} and {[s.display_name for s in red.members]}')
            elif 'c' in pug.lower():
                cursor = await db.execute(f"select red2, blu2, pug2address, pug2password from guildchannels where guildid='{guild.id}'")
                info = await cursor.fetchone()
                red = guild.get_channel(info[0])
                blu = guild.get_channel(info[1])
                for member in blu.members:
                    try:
                        await member.send(f"**YOUR PUG IS STARTING** \nYou will be on the :blue_square: **BLU** :blue_square: team! \nTo connect, put this in your TF2 console: \nconnect {info[2]};password {info[3]} \nOr just click on this link!: steam://connect/{info[2]}/{info[3]} \nIf you need help, contact <@{ctx.author.id}>")
                    except:
                        pass
                for member in red.members:
                    try:
                        await member.send(f"**YOUR PUG IS STARTING** \nYou will be on the :red_square: **RED** :red_square: team! \nTo connect, put this in your TF2 console: \nconnect {info[2]};password {info[3]} \nOr just click on this link!: steam://connect/{info[2]}/{info[3]} \nIf you need help, contact <@{ctx.author.id}>")
                    except:
                        pass
                await ctx.send(f'Sent connect info to {[s.display_name for s in blu.members]} and {[s.display_name for s in red.members]}')            
    else:
        await ctx.send('You do not have permission to use this command!')
@client.command()
async def command(ctx, pug, *, command):
    guild = client.get_guild(ctx.guild.id)
    author = guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            if 'a' in pug.lower():
                cursor = await db.execute(f"select pug1address, pug1rcon from guildchannels where guildid='{guild.id}'")
                info = await cursor.fetchone()
                ipport = info[0].split(':')
                address = ipport[0]
                port = ipport[1]
                rconpw = info[1]
                await ctx.send(f"Sending command '**{command}**' to **A Pug**'s server **{address}:{port}**")
                await rcon(command,host=address,port=port,passwd=rconpw)
            elif 'b' in pug.lower():
                cursor = await db.execute(f"select pug2address, pug2rcon from guildchannels where guildid='{guild.id}'")
                info = await cursor.fetchone()
                ipport = info[0].split(':')
                address = ipport[0]
                port = ipport[1]
                rconpw = info[1]
                await ctx.send(f"Sending command '**{command}**' to **B Pug**'s server **{address}:{port}**")
                await rcon(command,host=address,port=port,passwd=rconpw)
            elif 'c' in pug.lower():
                cursor = await db.execute(f"select pug3address, pug3rcon from guildchannels where guildid='{guild.id}'")
                info = await cursor.fetchone()
                ipport = info[0].split(':')
                address = ipport[0]
                port = ipport[1]
                rconpw = info[1]
                await ctx.send(f"Sending command '**{command}**' to **C Pug**'s server **{address}:{port}**")
                await rcon(command,host=address,port=port,passwd=rconpw)
    else:
        await ctx.send('You do not have permission to use this command!')
@command.error
async def command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
        colour = discord.Colour.orange()
    )
        embed.set_author(name="How to use the Discord RCON Function")
        embed.add_field(name="Use", value="Simply specify the Pug you would like to send the command to, then type the command like you would in TF2's in-game console. \n Example: $command A changelevel koth_product_rcx", inline=False)
    else:
        raise error
@client.command()
async def setserver(ctx, pug, ipport, password, rcon):
    guild = client.get_guild(ctx.guild.id)
    author = guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            if 'a' in pug.lower():
                await db.execute(f"update guildchannels set pug1address = '{ipport}', pug1password = '{password}', pug1rcon = '{rcon}' where guildid='{guild.id}'")
                await ctx.send(f"Set A Pug's server to be address '**{ipport}**' with password '**{password}**' and rcon password '**{rcon}**'")
                await db.commit()
            elif 'b' in pug.lower():
                await db.execute(f"update guildchannels set pug2address = '{ipport}', pug2password = '{password}', pug2rcon = '{rcon}' where guildid='{guild.id}'")
                await ctx.send(f"Set B Pug's server to be address '**{ipport}**' with password '**{password}**' and rcon password '**{rcon}**'")
                await db.commit()
            elif 'c' in pug.lower():
                await db.execute(f"update guildchannels set pug3address = '{ipport}', pug3password = '{password}', pug3rcon = '{rcon}' where guildid='{guild.id}'")
                await ctx.send(f"Set C Pug's server to be address '**{ipport}**' with password '**{password}**' and rcon password '**{rcon}**'")
                await db.commit()
    else:
        await ctx.send('You do not have permission to use this command!')
@setserver.error
async def setserver_error(ctx, error):
    author = ctx.guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
            colour = discord.Colour.orange()
        )
            embed.set_author(name="How to Set The TF2 Servers for your Pugs")
            embed.add_field(name="Use", value="Gather the Pug letter, address and port, server password, and rcon password for the pug you would like to set. \n Example: $setserver A 123.456.789:27015 mypassword rconpassword", inline=False)
            async with aiosqlite.connect('settings.sqlite3') as db:
                cursor = await db.execute(f"select pug1address, pug1password, pug1rcon, pug2address, pug2password, pug2rcon, pug3address, pug3password, pug3rcon from guildchannels where guildid='{ctx.guild.id}'")
                info = await cursor.fetchone()
                embed.add_field(name="Currently Set Servers", value=f"**A Pugs** \nconnect {info[0]}; password {info[1]} | rconpw = {info[2]} \n**B Pugs** \nconnect {info[3]}; password {info[4]} | rconpw = {info[5]} \n**C Pugs** \nconnect {info[6]}; password {info[7]} | rconpw = {info[8]} \n", inline=False)
            await ctx.send(embed=embed)
        else:
            raise error
    else:
        await ctx.send('You do not have permission to use this command!')
@client.command()
async def settings(ctx, setting, bool):
    if 'true' in bool:
        num = 1
    elif 'false' in bool:
        num = 0
    async with aiosqlite.connect('settings.sqlite3') as db:
        await db.execute(f"UPDATE guildsettings SET {setting} = {num} WHERE guildid = {ctx.guild.id}")
        await db.commit()
        await ctx.send(f"Changing setting '**{setting}**' to be '**{bool}**'")
@settings.error
async def settings_error(ctx, error):
    author = ctx.guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
            colour = discord.Colour.orange()
        )
            embed.set_author(name="Settings for your TF2 Pugs")
            async with aiosqlite.connect('settings.sqlite3') as db:
                cursor = await db.execute(f"select * from guildsettings where guildid='{ctx.guild.id}'")
                set = await cursor.fetchone()
                embed.add_field(name="skillbased", value='True' if set[1] == 1 else 'False', inline=False)
                embed.add_field(name="medcheck", value='True' if set[2] == 1 else 'False', inline=False)
                embed.add_field(name="meddodge", value='True' if set[3] == 1 else 'False', inline=False)
            embed.add_field(name="Settings Explanation", value="'skillbased' sets whether your $startpug command will factor in skill based on role divs that would be setup in $setrole. \n'medcheck' sets whether your $pickcaptains command will only select players that haven't played med, determined by a role in $setrole. \n'meddodge' sets whether your $pickcaptains command will prioritize picking players with a role that says they have dodged medic in the past.", inline=False)
            await ctx.send(embed=embed)
        else:
            raise error
    else:
        await ctx.send('You do not have permission to use this command!')
@client.command()
async def setrole(ctx, role: discord.Role, div):
    author = ctx.guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            await db.execute(f"UPDATE guildchannels SET {div} = {role.id} WHERE guildid = {ctx.guild.id}")
            await db.commit()
            await ctx.send(f"Setting '**{role}**' to be your '**{div}**' role!")
    else:
        await ctx.send('You do not have permission to use this command!')
@setrole.error
async def setrole_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
        colour = discord.Colour.orange()
    )
        embed.set_author(name="How to Set Division Roles for your Pugs")
        embed.add_field(name="Use", value="Simply @ the role you would like to set to be a division's role in the server. \n Example: $setrole @Invite invite", inline=False)
        embed.add_field(name="Division names", value="newcomer \namateur \nintermediate \nmain \nadvanced \nchallenger \ninvite")
        async with aiosqlite.connect('settings.sqlite3') as db:
            cursor = await db.execute(f"select newcomer, amateur, intermediate, main, advanced, challenger, invite, playedmed from guildchannels where guildid='{ctx.guild.id}'")
            info = await cursor.fetchone()
            info = [ctx.guild.get_role(s) for s in info]
            embed.add_field(name="Currently Set Roles", value=f"**Newcomer** \n{info[0]} \n**Amateur** \n{info[1]} \n**Intermediate** \n{info[2]} \n**Main** \n{info[3]} \n**Advanced** \n{info[4]} \n**Challenger** \n{info[5]} \n**Invite** \n{info[6]} \n**Played Med** \n{info[7]}", inline=False)
        await ctx.send(embed=embed)
    else:
        raise error
@client.command()
async def fatkid(ctx, number: int):
    author = ctx.guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            cursor = await db.execute(f"select buildchannel, fatkids from guildchannels where guildid='{ctx.guild.id}'")
            info = await cursor.fetchone()
            build = ctx.guild.get_channel(info[0])
            fatkids = ctx.guild.get_channel(info[1])
            fatkidded = random.sample(build.members,number)
            for fatkid in fatkidded:
                await fatkid.move_to(fatkids)
            await ctx.send(f"Fatkidded {[s.display_name for s in fatkidded]} and moved them to {fatkids.name}")
    else:
        await ctx.send('You do not have permission to use this command!')
@client.command()
async def bringin(ctx):
    author = ctx.guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            cursor = await db.execute(f"select buildchannel, fatkids from guildchannels where guildid='{ctx.guild.id}'")
            info = await cursor.fetchone()
            build = ctx.guild.get_channel(info[0])
            fatkids = ctx.guild.get_channel(info[1])
            await ctx.send(f'Bringing in {[s.display_name for s in fatkids.members]} from {fatkids.name}')
            for fatkid in fatkids.members:
                await fatkid.move_to(build)
    else:
        await ctx.send('You do not have permission to use this command!')
@client.command()
async def resetmedroles(ctx):
    author = ctx.guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            cursor = await db.execute(f"select playedmed from guildchannels where guildid='{ctx.guild.id}'")
            info = await cursor.fetchone()
            playedmed = ctx.guild.get_role(info[0])
            removedmed = []
            for member in ctx.guild.members:
                if playedmed in member.roles:
                    await member.remove_roles(playedmed)
                    removedmed.append(member)
            await ctx.send(f"Removed the role **{playedmed}** from **{[s.display_name for s in removedmed]}**")
    else:
        await ctx.send('You do not have permission to use this command!')
@client.command()
async def startbuild(ctx, number):
    author = ctx.guild.get_member(ctx.author.id)
    if author.guild_permissions.move_members:
        async with aiosqlite.connect('settings.sqlite3') as db:
            cursor = await db.execute(f"select addingup, buildchannel from guildchannels where guildid='{ctx.guild.id}'")
            info = await cursor.fetchone()
            addingup = ctx.guild.get_channel(info[0])
            build = ctx.guild.get_channel(info[1])
            selected = random.sample(addingup.members,int(number))
            await ctx.send(f"Moving {[s.display_name for s in selected]} to {build} to start pugs!")
            for member in selected:
                await member.move_to(build)
    else:
        await ctx.send('You do not have permission to use this command!')
@tasks.loop(hours=12)
async def watch():
    list = len(client.users)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"over {list} Puggers! Use $help for help!"))
    print(f"Updating status to be 'Watching over {list} Puggers! Use $help for help!'")
@watch.before_loop
async def before_watch():
    await client.wait_until_ready()
watch.start()
client.run(os.getenv('TOKEN'))
