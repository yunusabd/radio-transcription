# radio-transcription

How to use with [Vosk-Server](https://github.com/alphacep/vosk-server) for offline speech-to-text. The quality of the transcription is unfortunately not as good as Google's, partly because it's not optimized for Taiwanese vocabulary and pronunciations. The output text is also in simplified characters. But it doesn't cost money, so that's nice.

## Getting started

1. You'll need to have `ffmpeg` and `docker` installed.
2. `conda env create -f environment.yml`
3. `conda activate chinese`
4. `docker run -d -p 2700:2700 alphacep/kaldi-cn:latest`
5. `python radio.py`
6. Open `client.html` in a browser and click play



https://user-images.githubusercontent.com/20162302/139258993-11309ad5-42cc-4f62-95aa-5e0b4b2dfafe.mp4

