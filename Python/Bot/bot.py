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
from cassiopeia import Summoner, Champion, Champions, Items, Item

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
api_key = apiHolder.key
cassiopeia.set_riot_api_key(api_key)
lol_watcher = LolWatcher(api_key)

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


async def getRankedData(username, user_reg, message):
    region = user_reg
    if user_reg == "OCE":
        region = 'oc1'
    elif user_reg == "NA":
        region = 'na1'

    # try query data with given arguments
    try:
        User = lol_watcher.summoner.by_name(region, username)
    except ApiError as err:
        if err.response.status_code == 404:
            await message.channel.send("There is noone in that region with that name")
        else:
            await message.channel.send("An error has occurred")
    else:
        ranked_stats = lol_watcher.league.by_summoner(region, User['id'])
        solo_q = [stats for stats in ranked_stats if stats['queueType'] == 'RANKED_SOLO_5x5'][0]
        tier, rank, wins, losses = solo_q['tier'], solo_q['rank'], solo_q['wins'], solo_q['losses']
        total = solo_q['wins'] + solo_q['losses']

        text = ''.join([solo_q['summonerName'], "\n", tier, " ", rank, "\n", "Wins: ", str(wins), "\n",
                        "Losses: ", str(losses) + "\n" + "Win Rate: ", str(round(wins / total * 100)) + "%"])

        await message.channel.send(text)


async def getItem(itemName, message):
    item = Item(name=itemName, region='NA')
    itemImage = getItemURL(item.id)
    #use regex to remove tags in item description

    pattern = r'>([^<]+)<'
    itemDesc = item.description
    itemDesc = re.sub("<br>", "\n", itemDesc)
    itemDesc = re.sub("<li>", "\n", itemDesc)
    itemDesc = "".join(re.findall(pattern, itemDesc))
    embed = discord.Embed(title=item.name, description=itemDesc)
    embed.set_thumbnail(url=itemImage)
    await message.channel.send(embed=embed)




async def getChampionSpells(champion, message):
    # instantiate Champion object that holds data of specific champion
    champ = Champion(name=champion, region='NA')
    champImage = getChampURL(champ.key)

    passiveImage, passiveKey = getPassiveURL(champ.key)
    emoji = await createEmoji(message, passiveImage, passiveKey)
    text = f"{emoji} **{champ.passive.name} [PASSIVE]**: {champ.passive.description} \n\n"

    for ability in champ.spells:
        abilityImage = getAbilityURL(ability.key)
        emoji = await createEmoji(message, abilityImage, ability.key)
        text += f"{emoji} **{ability.name} [{ability.keyboard_key.name}]**: {ability.description} \n\n"

    embed = discord.Embed(title=champ.name, description=text)
    embed.set_image(url=champImage)
    await message.channel.send(embed=embed)


async def createEmoji(message, URL, key):
    emoji = get(message.guild.emojis, name=key)
    if emoji is None:
        img = urlopen(URL).read()
        await message.guild.create_custom_emoji(name=key, image=img)
        emoji = get(message.guild.emojis, name=key)

    return emoji


def getChampURL(champ_key):
    return f"http://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ_key}_0.jpg"


def getPassiveURL(champ_key):
    http = urllib3.PoolManager()
    fileLink = f"http://ddragon.leagueoflegends.com/cdn/12.18.1/data/en_US/champion/{champ_key}.json"
    r = http.request('GET', fileLink, fields={'arg': 'value'})
    passiveKey = json.loads(r.data.decode('utf-8'))["data"][champ_key]["passive"]["image"]["full"]
    return "http://ddragon.leagueoflegends.com/cdn/12.18.1/img/passive/" + passiveKey, passiveKey.strip(".png")


def getAbilityURL(ability_key):
    return f"http://ddragon.leagueoflegends.com/cdn/12.18.1/img/spell/{ability_key}.png"


def getItemURL(item_key):
    return f"http://ddragon.leagueoflegends.com/cdn/12.18.1/img/item/{item_key}.png"


async def champMastery(username, user_reg, message):
    masteryLevel = message[-1]
    champs = Summoner(name=username, region=user_reg).champion_masteries.filter(lambda cm: cm.level >= masteryLevel)
    await message.channel.send(", ".join([cm.champion.name for cm in champs]))


async def loldle(content, message):
    def check(message):
        return message.content.startswith("$guess") or message.content.startswith("$quit")

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


client.run(TOKEN)
