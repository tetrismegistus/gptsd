import io
import asyncio
import uuid
import sys
from aiohttp import ClientSession
from random import shuffle, random

import requests
import discord, openai
from discord.ext import commands
from PIL import Image

from tarotHandler import TarotHandler
from prompts import prompts

import asyncio

class AsyncSafeList:
    def __init__(self):
        self._list = []
        self._lock = asyncio.Lock()
        self._index = 0

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        async with self._lock:
            if self._index < len(self._list):
                item = self._list[self._index]
                self._index += 1
                return item
            else:
                raise StopAsyncIteration

    async def append(self, item):
        async with self._lock:
            self._list.append(item)
            if len(self._list) > 6:
                self._list.pop(0)

    async def remove(self, item):
        async with self._lock:
            self._list.remove(item)

    async def get(self, index):
        async with self._lock:
            return self._list[index]

    async def __len__(self):
        async with self._lock:
            return len(self._list)


class BotBot(discord.Client):
    def __init__(self, intents, log_channel):
        self.model = "text-davinci-003"
        self.temp = .9
        self.freq_penalty = 0.0
        self.pres_penalty = 0.7
        self.log_channel = log_channel
        self.top_p = 1
        self.tarotHandler = TarotHandler()
        self.gpt_history = AsyncSafeList()
        super().__init__(intents=intents)


    async def on_ready(self):
        await self.send_log_message(f'We have logged in as {self.user}')

    async def on_message(self, message, *args):
        if message.author == self.user:
            return
        sender_name = message.author.mention
        if message.content.startswith('$'):
            await self.execute_command(message)
        return

    async def send_chat(self, message, prompt, text, command):
        formatted_message =  prompt.format(text)
        response = await self.send_OpenAI_completion_request(formatted_message)

        await self.send_message(message, response, command)

    async def send_log_message(self, text):
        channel = bot.get_channel(self.log_channel)
        await channel.send(text)

    async def send_message(self, message, text, command, files=None):
        if command == '$python':
            text = '```python\n' + text + '\n```'

        if command == '$color':
            c = text.strip(';').strip(' ')
            img = Image.new(mode="RGBA", size=(100, 100), color=c)
            fname = 'temp/' + str(uuid.uuid4()) + '.png'
            img.save(fname, 'PNG')
            #embed = discord.Embed(title=c, color=int(c, 0))
            await message.channel.send(c, file=discord.File(fname), reference=message)
        else:

            text = (text[:1997] + '..') if len(text) > 1999 else text
            try:
                await message.channel.send(text, reference=message, files=files)
            except discord.errors.HTTPException as e:
                await message.channel.send(f"***Recieved no text in response***")
                await self.send_log_message(e)

    async def execute_command(self, message):
        command_args = message.content.split()

        prompt = ''

        if command_args[0] == '$RATI' or command_args[0] == '$LEGO':
            if len(command_args) == 1:
                command_args.append(' ')
            prompt = message.content.split(command_args[0])[1]
            primer = '{}'.format(command_args[0][1:])
            prompt = f'{primer}. {prompt}'
            command_args[0] = '$img'
        else:
            prompt = message.content.split(command_args[0])[1]


        await self.send_log_message(f"received command: {command_args[0]}: {prompt}")

        if command_args[0] in prompts.app_commands:
            settings = prompts.prompt_dict[command_args[0]]
            old_temp = self.temp
            old_freq_penalty = self.freq_penalty
            old_pres_penalty = self.pres_penalty
            old_model = self.model
            old_top_p = self.top_p
            self.model = settings['model']
            self.temp = settings['t']
            self.freq_penalty = settings['fp']
            self.pres_penalty = settings['pp']
            self.top_p = settings['tp']
            await self.send_chat(message, settings['prompt'], prompt, command_args[0])
            self.model = old_model
            self.freq_penalty = old_freq_penalty
            self.pres_penalty = old_pres_penalty
            self.temp = old_temp
            self.top_p = old_top_p


        if command_args[0] == '$draw':
            try:
                num_cards = int(command_args[1])
            except:
                num_cards = 1

            try:
                deck = command_args[2]
            except:
                deck = 'jodocamoin'

            response_text, images = self.tarotHandler.draw(num_cards, deck)
            response_text = '\n'.join(response_text)
            files = [discord.File(card_image) for card_image in images]
            await self.send_message(message, response_text, command_args[0], files)

        if command_args[0] == '$comp':
            response = await self.send_OpenAI_completion_request(prompt)
            await self.send_message(message, response, command_args[0])

        if command_args[0] == '$img+':
            prompt = "highly detailed 4k intricate professional " + prompt
            command_args[0] = '$img'

        if command_args[0] == '$img':

            response = await self.send_OpenAI_image_request(prompt)
            if isinstance(response, str):
                await message.channel.send(response, reference=message)
            else:
                image_url = response['data'][0]['url']

                img = requests.get(image_url)

                if img.status_code == 200:
                    image_data = io.BytesIO(img.content)
                    image_file = discord.File(image_data, filename="temp.png")
                    await message.channel.send(file=image_file, reference=message)

        if command_args[0] == '$edit':
            baseimg = requests.get(message.attachments[0].url)
            alphaimg = requests.get(message.attachments[1].url)


            response = openai.Image.create_edit(
                image=io.BytesIO(baseimg.content),
                mask=io.BytesIO(alphaimg.content),
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            image_url = response['data'][0]['url']
            img = requests.get(image_url)

            if img.status_code == 200:
                image_data = io.BytesIO(img.content)
                image_file = discord.File(image_data, filename="temp.png")
                await message.channel.send(file=image_file)

        if command_args[0] == '$gpt':
            await self.gpt_history.append({"role": "user", "content": prompt})
            response = await self.send_ChatGPT_request(prompt)
            await self.gpt_history.append({"role": "assistant", "content": response})
            text = (response[:1997] + '..') if len(response) > 1999 else response
            try:
                await message.channel.send(text, reference=message)
            except discord.errors.HTTPException as e:
                await message.channel.send(f"***Recieved no text in response***")
                await self.send_log_message(e)

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

    async def send_OpenAI_completion_request(self, prompt):
        returnval = None
        try:
            response = openai.Completion.create(model=self.model,
                                            prompt=prompt,
                                            temperature=self.temp,
                                            max_tokens=256,
                                            top_p = self.top_p,
                                            frequency_penalty=self.freq_penalty,
                                            presence_penalty=self.pres_penalty,)
            returnval = response['choices'][0]['text']
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

