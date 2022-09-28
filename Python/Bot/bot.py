# bot.py
import os

import cassiopeia
import discord
from discord import channel

import apiHolder  # holds api_key

from dotenv import load_dotenv
from riotwatcher import LolWatcher, ApiError
from cassiopeia import Summoner, Champion, Queue, Match

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


async def getChampionSpells(champion, message):
    champ = Champion(name=champion, region='NA')
    champ_image = "http://ddragon.leagueoflegends.com/cdn/img/champion/splash/" + champ.key + "_0.jpg"
    text = "**" + champ.passive.name + " [PASSIVE]" + "**" + ": " + champ.passive.description + "\n\n"

    for spell in champ.spells:
        text += "**" + spell.name + " [" + spell.keyboard_key.name + "]" + "**" ": " + spell.description + "\n\n"

    embed = discord.Embed(title=champ.name, description=text)
    embed.set_image(url=champ_image)
    await message.channel.send(embed=embed)


async def champMastery(username, user_reg, message):
    masteryLevel = message[-1]
    champs = Summoner(name=username, region=user_reg).champion_masteries.filter(lambda cm: cm.level >= masteryLevel)
    await message.channel.send(", ".join([cm.champion.name for cm in champs]))


async def getBestPlayer(message):
    # joke
    embed = discord.Embed(title="Best Player (read: Worst Player)",
                          description="https://oce.op.gg/summoners/oce/xxtheloneincelxx")
    file = discord.File("IMG_1608.jpg")
    embed.set_image(url="attachment://IMG_1608.jpg")
    await message.channel.send(embed=embed, file=file)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$ranked'):
        contentList = message.content.split(' ')
        await getRankedData(" ".join(contentList[1:-1]), contentList[2], message)

        # print(output)
        # if output:
        #     newList = "\n".join(output)
        #     await message.channel.send(newList)
        # else:
        #     print(" ".join(contentList[1:-1]))
        #     await message.channel.send((" ".join(contentList[1:-1]) + 'has not played enough games'))

    elif message.content.startswith("$champ"):
        contentList = message.content.split(' ')
        await getChampionSpells(contentList[1], message)

    elif message.content.startswith("$bestplayer"):
        await getBestPlayer(message)

    elif message.content.startswith("$mastery"):
        contentList = message.content.split(' ')
        await champMastery(" ".join(contentList[1:-1]), contentList[2], message)


client.run(TOKEN)
