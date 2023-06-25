# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import discord
import json
import subprocess
from dotenv import dotenv_values

##### data###############
env_vars = dotenv_values('secrets.env')
TOKEN = env_vars['TOKEN_ID']
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
########################

##### functions##########
########################


client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('Minecraft_Whitelist_Bot is Online!')


@client.event
async def on_message(message):
    if isinstance(message.channel, discord.Thread):
        thread_id = env_vars['THREAD_ID']  # Minecraft Whitelist Thread
        if message.channel.id == int(thread_id):
            if message.author != client.user:
                name = message.content

                #whitelist_path = '/home/mdkulikowski/game_server_data/minecraft_data/server/whitelist.json'
                working_dir = '/home/mdkulikowski/game_server_data/minecraft_data/'
                script_dir = working_dir + 'restart_server.sh'
                whitelist_path = working_dir + 'server/whitelist.json'
                # open file(filename)
                with open(whitelist_path) as file:
                    data = json.load(file)

                # check if duplicates
                duplicate = False

                for entrie in data:
                    if entrie['name'] == name:
                        duplicate = True

                # print error or write to json
                if (not duplicate):
                    new_data = {}
                    new_data['name'] = name
                    data.append(new_data)
                    with open(whitelist_path, 'w') as file:
                        json.dump(data, file)
                    await message.channel.send(
                        "Registered user in whitelist...Server will now restart")
                                        
                    subprocess.call(['bash', script_dir], cwd=working_dir)

                else:
                    await message.channel.send('Duplicate name detected, will not restart')


try:
    client.run(TOKEN)
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    else:
        raise e
