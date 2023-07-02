# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import discord
import json
import subprocess
import re
from dotenv import dotenv_values

##### data###############
env_vars = dotenv_values('secrets.env')
TOKEN = env_vars['TOKEN_ID']
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# whitelist_path = '/home/mdkulikowski/game_server_data/minecraft_data/server/whitelist.json'
working_dir = '/home/mdkulikowski/game_server_data/minecraft_data/'
script_dir = working_dir + 'restart_server.sh'
whitelist_path = working_dir + 'server/whitelist.json'
########################

##### functions##########


async def seach_whitelist(name, data, uuid):
    for entrie in data:
        if entrie['name'] == name:
            if (uuid != None):
                entrie['uuid'] = uuid
            return True
    return False


async def write_to_whitelist(data):
    with open(whitelist_path, 'w') as file:
        json.dump(data, file)


async def register_name(message, name, data):
    # check if duplicates
    # print error or write to json
    if (not (await seach_whitelist(name, data, None))):
        new_data = {}
        new_data['name'] = name
        data.append(new_data)
        await write_to_whitelist(data)
        await message.channel.send("Registered user in whitelist...Server will now restart")
        subprocess.call(['bash', script_dir], cwd=working_dir)
    else:
        await message.channel.send('Duplicate name detected, will not restart')


async def search_rejection_logs(logs):
    rejection = re.search('You are not white-listed on this server!', logs)
    if (rejection != None):
        pattern = r'UUID of player \S* is \S*'
        player_info_regex = re.search(pattern, logs)
        player_info = player_info_regex.group(0).split(' ')
        return (player_info[3], player_info[5])
    else:
        return None


async def register_uuid(message, data):
    # get the last login attempt
    docker_logs = subprocess.run(
        ['docker', 'logs', '--tail', '7', 'minecraft-server'], capture_output=True, text=True)
    error_log = docker_logs.stdout
    # search for attempt to join the server
    player_data = await search_rejection_logs(error_log)
    # get name and uuid if found
    if (player_data):
        # determine if name is registered
        if (await seach_whitelist(player_data[0], data, player_data[1])):
            # write uuid if name found
            await message.channel.send('Found record in whitelist...registering UUID')
            await write_to_whitelist(data)
            print(data)
            # restart server
            await message.channel.send('server restarting')
            subprocess.call(['bash', script_dir], cwd=working_dir)
        else:
            await message.channel.send('No record of player in whitelist. No UUID registered')
    else:
        await message.channel.send('Your login attempt was unable to be found on the server')
    return True
###################


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
                if message.content.startswith('#'):
                    pass
                else:
                    user_input = message.content
                    # open file(filename)
                    with open(whitelist_path) as file:
                        data = json.load(file)

                    if message.content == 'uuid':
                        await register_uuid(message, data)
                    else:
                        await register_name(message, user_input, data)


try:
    client.run(TOKEN)
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    else:
        raise e
