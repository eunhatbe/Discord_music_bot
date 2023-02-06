import asyncio

import discord
from discord.ext import commands


# Bot client create
bot = commands.Bot(command_prefix='!')

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



@bot.command()
async def ping(ctx):
    await ctx.send('pong')

#관리자 권한 확인 !checkAdmin
@bot.command(name='checkAdmin')
async def mangerCheck(ctx):
    if ctx.guild:
        if ctx.message.author.guild_permissions.administrator:
            await ctx.send(f'{ctx.author.mention}님은 서버의 관리자입니다.')
        else:
            await ctx.send(f'{ctx.author.mention}님은 서버의 관리자가 아닙니다.')
    else:
        await ctx.send('DM으론 불가능합니다.')


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
