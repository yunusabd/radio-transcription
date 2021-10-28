#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import io
import os
import requests
import time
import urllib3

import m3u8
import websockets

from google.cloud import speech_v1p1beta1 as speech

URL = "https://www.soundvideostar.com/live/_definst_/rti3/chunklist_w1129242241.m3u8"
BASE = "https://www.soundvideostar.com/live/_definst_/rti3/"
PHRASES = ["台灣", "中央廣播電台"]

audio_files = []

urllib3.disable_warnings()
start_time = time.time()
client = speech.SpeechClient()


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
        await asyncio.sleep(5)
        print(round(time.time() - start_time, 1), "Finished fetching new filenames")


async def run_stt(websocket, path):
    async for filename in get_filenames():
        with io.open(filename, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=16000,
            language_code="zh-TW",
            enable_automatic_punctuation=True,
            speech_contexts=[speech.types.SpeechContext(phrases=PHRASES,)],
        )
        response = client.recognize(config=config, audio=audio)
        print("Raw response: {}".format(response))
        for result in response.results:
            # The first alternative is the most likely one for this portion.
            print(u"Transcript: {}".format(result.alternatives[0].transcript))
            await websocket.send(result.alternatives[0].transcript)


async def main():
    if not os.path.exists("audio"):
        os.makedirs("audio")
    async with websockets.serve(run_stt, "localhost", 8765):
        await asyncio.Future()


asyncio.run(main())
