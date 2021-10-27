#!/usr/bin/env python3

import asyncio
import websockets

import requests
import m3u8
import subprocess

import time
import urllib3

urllib3.disable_warnings()

start_time = time.time()

URL = "https://www.soundvideostar.com/live/_definst_/rti3/chunklist_w1129242241.m3u8"
BASE = "https://www.soundvideostar.com/live/_definst_/rti3/"

waiting = []
started = []


async def stuff():
    playlist = m3u8.load(URL, verify_ssl=False)
    for line in playlist.dumps().splitlines():
        if line.startswith("media") and line not in waiting and line not in started:
            waiting.append(line)
    print(round(time.time() - start_time, 1), "Finished getting new filenames")


async def do_stuff_periodically(interval, periodic_function):
    while True:
        print(round(time.time() - start_time, 1), "Getting filenames")
        await asyncio.gather(
            asyncio.sleep(interval),
            periodic_function(),
        )


async def run_stt(websocket, path):

    async with websockets.connect("ws://localhost:2700") as ws:
        while True:
            if len(waiting) == 0:
                await asyncio.sleep(3)
            for line in waiting:
                started.append(line)
                print(BASE + line)
                r = requests.get(BASE + line, verify=False, stream=False)
                with open("audio/" + line, "wb") as f:
                    f.write(r.content)
                    subprocess.call(
                        [
                            "ffmpeg",
                            "-y",
                            "-nostats",
                            "-loglevel",
                            "0",
                            "-i",
                            "audio/" + line,
                            "-ac",
                            "1",
                            "-ar",
                            "8000",
                            "-filter:a",
                            "loudnorm",
                            "-acodec",
                            "pcm_s16le",
                            "audio/" + line[:-4] + ".wav",
                        ]
                    )
                    wf = open("audio/" + line[:-4] + ".wav", "rb")
                    while True:
                        data = wf.read(8000)
                        if len(data) == 0:
                            break
                        await ws.send(data)
                        res = await ws.recv()
                        await websocket.send(res)
                    print(r.status_code)
                    waiting.pop(waiting.index(line))

        await websocket.send('{"eof" : 1}')


async def main():
    async with websockets.serve(run_stt, "localhost", 8765):
        task = asyncio.create_task(do_stuff_periodically(10, stuff))
        await asyncio.Future()  # run forever


asyncio.run(main())
