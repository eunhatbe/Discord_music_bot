# This example requires the 'message_content' privileged intent to function.

import asyncio
import sys

import discord
import yt_dlp as youtube_dl

from discord.ext import commands

# Discord _ TOKEN
try:
    with open("TOKEN", 'r') as f:
        TOKEN = f.read()
except FileNotFoundError:
    print("Failed to open the token file.")
    sys.exit()


try:
    with open("help.txt", "r", encoding="utf-8") as f:
        help_string = f.read()
except Exception as e:
    print(f"An error occurred: {e}")

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


# youtube 음악과 로컬 음악의 재생을 구별하기 위한 클래스 작성.
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


# 음악 재생 클래스. 커맨드 포함.
class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_list = []

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            self.music_list.append(player.title)

        await ctx.send(f'Now playing: {player.title} Volume:{int(ctx.voice_client.source.volume * 100)}%')

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @commands.command()
    async def list(self, ctx):
        if self.music_list:
            response = "음악 리스트 -\n"
            for i, music in enumerate(self.music_list, start=1):
                response += f"{i}. {music}\n"
                await ctx.send(response)
        else:
            await ctx.send("음악 리스트가 비어 있습니다.")

    @commands.command()
    async def pause(self, ctx):
        pass

    # Help
    @commands.command()
    async def cmd(self, ctx):
        if help_string is not None:
            await ctx.send(help_string)
        else:
            await ctx.send("도움말 오류")


    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description='Relatively simple music bot example',
    intents=intents,
)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


async def main():
    async with bot:
        await bot.add_cog(MusicBot(bot))
        await bot.start(TOKEN)


asyncio.run(main())
