import os
import discord
import asyncio
from discord.ext import commands
from config import TOKEN, AFK_CHANNEL_ID
from yt_dlp import YoutubeDL

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store timers for each user
user_timers = {}

# YouTube music URL
YOUTUBE_URL = "https://www.youtube.com/watch?v=Y4tkItZR7Iw"

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

async def join_and_play_music(afk_channel):
    """Bot joins voice channel and plays YouTube music"""
    try:
        # Check if bot is already in the channel
        vc = None
        for client_vc in bot.voice_clients:
            if client_vc.channel == afk_channel:
                vc = client_vc
                break
        
        # Connect to channel if not already connected
        if vc is None:
            vc = await afk_channel.connect()
            print(f"Bot connected to voice channel: {afk_channel.name}")
        
        # Wait for connection to stabilize
        await asyncio.sleep(1)
        
        # Don't play if already playing
        if vc.is_playing():
            print("Music is already playing")
            return
        
        # Extract audio URL from YouTube
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
        }
        
        print("Preparing music from YouTube...")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(YOUTUBE_URL, download=False)
            audio_url = info['url']
        
        # Play the music
        audio_source = discord.FFmpegPCMAudio(
            audio_url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn"
        )
        vc.play(audio_source, after=lambda e: print("Music finished" if e is None else f"Error: {e}"))
        print("Now playing music from YouTube...")
        
    except Exception as e:
        print(f"Error playing music: {e}")

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

    # If user joins the AFK channel, send a message and play music
    if after.channel == afk_channel and before.channel != afk_channel:
        # Don't send message to bot
        if not member.bot:
            try:
                await member.send("goodnight darling <3")
                print(f"Sent welcome message to {member}")
            except discord.Forbidden:
                print(f"Cannot send DM to {member}: insufficient permissions")
            except Exception as e:
                print(f"Error sending DM to {member}: {e}")
        
        # Bot joins and plays music only if a real user joined
        if not member.bot:
            print(f"{member} joined AFK channel, bot is now joining...")
            await join_and_play_music(afk_channel)

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
