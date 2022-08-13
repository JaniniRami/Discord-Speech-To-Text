# needed until the fork is merged upstream #
import sys

sys.path.insert(0, "discord.py")
############################################

import os
import json
import discord
import asyncio
import speech_recognition as sr

from lib.audio import speach_to_text
from lib.buffer_sink import BufferSink
from threading import Thread

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer



discord.opus._load_default()
close_flag = False
question_query = []



model="microsoft/DialoGPT-large"
print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(model)
model = AutoModelForCausalLM.from_pretrained(model)
print('Loaded Model')

def read_token():
    if os.path.exists(".secrets"):
        with open(".secrets") as f:
            secrets = json.load(f)
        return secrets
    else:
        print("[!] Cannot read token from .secrets file.")
        sys.exit(0)


class Freyja(discord.Client):
    def __init__(self):
        super().__init__()
        self.target_channel = None
        self.post_thread = None
        self.buffer = BufferSink()

    async def on_ready(self):
        print("\nLogged in as")
        print(self.user.name)
        print(self.user.id)
        print("----------\n")


    async def on_message(self, message):
        global close_flag

        if message.author == self.user:
            return False

        if message.content.lower().startswith("/close"):
            await message.channel.send("Shuting down...")
            if self.voice_clients:
                for vc in self.voice_clients:
                    await vc.disconnect()

            close_flag = True
            self.post_thread.join()

            await self.close()
            quit()

        if message.content.lower().startswith("/leave"):
            if self.voice_clients:
                for vc in self.voice_clients:
                    await vc.disconnect()
                close_flag = True
                self.post_thread.join()
            else:
                await message.channel.send("You are not in a voice channel.")

        if message.content.lower().startswith("/join"):
            if message.author.voice is None:
                await message.channel.send("You are not in a voice channel.")
            else:
                if self.voice_clients:
                    self.target_channel = message.channel
                    await message.channel.send(
                        f"Joining voice channel: {message.author.voice.channel.name}."
                    )
                    await self.voice_clients[0].move_to(message.author.voice.channel)

                    if self.post_thread is None:
                        self.post_thread = Thread(
                            target=get_audio,
                            args=(self, self.buffer, self.target_channel),
                        )
                        self.post_thread.start()

                    self.voice_clients[0].listen(
                        discord.reader.UserFilter(self.buffer, message.author)
                    )
                else:
                    self.target_channel = message.channel
                    await message.channel.send(
                        f"Joining voice channel: {message.author.voice.channel.name}."
                    )
                    await message.author.voice.channel.connect()

                    if self.post_thread is None:
                        self.post_thread = Thread(
                            target=get_audio,
                            args=(self, self.buffer, self.target_channel),
                        )
                        self.post_thread.start()
                    self.voice_clients[0].listen(
                        discord.reader.UserFilter(self.buffer, message.author)
                    )


def get_audio(bot, buffer, target_channel):
    global close_flag
    global question_query
    while True:
        if len(buffer.bytearr_buf) > 960000:
            idx = buffer.bytes_ps * 5
            slice = buffer.bytearr_buf[:idx]

            if any(slice):
                idx_strip = slice.index(next(filter(lambda x: x != 0, slice)))

                if idx_strip:
                    buffer.freshen(idx_strip)
                    slice = buffer.bytearr_buf[:idx]
                    print("processing...")
                audio = sr.AudioData(
                    bytes(slice), buffer.sample_rate, buffer.sample_width
                )

                text = speach_to_text(audio)
                print(f"\n Question: {text}")
                asyncio.run_coroutine_threadsafe(
                        target_channel.send(f'You said: "{text}"'), bot.loop
                )
                if not text.startswith('ERROR'):
                    if len(question_query) > 5:
                        question_query = []
                    new_user_input_ids = tokenizer.encode(text + tokenizer.eos_token, return_tensors='pt')
                    bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if question_query else new_user_input_ids
                    chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
                    print("DialoGPT: {}".format(tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)))
                    if question_query and text == question_query[-1]:
                        question_query = []
                    else:
                        question_query.append(text)
            buffer.freshen(idx)

        if close_flag:
            try:
                buffer.freshen(idx)
            except:
                pass
            break

        

client = Freyja()
client.run(read_token()["token"])
