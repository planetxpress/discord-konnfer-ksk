import discord
import json
import os
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

    Parameters: data (dict): KSK JSON data.
    Returns: True if data is valid. False if not valid.
    '''
    try:
        if all (
            k in data['ksk'] for k in (
                'classes',
                'date',
                'lists',
                'time',
                'users'
            )
        ):
            return True
        else:
            return False
    except KeyError:
        return False


def discord_messages(klist):
    '''
    Creates a Discord embedded message with a given KSK list.
    Paginate messages to work within Discord imposed constraints:
     - 2000 characters (computer characters, not WoW characters =D) per message
     - 1024 characters per embed field.

    Parameters: klist (list): A single KSK list to post to Discord.
    Returns: messages (list): List of Discord message embed objects.
    '''
    messages = list()
    index = 0
    paginate = 50
    while index <= len(klist['characters']):
        m = discord.Embed(
            title=klist['name'],
            type='rich'
        )
        m.set_thumbnail(url='https://i.imgur.com/xK7nbVL.jpg')
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
        messages.append(m)
        index += paginate
    return messages


def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('Missing DISCORD_TOKEN in environment')
        exit(1)
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
                print(e)
                print(f'Could not parse KSK JSON data.')
                return
            if not validate_ksk(data):
                print(f'Could not parse KSK JSON data.')
                return
            ksk = parse_ksk(data)
            for klist in ksk:
                messages=discord_messages(klist)
                for m in messages:
                    await ctx.send(embed=m)
                    time.sleep(1)
        else:
            for a in ctx.message.attachments:
                try:
                    response = requests.get(a.url)
                    data = response.json()
                except Exception as e:
                    print(e)
                    print(f'Could not parse KSK JSON data at {a.url}.')
                    continue
                if not validate_ksk(data):
                    print(f'Could not parse KSK JSON data.')
                    continue
                ksk = parse_ksk(data)
                for klist in ksk:
                    messages=discord_messages(klist)
                    for m in messages:
                        await ctx.send(embed=m)
                        time.sleep(1)
        await ctx.message.delete() 

    bot.run(token)

if __name__ == '__main__':
    main()
