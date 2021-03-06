# radio-transcription

Live audio transcription for learning Mandarin (Chinese).

This project transcribes the radio stream of Radio Taiwan International ([RTI](https://www.rti.org.tw/)) in real time, so you can read along and look up words that you don't know.

You need a Google Cloud API key from here: [Create an API key](https://cloud.google.com/speech-to-text/docs/before-you-begin)

The API has a free tier of 60 minutes per month, after which it costs $1.44 per hour of audio, or $0.96 if you have data logging enabled.

If you want a free service, you can use the branch `feature/vosk` along with [Vosk-Server](https://github.com/alphacep/vosk-server) for offline speech-to-text, but Google's quality is much much better. See the [README](https://github.com/yunusabd/radio-transcription/blob/features/vosk/README.md) in the `feature/vosk` branch for instructions on how to use.

## Getting started

1. Create an API key (see above)
2. `conda env create -f environment.yml`
3. `conda activate chinese`
4. `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google_keys.json"`
5. `python radio.py`
6. Open `client.html` in a browser and click play



https://user-images.githubusercontent.com/20162302/139258993-11309ad5-42cc-4f62-95aa-5e0b4b2dfafe.mp4

