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
        help_command = f.read()
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
    music_count = 0
    def __init__(self, bot):
        self.bot = bot
        self.music_list = []
        self.current_Music_index = 0

    # 봇을 해당 채널에 참여시킵니다. 만약 채널을 지정하지 않을 경우 명령자에 채널로 이동합니다.
    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel=None):
        if channel is None: # 만약 !join으로 호출 했을 경우
            if ctx.author.voice:    # 호출자가 채널에 속해 있다면
                if ctx.voice_client is None:    # 봇이 아무채널에도 속해 있지 않다면 호출자의 채널로 입장시킨다.
                    await ctx.author.voice.channel.connect()
                    return
                if ctx.voice_client is not None:    # 봇이 다른 채널에 속해있다면 호출자의 채널로 이동시킨다.
                    return await ctx.voice_client.move_to(ctx.author.voice.channel)
            elif not ctx.author.voice:  # 호출자가 아무 채널에도 속해있지 않다면 메세지를 보낸다.
                await ctx.send("호출자가 현재 채널에 접속해 있지 않습니다.")
                return

    # 해당 url의 음악을 재생합니다.
    @commands.command()
    async def play(self, ctx, *, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            MusicBot.music_count += 1
            self.music_list.append({"no":MusicBot.music_count,"title":player.title,"url":url,"audio_url":player.url,"music_info":player})
        await ctx.send(f'Now playing: {player.title} Volume:{int(ctx.voice_client.source.volume * 100)}%')

    # 음악의 볼륨을 조절합니다.
    @commands.command()
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    # 음악을 중지시킵니다.
    @commands.command()
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()

    # 플레이리스트의 음악을 출력합니다.
    @commands.command()
    async def list(self, ctx):
        if self.music_list:
            response = "음악 리스트 -\n"
            for i, music in enumerate(self.music_list, start=1):
                title = music.get("title")
                response += f"{i}. 제목: {title}\n"
                await ctx.send(response)
        else:
            await ctx.send("플레이리스트가 비어 있습니다.")

    #플레이 리스트 음악을 추가합니다.
    #list_number 인자에 아무것도 전달되지 않으면 음악은 플레이리스트 마지막에 추가됩니다.
    @commands.command()
    async def add(self, ctx, url, list_number=0):
        # url , list number 체크
        print(f"list number{ list_number}") # Test code
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        if list_number == 0:
            MusicBot.music_count += 1
            self.music_list.append({"no":MusicBot.music_count,"title":player.title,"url":url,"audio_url":player.url,"music_info":player})
            await ctx.send(f"플레이리스트 {MusicBot.music_count}번에 음악을 추가 하였습니다.")
        elif list_number > 0:
            MusicBot.music_count += 1
            self.music_list.insert(list_number-1,{"no":MusicBot.music_count,"title":player.title,"url":url,"audio_url":player.url,"music_info":player})
            await ctx.send(f"플레이리스트 {list_number}번에 음악을 추가 하였습니다.")

    #플레이 리스트 음악을 삭제합니다.
    @commands.command()
    async def remove(self, ctx, list_number):
        if self.music_list:
            if list_number == None:
                target_music_title = self.music_list.pop()
                await ctx.send(f"{target_music_title}를 제거 하였습니다.")
            else:
                self.music_list.remove(list_number)
        else:
            await ctx.send("플레이리스트가 비어있습니다.")

    # 음악이 끝날 때까지 기다린후 Task를 생성해 다음 음악을 재생합니다.
    async def play_next_Music(self, ctx):
        if not ctx.voice_client.is_playing() and self.current_Music_index < self.music_count:
            player = await YTDLSource.from_url(self.music_list[self.current_Music_index]['url'], loop=self.bot.loop,
                                               stream=True)
            ctx.voice_client.play(player, after=lambda e: self.bot.loop.create_task(self.play_next_Music(ctx)))
            self.current_Music_index += 1

    # 플레이리스트 음악을 재생합니다.
    @commands.command()
    async def playlist(self, ctx):
        async with ctx.typing():
            print("MusicCount", self.music_count)
            if self.music_count > 0:
                await self.play_next_Music(ctx)
            print("playlist 끝")

    # 음악 재생을 중지 시킵니다.
    @commands.command()
    async def pause(self, ctx):
        pass

    # 명령어를 출력합니다.
    @commands.command()
    async def cmd(self, ctx):
        if help_command is not None:
            await ctx.send(help_command)
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
