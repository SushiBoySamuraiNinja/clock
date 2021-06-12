import discord
import asyncio
import time
import datetime
import subprocess
import os
#from discord.ext import tasks


TOKEN = os.environ['DISCORD_BOT_TOKEN']
client = discord.Client()

class Jtalk:
    global client
    open_jtalk=['open_jtalk']
    mech=['-x','/var/lib/mecab/dic/open-jtalk/naist-jdic']
    htsvoice=['-m','/usr/share/hts-voice/mei/mei_normal.htsvoice']
    speed=['-r','1.0']
    outwav=['-ow','open_jtalk.wav']

    allpass=["-a","1.0"]

    flag_allpass = False
    
    async def Talk(self,t,talker):
        cmd=self.open_jtalk+self.mech+self.htsvoice+self.speed+self.outwav
        if self.flag_allpass == True:
            cmd += self.allpass
        
        string = t.split("\n")
        print(string)
        for i in string:
            terminal = subprocess.Popen(cmd,stdin=subprocess.PIPE)
            terminal.stdin.write(i.encode())
            terminal.stdin.close()
            terminal.wait()
            Guild = client.get_guild(talker)
            while Guild.voice_client.is_playing():
                await asyncio.sleep(1)
            Guild.voice_client.play(discord.FFmpegPCMAudio("open_jtalk.wav"))
        return

    def Speed(self,n=None):
        if n == None:
            s = 1.0
        if n > 0.0:
            s = n
        else:
            s = 1.0
        self.speed[1] = str(s)
        return
    
    def Allpass(self,n=None):
        if n == None:
            a = 1.0
            self.flag_allpass = False
        if n >= 0.0 and n <= 1.0:
            a = n
            self.flag_allpass = True
        else:
            a = 1.0
            self.flag_allpass = False
        self.allpass[1] = str(a)
        return

TALK = Jtalk()

VOICE_FLAG = False

#MUSIC1 = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source="open_jtalk.wav"), volume=0.4)
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

@client.event
async def on_message(message):
    global MUSIC1
    global VOICE_FLAG
    global TALK
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    elif message.content == "!help":
        await message.channel.send(HelpMessage)
        return

    elif message.content == "!call":
        if message.author.voice is None:
            await message.channel.send("接続先がみつかりません。")
            return
        await message.author.voice.channel.connect()
        await message.channel.send("しゃべるよ!!")
        VOICE_FLAG = True

    elif message.content == "!calloff":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        await message.guild.voice_client.disconnect()
        await message.channel.send("私は必要とされていないんですね...")
        VOICE_FLAG = False
        return

    elif message.content[0:6] == "!speed":
        try:
            s = float(message.content[6:])
        except:
            s = 1.0
        TALK.Speed(s)
        return
    
    elif message.content[0:8] == "!allpass":
        try:
            a = float(message.content[8:])
        except:
            a = -1.0
        TALK.Allpass(a)
        return

    elif message.content[0] != "!" and VOICE_FLAG==True:
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        id = message.guild.id
        await TALK.Talk(message.content,id)
        return
    
    return


# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)