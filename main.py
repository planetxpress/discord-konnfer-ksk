import discord
import json
import os
import random
import requests
import time
from discord.ext import commands


def parse_ksk(data):
    '''
    Parses the JSON output provided by the KSK Classic WoW Addon.
    Format:
    {
        "ksk": {
            "date": (y-m-d),
            "time": (h:m),
            "classes": [
                {
                    "id": (uid),
                    "v": (class)
                }
            ],
            "users": [
                {
                    "id": (uid),
                    "n": (character name),
                    "c": (class uid)
                }
            ],
            "lists": [
                {
                    "id": (uid),
                    "n": (list name),
                    "users": [
                        (user uid)
                    ]
                }
            ]
        }
    }
    Parameters: data (dict): KSK JSON data.
    Returns: ksk (list): KSK lists to post to Discord.
    '''
    ksk = list()
    for klist in data['ksk']['lists']:
        class_rank = list()
        k = dict()
        k['characters'] = list()
        k['classes'] = list()
        k['name'] = klist['n']
        k['id'] = klist['id']
        k['updated'] = f'{data["ksk"]["date"]} {data["ksk"]["time"]}'

        for uid in klist['users']:
            class_rank.extend(
                [ u['c'] for u in data['ksk']['users'] if u['id'] == uid ]
            )
            k['characters'].extend(
                [ u['n'] for u in data['ksk']['users'] if u['id'] == uid ]
            )
        for uid in class_rank:
            k['classes'].extend(
                [ c['v'].capitalize() for c in data['ksk']['classes'] if c['id'] == uid ]
            )
        ksk.append(k)
    return ksk


def validate_ksk(data):
    '''
    Validate that the JSON data is in the expected KSK format.
    Check that we aren't getting spammed with too much data.

    Parameters: data (dict): KSK JSON data.
    Returns: True if data is valid. False if not valid.
    '''
    list_size_max = 50
    user_size_max = 1000
    try:
        if not all (
            k in data['ksk']
            for k in (
                'classes',
                'date',
                'lists',
                'time',
                'users'
            )
        ):
            return False
    except:
        return False
    try:
        list_size = len(data['ksk']['lists'])
        user_size = 0
        for l in data['ksk']['lists']:
            if len(l['users']) > user_size:
                user_size = len(l['users'])
    except:
        return False
    if (user_size > user_size_max) or (list_size > list_size_max):
        print(f'Amount of data sent was over the limit. Lists: {list_size} Users: {user_size}')
        return False
    return True 

def discord_messages(klist):
    '''
    Creates a Discord embedded message with a given KSK list.
    Paginate messages to work within Discord imposed constraints:
     - 2000 characters (computer characters, not WoW characters =D) per message.
     - 1024 characters per embed field.

    Parameters: klist (list): A single KSK list to post to Discord.
    Returns: messages (list): List of Discord message embed objects.
    '''
    messages = list()
    color = random.randrange(0, 16777215) # Random accent color for this list.
    index = 0
    paginate = 50
    while index <= len(klist['characters']):
        m = discord.Embed(
            color=color,
            title=klist['name'],
            type='rich'
        )
        m.set_thumbnail(url='https://raw.githubusercontent.com/planetxpress/discord-ksk-classic/main/images/ksklogo.png')
        if index == 0:
            m.add_field(name='Last Updated', value=klist['updated'], inline=False)
        if len(klist['characters']) < index + paginate:
            end = len(klist['characters'])
        else:
            end = index + paginate
        characters = klist['characters'][index:end]
        classes = klist['classes'][index:end]
        positions = [ str(p) for p in range(index+1,end+1) ]
        m.add_field(name='Name', value='\n'.join(characters), inline=True)
        m.add_field(name='Class', value='\n'.join(classes), inline=True)
        m.add_field(name='Position', value='\n'.join(positions), inline=True)
        m.set_footer(text=f'ID: {klist["id"]}')
        messages.append(m)
        index += paginate
    return messages


async def delete_old_list(ctx, *, kid: str):
    messages = await ctx.channel.history(limit=100).flatten()
    for m in messages:
        for e in m.embeds:
            if not e.footer:
                continue
            if kid in e.footer.text:
                await m.delete()
                time.sleep(1)


def main():
    bot = commands.Bot(
        command_prefix=commands.when_mentioned,
        description='Post a KSK list from an exported JSON string.',
        help_command=commands.DefaultHelpCommand(
            no_category = 'Commands'
        )
    )

    @bot.command(name='post', help='Post a JSON file or string.')
    async def post(ctx, *, arg=None):
        if arg:
            try:
                data = json.loads(arg)
            except Exception as e:
                data = None
                error = e
        else:
            a = ctx.message.attachments[0]
            try:
                response = requests.get(a.url)
                data = response.json()
            except Exception as e:
                data = None
                error = e
        if not data: # TODO: Send errors as Discord private message maybe
            print(f'Error retrieving or parsing JSON: {error}')
        elif not validate_ksk(data):
            print(f'This did not look like KSK data: {data}')
        else:
            ksk = parse_ksk(data)
            for klist in ksk:
                await delete_old_list(ctx, kid=klist['id'])
                messages=discord_messages(klist)
                for m in messages:
                    await ctx.send(embed=m)
                    time.sleep(1)
            await ctx.message.delete()

    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('Missing DISCORD_TOKEN in environment')
        exit(1)
    bot.run(token)


if __name__ == '__main__':
    main()
