# KSK Classic Discord Bot
For Classic WoW guilds using the Konfer Suicide Kings loot system, this bot can post exported JSON results from the KSK addon to Discord.

The intent of this bot is to allow easy viewing of KSK positions for guild members, which should also reduce the overhead and complexity for raid leaders/loot masters of needing to keep the addon in sync whenever guild members want to see their KSK positions.

## Installation
[Click here](https://discord.com/api/oauth2/authorize?client_id=807655262961532938&permissions=26624&scope=bot) to add to your Discord server.

## Usage

Mention the bot user `@KSK` in a channel it has access to followed by one of the available commands.

Command List:
```
@KSK post - Copy and paste the string provided by the KSK addon following this command.

@KSK help - Displays the Discord bot help message.
```

If Discord tells you that your message is too large, simply click the **Upload** button when prompted. The bot can handle KSK data either directly in the message or accompanied by an uploaded text file.

### Getting the string

You must be a designated admin user in your guild's KSK system in order to export data.

>Select the **Export** button in the **Config** tab.
![](images/ksk1.jpg)


>Export either a single list (selected in the previous screen), or all your KSK lists, as **JSON**.
![](images/ksk2.jpg)


## Links and Notices

[Konfer Suicide Kings (KSK) for Classic WoW](https://www.curseforge.com/wow/addons/ksk-classic)

<sub>World of Warcraft®
©2004 Blizzard Entertainment, Inc. All rights reserved. World of Warcraft, Warcraft and Blizzard Entertainment are trademarks or registered trademarks of Blizzard Entertainment, Inc. in the U.S. and/or other countries.</sub>
