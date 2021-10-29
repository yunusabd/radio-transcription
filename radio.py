#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import io
import os
import requests
import subprocess
import time
import urllib3

import m3u8
import websockets


URL = "https://www.soundvideostar.com/live/_definst_/rti3/chunklist_w1129242241.m3u8"
BASE = "https://www.soundvideostar.com/live/_definst_/rti3/"
PHRASES = ["台灣", "中央廣播電台"]

audio_files = []

urllib3.disable_warnings()
start_time = time.time()


async def get_filenames():
    while True:
        playlist = m3u8.load(URL, verify_ssl=False)
        for line in playlist.dumps().splitlines():
            if line.startswith("media") and line not in audio_files:
                audio_files.append(line)
                r = requests.get(BASE + line, verify=False, stream=False)
                with open("audio/" + line, "wb") as f:
                    f.write(r.content)
                    print("audio/" + line)
                    yield "audio/" + line
        print(round(time.time() - start_time, 1), "Finished fetching new filenames")


async def run_stt(websocket, path):
    async with websockets.connect("ws://localhost:2700") as ws:
        async for filename in get_filenames():
            subprocess.call(
                [
                    "ffmpeg",
                    "-y",
                    "-nostats",
                    "-loglevel",
                    "0",
                    "-i",
                    filename,
                    "-ac",
                    "1",
                    "-ar",
                    "8000",
                    "-filter:a",
                    "loudnorm",
                    "-acodec",
                    "pcm_s16le",
                    filename[:-4] + ".wav",
                ]
            )
            wf = open(filename[:-4] + ".wav", "rb")
            while True:
                data = wf.read(8000)
                if len(data) == 0:
                    break
                await ws.send(data)
                res = await ws.recv()
                await websocket.send(res)


async def main():
    if not os.path.exists("audio"):
        os.makedirs("audio")
    async with websockets.serve(run_stt, "localhost", 8765):
        await asyncio.Future()


asyncio.run(main())
