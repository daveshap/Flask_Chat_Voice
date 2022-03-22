from flask import Flask, Response,render_template
import pyaudio

app = Flask(__name__)


FORMAT = pyaudio.paInt16
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 1
bitsPerSample = 16
CHANNELS = 1
audio1 = pyaudio.PyAudio()


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


@app.route('/audio')
def audio():
    def sound():
        wav_header = genHeader(RATE, bitsPerSample, CHANNELS)
        stream = audio1.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,input_device_index=1,
                        frames_per_buffer=CHUNK)
        print("recording...")
        first_run = True
        while True:
           if first_run:
               data = wav_header + stream.read(CHUNK)
               first_run = False
           else:
               data = stream.read(CHUNK)
           yield(data)
    return Response(sound())

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True,port=5000)