import os
import discord
import asyncio
from discord.ext import commands
from config import TOKEN, AFK_CHANNEL_ID

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store timers for each user
user_timers = {}

# Music folder path
MUSIC_FOLDER = 'music'
MUSIC_FILE = 'music/song.mp3'

async def move_to_afk(member, afk_channel):
    try:
        await member.move_to(afk_channel)
        print(f"Moved {member} to AFK channel")
        await member.send("goodnight darling <3")
        print(f"Sent DM to {member}")
    except discord.Forbidden:
        print(f"Cannot move {member} to AFK channel or send DM: insufficient permissions")
    except Exception as e:
        print(f"Error moving {member}: {e}")

async def afk_timer(member, afk_channel, delay=420):  # 7 minutes = 420 seconds
    await asyncio.sleep(delay)
    if member.id in user_timers:
        del user_timers[member.id]
        await move_to_afk(member, afk_channel)

@bot.command()
async def join_afk(ctx):
    afk_channel = bot.get_channel(AFK_CHANNEL_ID)
    if afk_channel is None:
        await ctx.send("AFK channel not found")
        return

    # Check if bot is already in the channel
    vc = None
    for client_vc in bot.voice_clients:
        if client_vc.channel == afk_channel:
            vc = client_vc
            break

    if vc is None:
        vc = await afk_channel.connect()
        await ctx.send(f"Joined AFK channel: {afk_channel.name}")
    else:
        await ctx.send("Already in AFK channel")

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    afk_channel = bot.get_channel(AFK_CHANNEL_ID)
    if afk_channel is None:
        print("AFK channel not found")
        return

    # If user joins the AFK channel, send a message
    if after.channel == afk_channel and before.channel != afk_channel:
        # لا نرسل رسالة للبوت نفسه
        if not member.bot:
            try:
                await member.send("goodnight darling <3")
                print(f"Sent welcome message to {member}")
            except discord.Forbidden:
                print(f"Cannot send DM to {member}: insufficient permissions")
            except Exception as e:
                print(f"Error sending DM to {member}: {e}")

    # If user leaves the AFK channel, check if channel is empty and disconnect bot
    elif before.channel == afk_channel and after.channel != afk_channel:
        # Check if channel is empty (only bot or no one)
        members_in_channel = [m for m in afk_channel.members if not m.bot]
        if len(members_in_channel) == 0:
            # Disconnect bot
            for vc in bot.voice_clients:
                if vc.channel == afk_channel:
                    await vc.disconnect()
                    print(f"Disconnected from AFK channel: {afk_channel.name}")
                    break

    # If user joins a voice channel (not AFK)
    if before.channel is None and after.channel is not None and after.channel != afk_channel:
        if member.id in user_timers:
            user_timers[member.id].cancel()
        user_timers[member.id] = bot.loop.create_task(afk_timer(member, afk_channel))

    # If user leaves voice channel
    elif before.channel is not None and after.channel is None:
        if member.id in user_timers:
            user_timers[member.id].cancel()
            del user_timers[member.id]

    # If user changes voice state (mute, deafen, etc.) - reset timer
    elif before.channel == after.channel and before != after and before.channel != afk_channel:
        if member.id in user_timers:
            user_timers[member.id].cancel()
        user_timers[member.id] = bot.loop.create_task(afk_timer(member, afk_channel))

bot.run(TOKEN)
