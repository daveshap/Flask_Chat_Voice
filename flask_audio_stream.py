from flask import Flask, Response,render_template
import pyaudio
from scipy.io.wavfile import write
import numpy as np
from threading import Thread
from time import time


app = Flask(__name__)


FORMAT = pyaudio.paInt16
RATE = 44100
#CHUNK_SIZE = 1024
CHUNK_SIZE = RATE
RECORD_SECONDS = 1
bitsPerSample = 16
CHANNELS = 1
audio1 = pyaudio.PyAudio()
outdir = 'audio_cache/'


def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    header = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    header += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    header += bytes("WAVE",'ascii')                                              # (4byte) File type
    header += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    header += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    header += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    header += (channels).to_bytes(2,'little')                                    # (2byte)
    header += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    header += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    header += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    header += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    header += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    header += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return header


def save_chunk(chunk, timestamp):
    filename = '%s%s_input_microphone.wav' % (outdir, timestamp)
    numpydata = np.frombuffer(chunk, dtype=np.int16)
    #print(numpydata)
    write(filename, RATE, numpydata)


@app.route('/audio')
def audio():
    def sound():
        stream = audio1.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,input_device_index=1, frames_per_buffer=CHUNK_SIZE)
        print("recording...")
        first_run = True
        while True:
            chunk = stream.read(CHUNK_SIZE)
            if first_run:
                wav_header = genHeader(RATE, bitsPerSample, CHANNELS)
                data = wav_header + chunk
                first_run = False
            else:
                data = chunk
            save_thread = Thread(target=save_chunk, args=(chunk, time()))
            save_thread.start()
            yield(data)
    return Response(sound())


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True,port=5000)