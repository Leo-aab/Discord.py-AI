import discord, os, asyncio,re,unicodedata
from discord.ext import commands
from dotenv import load_dotenv
from google import genai




"""token do modelo de linguagem"""
load_dotenv()
client = genai.Client(api_key= os.getenv("GO_API_KEY"))



intents = discord.Intents.all()
intents.members = True
intents.message_content = True
  
bot = commands.Bot(".", intents=intents)

@bot.event
async def on_ready():
    print('bot inicializado com sucesso')
    await bot.tree.sync()
    

@bot.command()
async def ping(ctx):
        latency_ms = round(bot.latency * 1000)
        await ctx.send(f"Pong!! Minha latência é de {latency_ms} ms... Mais alguma coisa?")

#comando de fala - talk
    
def contains_mention(content: str) -> bool:
   normalizado = unicodedata.normalize("NFKC", content)
   limpo = "".join(c for c in normalizado if not unicodedata.category(c).startswith("C"))
   if re.search(r"@[\.\s\u200b]*everyone|@[\.\s\u200b]*here", limpo, re.IGNORECASE):
    return True
   return False
@bot.command(name='talk')
async def ask_gemini(ctx, *, question: str):
    
    async with ctx.typing():
        await asyncio.sleep(10)
        """Definindo personalidade"""
        caminho = os.path.join(os.path.dirname(__file__),"personalidade.txt")
        with open(caminho, "r", encoding="utf-8") as f:
            personalidade = f.read() 
        
        #Bloqueio de entrada
        if contains_mention(question):
            await ctx.send("Não posso mencionar `@everyone` ou `@here`, desculpinha :(...")
            return
        else:
            """Perguntar para o bot"""
            try: 
                
                if not question.strip():
                    await ctx.send("Parece que você não fez uma pergunta...")
                    return
                response = client.models.generate_content(model="gemini-2.5-flash",contents=f'{personalidade}\n\n{question}')
                resposta_txt = response.text
                #await ctx.send(f"{response.text}")
                #divisão de mensagens
                
                
                #Bloqueio de saída 
                if contains_mention(resposta_txt):
                    await ctx.reply("🚫 A resposta continha menções proibidas, então foi bloqueada.", allowed_mentions=discord.AllowedMentions.none())
                    return
                 # Envio seguro

                    """Divide a resposta em chunks de no máximo 2000 caracteres cada
                    Isso evita o limite de caracteres do Discord por mensagem"""
                for chunk in [resposta_txt[i:i+2000] for i in range(0, len(resposta_txt), 2000)]:
                    await ctx.reply(chunk, allowed_mentions=discord.AllowedMentions.none())
                    await asyncio.sleep(1)
            except Exception as e:
                await ctx.send(f"Travei um pouco aqui, mande de novo a pergunta!!: {e}",allowed_mentions=discord.AllowedMentions.none())

#comando de sniper
bot.sniped_messages = {}
@bot.event
async def on_message_delete(message):
    if not message.author.bot: # Don't snipe bot messages
        bot.sniped_messages[message.channel.id] = {
            "content": message.content,
            "author": message.author,
            "channel": message.channel,
            "timestamp": message.created_at
        }
        
@bot.command()
async def snipe(ctx):
    if ctx.channel.id in bot.sniped_messages:
        sniped_info = bot.sniped_messages[ctx.channel.id]
        embed = discord.Embed(
            description=sniped_info["content"],
            color=discord.Color.blue(),
            timestamp=sniped_info["timestamp"]
        )
        embed.set_author(name=str(sniped_info["author"]), icon_url=sniped_info["author"].avatar.url)
        embed.set_footer(text=f"Esnaipada em #{sniped_info['channel'].name}")
        await ctx.send(embed=embed)
        del bot.sniped_messages[ctx.channel.id] # Optionally clear after sniping
    else:
        await ctx.send("Não tem nada pra esnaipar.... </3")





if __name__ == '__main__':
    load_dotenv()
    discord_key = os.getenv("DISCORD_TOKEN")
    bot.run(discord_key)

