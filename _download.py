# -*- coding: utf-8 -*-

import asyncio
import requests
import time
import urllib3

import m3u8
from functools import partial

URL = "https://www.soundvideostar.com/live/_definst_/rti3/chunklist_w1129242241.m3u8"
BASE = "https://www.soundvideostar.com/live/_definst_/rti3/"

audio_files = []

urllib3.disable_warnings()
start_time = time.time()


async def get_filenames():
    while True:
        print(round(time.time() - start_time, 1), "Fetching new playlist...")
        loop = asyncio.get_event_loop()
        # using partial to pass in function with two arguments to run_in_executor()
        # https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor
        playlist = await loop.run_in_executor(
            None, partial(m3u8.load, URL, verify_ssl=False),
        )
        for line in playlist.dumps().splitlines():
            if line.startswith("media") and line not in audio_files:
                audio_files.append(line)
                r = requests.get(BASE + line, verify=False, stream=False)
                with open("audio/" + line, "wb") as f:
                    f.write(r.content)
                    yield "audio/" + line
