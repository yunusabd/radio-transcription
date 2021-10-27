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


from google.cloud import speech_v1p1beta1 as speech
import io

client = speech.SpeechClient()


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
    while True:
        if len(waiting) == 0:
            await asyncio.sleep(3)
        for line in waiting:
            started.append(line)
            print(BASE + line)
            r = requests.get(BASE + line, verify=False, stream=False)

            audio = speech.RecognitionAudio(content=r.content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                sample_rate_hertz=16000,
                language_code="zh-TW",
            )

            response = client.recognize(config=config, audio=audio)

            # Each result is for a consecutive portion of the audio. Iterate through
            # them to get the transcripts for the entire audio file.
            for result in response.results:
                # The first alternative is the most likely one for this portion.
                print(u"Transcript: {}".format(result.alternatives[0].transcript))
                await websocket.send(result.alternatives[0].transcript)

            print(r.status_code)
            waiting.pop(waiting.index(line))


async def main():
    async with websockets.serve(run_stt, "localhost", 8765):
        task = asyncio.create_task(do_stuff_periodically(10, stuff))
        await asyncio.Future()  # run forever


asyncio.run(main())
