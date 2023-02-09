import asyncio

import discord
from discord.ext import commands


# Bot client create
bot = commands.Bot(command_prefix='!')


music_queue = []




# 실행시 한번만 동작
@bot.event
async def on_ready():
    print("------> Terminal onStart <---------")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("테스트"))

'''
    Event Listener
'''

# @bot.event
# async def on_message(message):
#     # 봇 자신이 한 대답이면 반응하지 않음
#     if message.author.bot:
#         return
#
#     if message.content.startswith("hello"):
#         print("debug")
#         channel = message.channel
#
#         print(channel)
#         await channel.send("Hello hi!!")
#         # await message.author.send(f"{message.author} | {message.author.mention}, User, Hello")
#
#     def check(m):
#         return m.content == 'hello' and m.channel == channel
#
#     if message.content == "특정입력":
#         ch = bot.get_channel(769416844008095748)
#         await ch.send("테스트입니다.")



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
        pass


# 음악 리스트 확인
@bot.command(name='list')
async def music_list(ctx):
    if music_queue:
        for i in music_queue:
            pass
    else:
        await ctx.send('음악 목록이 비어 있습니다.')



















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
