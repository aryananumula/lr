import interactions
import json
import os
from flask import Flask
from threading import Thread
import requests
import ast
from colorama import Fore, Back, Style

app = Flask('')

t = os.environ['lr']
bot = interactions.Client(token=t,
                          intents=interactions.Intents.ALL,
                          auto_defer=True)


@app.route('/')
def main():
  return "Your bot is alive!"


def run():
  app.run(host="0.0.0.0", port=0)


def ka():
  server = Thread(target=run)
  server.start()


model = "openchat/openchat-3.5-1210"
API_URL = "https://api-inference.huggingface.co/models/" + model
headers = {"Authorization": "Bearer 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"}


def query(x):
  x["parameters"] = {"temperature":1}
  x["options"] = {"wait_for_model": True}
  response = requests.post(API_URL, headers=headers, json=x)
  return response.json()


@bot.event
async def on_ready():
  print("Logged in.")


@bot.event
async def on_message_create(message):
  msgchannel = await message.get_channel()
  try:
    guild = await message.get_guild()
    guild_name = guild.name
  except:
    guild_name = "Direct"
    msgchannel.name = message.author.username
  s = f"{Fore.LIGHTGREEN_EX}{message.author.username}#{message.author.discriminator}: {Fore.WHITE}{message.content} {Fore.LIGHTBLUE_EX} {msgchannel.name} {Fore.LIGHTMAGENTA_EX} {guild_name}"
  print(Style.RESET_ALL)
  print(s)
  if not message.author.bot:
    with open("AllowedChannels.py", "r") as f:
      t = ast.literal_eval(f.read())
    if msgchannel.id in t["listening_channels"] or msgchannel.id in t[
        "conversation_channels"]:
      s = f"GPT4 Correct {message.author}: {message.content}<|end_of_turn|>"
      try:
        with open(os.path.join(guild_name, f"{msgchannel.name}.txt"),
                  "a") as f:
          f.write(s)
      except:
        os.mkdir(guild_name)
        with open(os.path.join(guild_name, f"{msgchannel.name}.txt"),
                  "a") as f:
          f.write("GPT4 Correct System: Speak in the same language as the user.")
          f.write(s)
    if msgchannel.id in t["conversation_channels"]:
      with open(os.path.join(guild_name, f"{msgchannel.name}.txt"),
        "a") as f:
        f.write("GPT4 Correct Assistant: ")
      e = await message.reply("*...*")
      with open(os.path.join(guild_name, f"{msgchannel.name}.txt"), "r") as f:
        o = f.read()
      y = query({"inputs": o})
      l = 0
      while not "<|end_of_turn|>" in y[0]["generated_text"][
          len(o):] or "GPT4 Correct" in y[0]["generated_text"][len(o):]:
        l += 1
        await e.edit(y[0]["generated_text"][len(o):])
        py = y[0]["generated_text"]
        y = query({"inputs": y[0]["generated_text"]})
        if y[0]["generated_text"] == py:
          break
      r = y[0]["generated_text"][len(o):].split("<|end_of_turn|>")[0]
      r = r.split("GPT4 Correct")[0]
      with open(os.path.join(guild_name, f"{msgchannel.name}.txt"), "a") as f:
        f.write(r)
      await e.edit(r)


@bot.command(
    name="reset",
    description="Reset the conversation history in the channel.",
    options=[],
)
async def resetConversation(ctx):
  await ctx.defer()
  msgchannel = await ctx.get_channel()
  try:
    guild = await ctx.get_guild()
    guild_name = guild.name
  except:
    guild_name = "Direct"
    msgchannel.name = ctx.author.username
  with open(os.path.join(guild_name, f"{msgchannel.name}.txt"), "w") as f:
    f.write("GPT4 Correct System: Speak in the same language as the user.")
  await ctx.send("Conversation history has been reset.")


@bot.command(
    name="startconversation",
    description=
    "Allows the bot to listen and reply to messages in this channel.",
    options=[],
)
async def startConversation(ctx):
  await ctx.defer()
  msgchannel = await ctx.get_channel()
  with open("AllowedChannels.py", "r") as f:
    t = ast.literal_eval(f.read())
    t["conversation_channels"].append(str(msgchannel.id))
  with open("AllowedChannels.py", "w") as f:
    f.write(str(t))
  await ctx.send("Conversation has started.")


@bot.command(
    name="endconversation",
    description=
    "Makes the bot unable to listen and reply to messages in this channel.",
    options=[],
)
async def endConversation(ctx):
  await ctx.defer()
  msgchannel = await ctx.get_channel()
  try:
    guild = await ctx.get_guild()
    guild_name = guild.name
  except:
    guild_name = "Direct"
    msgchannel.name = ctx.author.username
  with open("AllowedChannels.py", "r") as f:
    t = ast.literal_eval(f.read())
    t["conversation_channels"].remove(str( msgchannel.id ))
  with open("AllowedChannels.py", "w") as f:
    f.write(str(t))
  await ctx.send("Conversation has ended.")


@bot.command(
    name="endlistening",
    description=
    "Makes the bot unable to listen and reply to messages in this channel.",
    options=[],
)
async def endListening(ctx):
  await ctx.defer()
  msgchannel = await ctx.get_channel()
  try:
    guild = await ctx.get_guild()
    guild_name = guild.name
  except:
    guild_name = "Direct"
    msgchannel.name = ctx.author.username
  with open("AllowedChannels.py", "r") as f:
    t = ast.literal_eval(f.read())
    t["listening_channels"].remove(str(msgchannel.id))
  with open("AllowedChannels.py", "w") as f:
    f.write(str(t))
  await ctx.send("Listening has ended.")


@bot.command(
    name="startlistening",
    description=
    "Makes the bot able to listen and reply to messages in this channel.",
    options=[],
)
async def startListening(ctx):
  await ctx.defer()
  msgchannel = await ctx.get_channel()
  try:
    guild = await ctx.get_guild()
    guild_name = guild.name
  except:
    guild_name = "Direct"
    msgchannel.name = ctx.author.username
  with open("AllowedChannels.py", "r") as f:
    t = ast.literal_eval(f.read())
    t["listening_channels"].append(str(msgchannel.id))
  with open("AllowedChannels.py", "w") as f:
    f.write(str(t))
  await ctx.send("Listening has ended.")


ka()
bot.start()
