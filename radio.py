#!/usr/bin/env python3

import asyncio
import websockets

import requests
import m3u8
import subprocess


async def run_stt(websocket, path):

    async with websockets.connect("ws://localhost:2700") as ws:
        url = "https://www.soundvideostar.com/live/_definst_/rti3/chunklist_w1129242241.m3u8"
        base = "https://www.soundvideostar.com/live/_definst_/rti3/"
        playlist = m3u8.load(url, verify_ssl=False)
        for line in playlist.dumps().splitlines():
            if line.startswith("media"):
                print(base + line)
                r = requests.get(base + line, verify=False, stream=False)
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

        await websocket.send('{"eof" : 1}')


async def main():
    async with websockets.serve(run_stt, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
