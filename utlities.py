import json
import random
import asyncio
import re

botTokens = None
botOptions = None
with open("./tokens.json") as f:
    botTokens = json.load(f)
with open("./options.json") as f:
    botOptions = json.load(f)    


def shouldSend(bot, msg):
    if (msg.author == bot.user): return False
    if (msg.channel.id not in botOptions["channels"]): return False

    SEND_PROB = botOptions["replyChance"] if (bot.user in msg.mentions) else botOptions["messageChance"]
    return random.randint(1, 100) < SEND_PROB

def generatePrompt(bot, msg):
    msgContent = msg.content
    while True:
        print("msgContent: ", msgContent)
        match = re.search(r"<@(\d+)>", msgContent)
        if match: 
            userId = int(match.group(1))
        username = bot.get_user(userId).name
        newMsgContent = re.sub(r"<@\d+>", username, msgContent, 1)
        if newMsgContent == msgContent: break
        msgContent = newMsgContent
    msgType = ""
    # Determine message type
    if (bot.user in msg.mentions):      msgType = 'reply'
    elif (random.randint(0, 100) > 10): msgType = 'comment'
    else:                               msgType = 'statement'
    match msgType:
        case 'statement':
            return botOptions["prompts"]["statement"].replace("=content=", msgContent)
        case 'comment':
            return botOptions["prompts"]["comment"].replace("=content=", msgContent)
        case 'reply':
            return botOptions["prompts"]["reply"].replace("=content=", msgContent)

async def sendMessage(bot, msg, completion, lock):
    async with lock:
        msgType = ""
        generatedMsg = completion["choices"][0]["text"]
        typingLength = len(generatedMsg) / random.randint(5, 7)
        # Determine message type
        if (bot.user in msg.mentions):      msgType = 'reply'
        elif (random.randint(0, 100) > 10): msgType = 'comment'
        else:                               msgType = 'statement'

        await asyncio.sleep(random.randint(1, 3))
        async with msg.channel.typing():
            await asyncio.sleep(typingLength)
            async with msg.channel.typing():
                if (msgType == 'reply') or (msgType == 'comment'):
                    await msg.reply(generatedMsg)
                else:
                    await msg.channel.send(generatedMsg)