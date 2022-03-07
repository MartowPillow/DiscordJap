import os
import random
import urllib.request, json 

import discord
from discord.ext import commands

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

TOKEN = "OTUwMzg4MDA2OTExNjIzMjM4.YiYLzg.X9v7HEC4haft6JFe3mjfLYel-6Q"
GUILD1 = "TestBot"
GUILD2 = "COOOOO"

bot = commands.Bot(command_prefix='!')

'''
@bot.event
async def on_command_error(context, error):
    await context.send(error)
'''

@bot.command(name='start', help="starts the game")
async def start(context):
    await context.send("c'est parti!" + str(context.message.author.mention) + '(' + str(context.message.author) + ')')
    
@bot.command(name='d', help="roll dice (give number of faces then number of dice)")
async def roll_dice(context, nb_face: int, nb_dice: int =1):
    rep = ""
    sum = 0
    max = 0
    for i in range(0, nb_dice):
        res = random.choice(range(1, nb_face + 1))
        if(max < res): max = res
        sum += res
        rep += str(res) + (', ' if (i < nb_dice - 1) else '') 
    if(nb_dice > 1): rep += ", sum=" + str(sum) + '/' + str(nb_dice*nb_face) + ", max=" + str(max)
    await context.send(rep)

@bot.command(name="fetch",help="fetch url and prints content")
async def fetch(context, urltxt = "https://api.thecatapi.com/v1/images/search"):
    with urllib.request.urlopen(urltxt) as url:
        data = json.loads(url.read().decode())
        await context.send(data)

waiting = "none"

@bot.command(name="kana",help="ask random kana signification")
async def kana(context):
    kana_url = "https://localhost:7113/api/Kana"
    global waiting
    with urllib.request.urlopen(kana_url) as url:
        kanas = json.loads(url.read().decode())
        curr = random.choice(kanas)
        waiting = [context.message.author, curr["romaji"]]
        await context.send("what is " + curr["character"] + " ?")

@bot.event
async def on_message(message):
    if(message.author != bot.user and "repeat" in message.content):
        await message.channel.send(message.content)
    global waiting
    if(waiting != "none" and message.author == waiting[0]):
        if(message.content == waiting[1]):
            await message.channel.send("bravo")
        else:
            await message.channel.send("raté, c'était " + waiting[1])
        waiting = "none"

    await bot.process_commands(message)

bot.run(TOKEN)