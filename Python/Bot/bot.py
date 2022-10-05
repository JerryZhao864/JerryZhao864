# bot.py
import os
import re
import cassiopeia
import discord
from discord.utils import get
import urllib3
import json
from urllib.request import urlopen

import apiHolder  # holds api_key
import random
from dotenv import load_dotenv
from riotwatcher import LolWatcher, ApiError
from cassiopeia import Summoner, Champion, Champions, Items, Item, Role, Match

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
api_key = apiHolder.key
cassiopeia.set_riot_api_key(api_key)
lol_watcher = LolWatcher(api_key)
client = discord.Client()

matchRouting = {'NA': 'AMERICAS',
                'BR': 'AMERICAS',
                'LAN': 'AMERICAS',
                'LAS': 'AMERICAS',
                'KR': 'ASIA',
                'JP': 'ASIA',
                'EUNE': 'EUROPE',
                'EUW': 'EUROPE',
                'TR': 'EUROPE',
                'RU': 'EUROPE',
                'OCE': 'SEA'}

serverConversion = {'OCE': 'oc1',
                    "NA": 'na1',
                    "EUW": 'euw1',
                    "BR": 'br1',
                    "EUNE": 'eun1',
                    "JP": 'jp1',
                    "KR": "KR"}


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


async def getRankedData(username, user_reg):
    playerProfile = {}
    # request user data and ranked stats based off user id
    User = lol_watcher.summoner.by_name(serverConversion[user_reg], username)
    ranked_stats = lol_watcher.league.by_summoner(serverConversion[user_reg], User['id'])
    # store all stats that are from ranked solo matches
    solo_q = [stats for stats in ranked_stats if stats['queueType'] == 'RANKED_SOLO_5x5'][0]
    playerProfile["tier"] = solo_q['tier']
    playerProfile["rank"] = solo_q['rank']
    playerProfile["wins"] = solo_q['wins']
    playerProfile["losses"] = solo_q['losses']

    return playerProfile


def playedRecently(name, region):
    player = Summoner(name=name, region=region)

    champCount = {}
    recentMatch = {}
    matchCount = 0
    # Have to differentiate between OCE and other regions as cassiopeia as an error with querying OCE matches

    match_history = lol_watcher.match.matchlist_by_puuid(puuid=player.puuid, region=matchRouting[region])
    for matchID in match_history:
        match = lol_watcher.match.by_id(region=matchRouting[region], match_id=matchID)
        for participant in match['info']['participants']:
            if participant['summonerName'] == name:
                if matchCount == 0:
                    if participant['win']:
                        recentMatch['outcome'] = 'Win'
                    else:
                        recentMatch['outcome'] = 'Loss'

                    recentMatch['lane'] = participant['individualPosition'].title()
                    recentMatch['champion'] = participant['championId']
                    recentMatch['stats'] = f"{participant['kills']}/{participant['deaths']}/{participant['assists']}"

                if participant['championId'] in champCount:
                    champCount[participant['championId']] += 1
                else:
                    champCount[participant['championId']] = 1
        matchCount += 1

    sortedChampCount = [(champ, count) for champ, count in sorted(champCount.items(),
                                                                  key=lambda item: item[1], reverse=True)]
    return sortedChampCount[0:5], recentMatch


# Request data (ranked, most played, highest mastery) for specific player and output it
async def getProfile(player, region, message):
    playerData = await getRankedData(player, region)
    playerMastery = champMastery(player, region)
    recentChamps, recentGame = playedRecently(player, region)

    masteryText = ""
    champText = ""
    # Format text for both mastery text and champ text using the top 5 highest champs
    for i in range(5):
        # For each champion, create an emoji using champion's web api URL and format output text
        masteryChamp = playerMastery[i]
        champObj = Champion(id=masteryChamp[1], region='NA')
        iconURL = getChampIcon(champObj.image.full)
        emojiName = champObj.name.replace(" ", "")
        emojiName = emojiName.replace("'", "")
        iconEmoji = await createEmoji(message, iconURL, emojiName)
        masteryText += f"**[{masteryChamp[0]}]** {iconEmoji} {champObj.name}: {masteryChamp[2]}\n"

        recentChamp = recentChamps[i]
        champObj = Champion(id=recentChamp[0], region='NA')
        iconURL = getChampIcon(champObj.image.full)
        emojiName = champObj.name.replace(" ", "")
        emojiName = emojiName.replace("'", "")
        iconEmoji = await createEmoji(message, iconURL, emojiName)
        champText += f"**{i + 1}.** {iconEmoji} {champObj.name} ({recentChamp[1]} games)\n"

    # set text for ranked data
    winRate = round((playerData['wins'] / (playerData['wins'] + playerData['losses'])) * 100)
    rankEmoji = get(message.guild.emojis, name=playerData['tier'].title())
    rankedText = f"{rankEmoji} {playerData['tier']} {playerData['rank']} | Winrate: {winRate}%" \
                 f" ({playerData['wins']}W/{playerData['losses']}L)"

    # set text for the recent game
    if recentGame['outcome'] == 'Win':
        outcomeEmoji = "✓"
    else:
        outcomeEmoji = "✘"

    # create champ emoji
    champObj = Champion(id=recentGame['champion'], region='NA')
    iconURL = getChampIcon(champObj.image.full)
    emojiName = champObj.name.replace(" ", "")
    emojiName = emojiName.replace("'", "")
    champEmoji = await createEmoji(message, iconURL, emojiName)

    laneEmoji = get(message.guild.emojis, name=recentGame['lane'] + "_icon")
    recentGameText = f"{outcomeEmoji} {laneEmoji} {recentGame['outcome']} as {champEmoji} {champObj.name} | " \
                     f"{recentGame['stats']}"

    # Instantiate the Embed object and add field descriptions
    p1Embed = discord.Embed(title=f"{player} ({region})")

    p1Embed.add_field(name="Rank", value=rankedText, inline=False)
    p1Embed.add_field(name="Highest Mastery", value=masteryText)
    p1Embed.add_field(name="Most Played Recently (20 Games)", value=champText)
    p1Embed.add_field(name="Most Recent Game", value=recentGameText, inline=False)

    botMessage = await message.channel.send(embed=p1Embed)
    await botMessage.add_reaction("1️⃣")
    await botMessage.add_reaction("2️⃣")

    '''def check(reaction):
        return str(reaction.emoji) in validReactions

    reaction = await client.wait_for('reaction_add', check=check)
    if str(reaction.emoji) == validReactions[0]:
    '''

    return


# Finds item description and effects
async def getItem(itemName, message):
    item = Item(name=itemName, region='NA')
    itemImage = getItemURL(item.id)
    # use regex to remove tags in item description
    pattern = r'>([^<]+)<'
    itemDesc = item.description
    itemDesc = re.sub("<br>", "\n", itemDesc)
    itemDesc = re.sub("<li>", "\n", itemDesc)
    itemDesc = "".join(re.findall(pattern, itemDesc))
    goldEmoji = get(message.guild.emojis, name="Currency")
    embed = discord.Embed(title=f"{item.name} {item.gold.total} {goldEmoji}", description=itemDesc)
    embed.set_thumbnail(url=itemImage)
    await message.channel.send(embed=embed)
    return


# Get the passive and abilities of a champion and send them as an embedded message
async def getChampionSpells(champion, message):
    # instantiate Champion object that holds data of specific champion
    champ = Champion(name=champion, region='NA')
    champImage = getChampURL(champ.key)

    # create emoji for passive image
    passiveKey = champ.passive.image_info.full.strip('.png')
    passiveImage = getPassiveURL(passiveKey)
    emoji = await createEmoji(message, passiveImage, passiveKey)
    text = f"{emoji} **{champ.passive.name} [PASSIVE]**: {champ.passive.description} \n\n"

    # create emojis for each ability and add formatted text to final output
    for ability in champ.spells:
        abilityImage = getAbilityURL(ability.key)
        emoji = await createEmoji(message, abilityImage, ability.key)
        text += f"{emoji} **{ability.name} [{ability.keyboard_key.name}]**: {ability.description} \n\n"

    # instantiate Embed message and set fields
    embed = discord.Embed(title=champ.name, description=text)
    embed.set_image(url=champImage)
    await message.channel.send(embed=embed)


# Create custom emoji if the emoji key does not already exist
async def createEmoji(message, URL, key):
    emoji = get(message.guild.emojis, name=key)
    if emoji is None:
        img = urlopen(URL).read()
        await message.guild.create_custom_emoji(name=key, image=img)
        emoji = get(message.guild.emojis, name=key)
    return emoji


# Returns a user's champions with mastery level higher than 6
def champMastery(username, user_reg):
    champs = Summoner(name=username, region=user_reg).champion_masteries.filter(lambda cm: cm.level >= 6)
    return [(cm.level, cm.champion.id, cm.points) for cm in champs]


# Wordle Minigame for League Items or Champions
async def loldle(content, message):
    def check(user_msg):
        return user_msg.content.startswith("$guess") or user_msg.content.startswith("$quit")

    tries = 0
    posLetters = "a b c d e f g h i j k l m n o p q r s t u v w x y z"
    contentList = getContentList(content)
    chosenWord = random.choice(contentList)
    output = ""
    for char in chosenWord:
        if char != " ":
            output += ":white_large_square: "
        else:
            output += "  "
    await message.channel.send(output)
    print(chosenWord)

    while tries < 5:
        message = await client.wait_for('message', check=check)
        guess = message.content.lower()
        guess = guess.split()

        attempt = guess[1]

        while len(attempt) != len(chosenWord) and attempt != "$quit":
            if len(attempt) != len(chosenWord):
                await message.channel.send("Your attempted guess was the incorrect length")

            message = await client.wait_for('message', check=check)
            guess = message.content.lower()
            guess = guess.split()
            attempt = guess[1]

        if attempt == "$quit":
            await message.channel.send("The game has been aborted")
            return

        output = ""
        correctGuess = True

        for i in range(len(chosenWord)):
            if attempt[i] != chosenWord[i]:
                correctGuess = False
                if attempt[i] in chosenWord:
                    output += ":yellow_square: "
                else:
                    # if letter not in chosenWord
                    output += ":red_square: "
                    if " " + attempt[i] + " " in posLetters:
                        posLetters = posLetters.replace(attempt[i], "~~" + attempt[i] + "~~")
            else:
                output += ":green_square: "

        await message.channel.send(output + "\n" + posLetters)
        if correctGuess:
            break
        tries += 1

    if correctGuess:
        await message.channel.send("Congratulations you have guessed the correct word!")
    else:
        await message.channel.send("Unfortunately you have not guessed the correct word!")


def getContentList(content):
    if content == "champions":
        champions = Champions(region="NA")
        return [champion.name.lower() for champion in champions]

    elif content == "items":
        items = Items(region="NA")
        return [item.name.lower() for item in items]


def getChampURL(champ_key):
    return f"http://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ_key}_0.jpg"


def getChampIcon(champ_key):
    return f"http://ddragon.leagueoflegends.com/cdn/12.18.1/img/champion/{champ_key}"


def getPassiveURL(passive_key):
    return f"http://ddragon.leagueoflegends.com/cdn/12.18.1/img/passive/{passive_key}.png"


def getAbilityURL(ability_key):
    return f"http://ddragon.leagueoflegends.com/cdn/12.18.1/img/spell/{ability_key}.png"


def getItemURL(item_key):
    return f"http://ddragon.leagueoflegends.com/cdn/12.18.1/img/item/{item_key}.png"


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    contentList = message.content.split(' ')

    if message.content.startswith('$ranked'):
        await getRankedData(" ".join(contentList[1:-1]), contentList[2], message)

    elif message.content.startswith("$champ"):
        try:
            await getChampionSpells(" ".join(contentList[1:]), message)
        except IndexError:
            await message.channel.send("The command did not have the right number of arguments")

    elif message.content.startswith("$mastery"):
        try:
            await champMastery(" ".join(contentList[1:-1]), contentList[2], contentList[3], message)
        except IndexError:
            await message.channel.send("The command did not have the right number of arguments")

    elif message.content.startswith("$loldle"):
        await loldle(contentList[1], message)

    elif message.content.startswith("$item"):
        await getItem(" ".join(contentList[1:]), message)

    elif message.content.startswith("$profile"):
        await getProfile(contentList[1], contentList[2], message)


client.run(TOKEN)
