import openai
import asyncio
from discord.ext import commands
import json
from utlities import shouldSend, generatePrompt, sendMessage

bot = commands.Bot(command_prefix='>', self_bot=True)
botTokens = None
with open("./tokens.json") as f:
    botTokens = json.load(f)

userToken = botTokens["userToken"]
openai.api_key = botTokens["openAIToken"]

@bot.event
async def on_ready():
  print('Logged in as')
  print(bot.user.name)
  print(bot.user.id)
  print('------')

messageSemaphore = asyncio.Semaphore(2)
@bot.event
async def on_message(msg):
    if messageSemaphore.locked(): return
    await messageSemaphore.acquire()
    try:
        if (shouldSend(bot, msg)):
            completion = openai.Completion.create(
                model="text-davinci-003",
                prompt=generatePrompt(bot, msg),
                temperature=0.7,
                max_tokens=100,
                frequency_penalty= 1,
                presence_penalty= .8,
            )
            lock = asyncio.Lock()
            await sendMessage(bot, msg, completion, lock)
    finally:
        messageSemaphore.release()

bot.run(userToken)