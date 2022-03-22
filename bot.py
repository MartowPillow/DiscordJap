import os
import random
import urllib.request, json 

import discord
from discord.ext import commands

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

TOKEN = "secret"
GUILD1 = "TestBot"
GUILD2 = "COOOOO"

bot = commands.Bot(command_prefix='!')

'''
@bot.event
async def on_error(event, *args, **kwargs):
    message = args[0] #Gets the message object
    logging.warning(traceback.format_exc()) #logs the error
    await bot.send_message(message.channel, "You caused an error!")
'''
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
'''
kana_url = "https://localhost:7113/api/Kana"
url = urllib.request.urlopen(kana_url)
kanas = json.loads(url.read().decode())

page_nb = 1
kanji_url = "https://localhost:7113/api/Kanji?page=" + str(page_nb) + "&kanjiPerPage=10"
url = urllib.request.urlopen(kanji_url)
kanjis = json.loads(url.read().decode())

print("ready")

user_queue = []
res_queue = []
scores = []
high_scores = []
game = []

versus_queue = []
res_versus = "none"
char_versus = "none"
lang_versus = "none"
versus_scores = []
best_versus = 0
best_name_versus = "none"

@bot.command(name="refresh",help="loads new page of kanjis")
async def refresh(context):
    global page_nb
    page_nb = page_nb + 1
    kanji_url = "https://localhost:7113/api/Kanji?page=" + str(page_nb) + "&kanjiPerPage=10"
    url = urllib.request.urlopen(kanji_url)
    global kanjis
    kanjis = json.loads(url.read().decode())
    await context.send("done!")

@bot.command(name="kana",help="ask random kana signification")
async def kana(context):
    curr = random.choice(kanas)
    if(context.message.author in user_queue):
        i = 0
        while (user_queue[i] != context.message.author) :
            i = i + 1
        res_queue[i] = curr["romaji"]
        game[i] = "kana"
    else:
        user_queue.append(context.message.author)
        res_queue.append(curr["romaji"])
        scores.append(0)
        high_scores.append(0)
        game.append("kana")
    await context.send(context.message.author.mention + " what is " + curr["character"] + " ?")

@bot.command(name="kanji",help="ask random kanji meaning")
async def kanji(context):
    curr = random.choice(kanjis)
    if(context.message.author in user_queue):
        i = 0
        while (user_queue[i] != context.message.author) :
            i = i + 1
        res_queue[i] = curr["meanings"]
        game[i] = "kanji"
    else:
        user_queue.append(context.message.author)
        res_queue.append(curr["meanings"])
        scores.append(0)
        high_scores.append(0)
        game.append("kanji")
    await context.send(context.message.author.mention + " what is " + curr["character"] + " ? (" + curr["meaningsLanguage"] + ")")

@bot.command(name="versus",help="begin/join a versus on kanji")
async def versus(context):
    global res_versus
    global char_versus
    global lang_versus
    global best_versus
    global best_name_versus
    if(not context.message.author in versus_queue):
        if(context.message.author in user_queue):
            i = 0
            while (user_queue[i] != context.message.author) :
                i = i + 1
            game[i] = "versus"
            res_queue[i] = "none"
        else:
            game.append("versus")
            user_queue.append(context.message.author)
            res_queue.append("none")
            scores.append(0)
            high_scores.append(0)

        versus_queue.append(context.message.author)
        if(res_versus == "none"):
            curr = random.choice(kanjis)
            char_versus = curr["character"]
            lang_versus = curr["meaningsLanguage"]
            res_versus = curr["meanings"]
            best_versus = 0
            best_name_versus = "none"
        
    await context.send(context.message.author.mention + " what is " + char_versus + " ? (" + lang_versus + ")")

@bot.event
async def on_message(message):
    if(message.author != bot.user and "repeat" in message.content):
        await message.channel.send(message.content)

    global res_versus
    global versus_queue
    global lang_versus
    global char_versus
    global best_name_versus
    global best_versus
    if(message.author in user_queue):
        i = 0
        while (user_queue[i] != message.author) :
            i = i + 1    
        if(res_versus != "none" or res_queue[i] != "none"):
            if(game[i] == "kana"):
                if(message.content == "cheat" or message.content == res_queue[i]):
                    scores[i] = scores[i] + 1
                    curr = random.choice(kanas)
                    res_queue[i] = curr["romaji"]
                    await message.channel.send(message.author.mention + " bravo, what is " + curr["character"] + " ?")
                else:
                    if(scores[i] > high_scores[i]):
                        high_scores[i] = scores[i]
                        await message.channel.send(message.author.mention + " raté, c'était '" + str(res_queue[i]) + "'. New high score: " + str(scores[i]) + '!')
                    else:
                        await message.channel.send(message.author.mention + " raté, c'était '" + str(res_queue[i]) + "'. Score = " + str(scores[i]))
                    scores[i] = 0
                    res_queue[i] = "none"
                    game[i] = "none"
            elif(game[i] == "kanji"):
                if(message.content == "cheat" or message.content in res_queue[i]):
                    scores[i] = scores[i] + 1
                    curr = random.choice(kanjis)
                    res_queue[i] = curr["meanings"]
                    await message.channel.send(message.author.mention + " bravo, what is " + curr["character"] + " ? (" + curr["meaningsLanguage"] + ")")
                else:
                    if(scores[i] > high_scores[i]):
                        high_scores[i] = scores[i]
                        await message.channel.send(message.author.mention + " raté, c'était " + str(res_queue[i]) + ". New high score: " + str(scores[i]) + '!')
                    else:
                        await message.channel.send(message.author.mention + " raté, c'était " + str(res_queue[i]) + ". Score = " + str(scores[i]))
                    scores[i] = 0
                    res_queue[i] = "none"
                    game[i] = "none"


            elif(game[i] == "versus"):
                if(message.content == "cheat" or message.content in res_versus ):
                    scores[i] = scores[i] + 1
                    if(best_versus<scores[i]):
                        best_versus = scores[i]
                        best_name_versus = message.author
                    curr = random.choice(kanjis)
                    char_versus = curr["character"]
                    lang_versus = curr["meaningsLanguage"]
                    res_versus = curr["meanings"]
                    await message.channel.send(message.author.mention + " bravo, what is " + char_versus + " ? (" + lang_versus + ")")
                else:
                    await message.channel.send(message.author.mention + " raté, c'était " + str(res_versus) + ". Tu es éliminé" )
                    versus_queue.remove(message.author)
                    game[i] = "none"
                    scores[i] = 0

                    if(len(versus_queue) == 0):
                        await message.channel.send(best_name_versus.mention + " Tu as gagné ")
                        flag = False
                        for i in range(0,len(versus_scores)):
                            if( best_name_versus.name == versus_scores[i][0]):
                                flag = True
                        if (flag == False or len(versus_scores) == 0):   
                            versus_scores.append([ best_name_versus.name, 1])
                        else:
                            j = 0
                            while best_name_versus.name not in versus_scores[j]:
                                j = j + 1
                            versus_scores[j][1] = versus_scores[j][1] + 1

                        i = 0
                        while (user_queue[i] !=  best_name_versus) :
                            i = i + 1
                        game[i] = "none"
                        res_versus  = "none"
                        scores[i] = 0
                        versus_queue = []


    await bot.process_commands(message)

@bot.command(name="scores",help="print versus scores")
async def versus(context):
    await context.send(str(versus_scores))

bot.run(TOKEN)