import io
import sys
from random import shuffle, random

import requests
import discord, openai
from discord.ext import commands

from modules.tarotHandler import TarotHandler
from modules.helpers import AsyncSafeList


class BotBot(commands.Bot):
    def __init__(self, intents, log_channel):
        self.log_channel = log_channel
        self.tarotHandler = TarotHandler()
        super().__init__(command_prefix='/', intents=intents)
        self.gpt_history = AsyncSafeList()
        self.add_commands()

    async def on_ready(self):
        await self.send_log_message(f'We have logged in as {self.user}')

    async def send_log_message(self, text):
        channel = bot.get_channel(self.log_channel)
        await channel.send(text)

    async def send_img_response(self, response, message):
        if isinstance(response, str):
            await message.channel.send(response, reference=message)
        else:
            image_url = response['data'][0]['url']
            img = requests.get(image_url)
            if img.status_code == 200:
                image_data = io.BytesIO(img.content)
                image_file = discord.File(image_data, filename="temp.png")
                await message.channel.send(file=image_file, reference=message)


    def add_commands(self):
        @self.command(name='gpt', pass_context=True, help='Sends text after command to chatGPT')
        async def gpt(ctx):
            prompt = ctx.message.content[len(ctx.prefix)+len(ctx.invoked_with):].strip()
            await ctx.bot.gpt_history.append({"role": "user", "content": prompt})
            response = await ctx.bot.send_ChatGPT_request(prompt)
            await ctx.bot.gpt_history.append({"role": "assistant", "content": response})
            text = (response[:1997] + '..') if len(response) > 1999 else response
            try:
                await ctx.channel.send(text, reference=ctx.message)
            except discord.errors.HTTPException as e:
                await ctx.channel.send(f"***Recieved no text in response***")
                await ctx.bot.send_log_message(e)

        @self.command(name='draw', pass_context=True, help="Draws tarot cards.")
        async def draw(ctx,
                       num_cards: int = commands.parameter(default=1,
                                                           description="the number of cards to draw"),
                       deck: str = commands.parameter(default='jodocamoin',
                                                      description="type of deck: jodocamoin, crowleythoth, riderwaitesmith")):
            if num_cards is None:
                num_cards = 1
            else:
                num_cards = int(num_cards)

            response_text, images = ctx.bot.tarotHandler.draw(num_cards, deck)
            response_text = '\n'.join(response_text)
            files = [discord.File(card_image) for card_image in images]
            await ctx.channel.send(response_text, reference=ctx.message, files=files)

        @self.command(name='img', pass_context=True, help="Sends text after command to DALL-E")
        async def img(ctx):
            prompt = ctx.message.content[len(ctx.prefix)+len(ctx.invoked_with):].strip()
            response = await ctx.bot.send_OpenAI_image_request(prompt)
            await ctx.bot.send_img_response(response, ctx.message)

        @self.command(name='imgp', pass_context=True, help="like /img, but adds 'highly detailed 4k intricate professional' before prompt")
        async def imgp(ctx):
            prompt = "highly detailed 4k intricate professional " + ctx.message.content[len(ctx.prefix)+len(ctx.invoked_with):].strip()
            response = await ctx.bot.send_OpenAI_image_request(prompt)
            await ctx.bot.send_img_response(response, ctx.message)

        @self.command(name='RATI', pass_context=True, help="like /img, but adds 'RATI the rat God. ' before your prompt")
        async def RATI(ctx):
            prompt = "RATI the rat God. " + ctx.message.content[len(ctx.prefix)+len(ctx.invoked_with):].strip()
            response = await ctx.bot.send_OpenAI_image_request(prompt)
            await ctx.bot.send_img_response(response, ctx.message)

        @self.command(name='LEGO', pass_context=True, help="like /img, but adds 'LEGO. ' before your prompt")
        async def LEGO(ctx):
            prompt = "LEGO. " + ctx.message.content[len(ctx.prefix)+len(ctx.invoked_with):].strip()
            response = await ctx.bot.send_OpenAI_image_request(prompt)
            await ctx.bot.send_img_response(response, ctx.message)

    async def send_ChatGPT_request(self, prompt):
        model = "gpt-3.5-turbo"
        mess = [{"role": "system", "content": "You are a helpful assistant. You respond in great depth."}]
        async for m in self.gpt_history:
            mess.append(m)
        try:
            response = openai.ChatCompletion.create(model=model,
                                                    messages=mess,
                                                    temperature=0,
                                                    )
            returnval = response['choices'][0]['message']['content']
        except (openai.error.InvalidRequestError, openai.error.APIError) as e:
            returnval = f'***{e}***'
            await self.send_log_message(e)
        return returnval

    async def send_OpenAI_image_request(self, prompt):
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
        except (openai.error.InvalidRequestError, openai.error.APIError) as e:
            await self.send_log_message(e)
            response = f'***{e}***'
        return response


if __name__ == '__main__':
    openai.api_key = sys.argv[1]
    intents = discord.Intents.default()
    intents.message_content = True
    bot = BotBot(intents=intents, log_channel=int(sys.argv[2]))
    bot.run(sys.argv[3])

