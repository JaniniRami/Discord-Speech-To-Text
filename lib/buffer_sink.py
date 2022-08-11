# needed until the fork is merged upstream
import sys

sys.path.insert(0, "discord.py")
############################################


import discord


class BufferSink(discord.reader.AudioSink):
    def __init__(self):
        self.bytearr_buf = bytearray()
        self.sample_width = 4
        self.sample_rate = 48000
        self.bytes_ps = self.sample_width * self.sample_rate

    def write(self, data):
        self.bytearr_buf += data.data

    def freshen(self, idx):
        self.bytearr_buf = self.bytearr_buf[idx:]
