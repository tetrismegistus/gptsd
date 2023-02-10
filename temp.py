import requests
import io
import asyncio
from random import shuffle

from PIL import Image
import discord, openai
from tarotdeck import TarotDeck


MAX_CARDS = 3
DECKS = ('jodocamoin', 'riderwaitesmith', 'crowleythoth')
DECK = 'jodocamoin'

class BotBot(discord.Client):
    def __init__(self, key, ):
        openai.api_key = key
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intent=intents)
        client.run('MTA1MDQ2ODQ3NzE0OTkxNzIwNA.GqSdvD.b7fnLpg2VkuTvDACjnutbipxFJp3NCX-XErxzY')

    async def on_ready():
        print(f'We have logged in as {client.user}')

    async def on_message(message, *args):
        if message.author == client.user:
            return

        command_args = message.content.split()

        if command_args[0] == '$setdeck':
            try:
                if command_args[1] in DECKS:
                    global DECK
                    await message.channel.send("Deck set to {}".format(command_args[1]))
                    DECK = command_args[1]
                else:
                    await message.channel.send("Deck type must be one of {}".format(DECKS))
            except (IndexError):
                pass

        if command_args[0] == '$draw':
            deck = TarotDeck(DECK)
            shuffle(deck)
            try:
                num_cards = int(command_args[1])
            except (ValueError, IndexError):
                num_cards = 1  # Default to 1 card if the argument is not a valid integer

            if num_cards > MAX_CARDS:
                await message.channel.send("I will draw a max of {} cards.".format(MAX_CARDS))
            else:
                for c in range(num_cards):
                    card = deck.pop()
                    if 'majors' not in card.image:
                        caption = card.rank + ' of ' + card.kind
                    else:
                        caption = card.rank + ': ' + card.kind

                    await message.channel.send(caption)
                    await message.channel.send(file=discord.File(card.image))

        if command_args[0] == '$gptcomp':
            prompt = message.content.split('$gptcomp')[1]
            response = send_OpenAI_completion_request(prompt)
            await message.channel.send(response)

        if command_args[0] == '$gptimg':
            prompt = message.content.split('$gptimg')[1]

            response = send_OpenAI_image_request(prompt)
            image_url = response['data'][0]['url']

            img = requests.get(image_url)

            if img.status_code == 200:
                image_data = io.BytesIO(img.content)
                image_file = discord.File(image_data, filename="temp.png")
                await message.channel.send(file=image_file)

        if message.content.startswith('$gptedit'):
            prompt = message.content.split('$gptedit')[1]
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


    def send_OpenAI_completion_request(prompt, temp=0.93):
        response = openai.Completion.create(model="text-davinci-002",
                                            prompt=prompt,
                                            temperature=temp,
                                            max_tokens=640,
                                            frequency_penalty=0.93,
                                            presence_penalty=0.93,)
        return response['choices'][0]['text']



    def send_OpenAI_image_request(prompt):
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        return response


if __name__ == '__main__':
    bot = BotBot()


