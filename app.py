import asyncio, os


import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL


# Bot client create
bot = commands.Bot(command_prefix='!')

bot_status_msg : str = "테스트"

music_queue = []


# 실행시 한번만 동작
@bot.event
async def on_ready():
    print("------> Terminal onStart <---------")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(bot_status_msg))


'''
    Event Listener
'''

# 인사
@bot.command()
async def hello(ctx):
    await ctx.send('Hi there!')

#관리자 권한 확인 !checkAdmin
@bot.command(name='checkAdmin')
async def manger_check(ctx):
    if ctx.guild:
        if ctx.message.author.guild_permissions.administrator:
            await ctx.send(f'{ctx.author.mention}님은 서버의 관리자입니다.')
        else:
            await ctx.send(f'{ctx.author.mention}님은 서버의 관리자가 아닙니다.')
    else:
        await ctx.send('DM으론 불가능합니다.')

# 도움말
@bot.command(name='도움말')
async def help_msg(ctx):
    await ctx.send('도움말 준비중')


#채널 참가
@bot.command(name='입장')
async def join(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        await ctx.author.voice.channel.connect()
        await ctx.send('보이스 채널에 입장했습니다.')
    else:
        await ctx.send('음성채널 없음')


#채널 퇴장
@bot.command(name='퇴장')
async def leave(ctx):
    # 입장중인 방이 있다면 퇴장
    if  bot.voice_clients:
        await ctx.send('안녕히계세요!!')
        await bot.voice_clients[0].disconnect()
    else:
        await ctx.send('현재 참가중인 음성 채널이 없습니다.')


# 음악 리스트 확인
@bot.command(name='list')
async def music_list(ctx):
    if music_queue:
        for i in music_queue:
            pass
    else:
        await ctx.send('음악 목록이 비어 있습니다.')


# 음악 재생
@bot.command(name="play")
async def play_music(ctx, url):

    voice_client = None

    if ctx.message.author.voice.channel:
        voice_channel = ctx.message.author.voice.channel
    else:
        await ctx.send("You are not in a voice channel")
        return

    # 입력한 url이 잘못되었다면
    if url is None:
        await ctx.send('url 형식이 잘못되었습니다.')

    music_queue.append(url)

    #봇이 음성채팅에 참여하지 않았을 경우 참여시킴
    if bot.voice_clients == []:
        voice_client = await voice_channel.connect()
        await ctx.send("connected to the voice channel, " + str(bot.voice_clients[0].channel))


    # 음악 실행
    # if len(music_queue) == 1 and voice_client:
    #     voice_client.play(discord.PCMVolumeTransformer(source))


    #음악 재생 코드



# 봇 실행
if __name__ == "__main__":
    # TOKEN 파일 필요
    try:
        with open("TOKEN", 'r') as f:
            TOKEN = f.readline()
    except FileNotFoundError:
        print("토큰 파일이 없습니다.")
    else:
        bot.run(TOKEN)
