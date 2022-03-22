# write a Python Flask app that can use the microphone with PyAudio to record audio and then use the Google Cloud Speech API to transcribe the audio.
# https://stackoverflow.com/questions/51079338/audio-livestreaming-with-python-flask

import flask
from flask import Flask, request, render_template, send_from_directory
from flask_cors import CORS
import os
import subprocess
import time
import json
import pandas as pd
from io import StringIO
import sys

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Get the audio file from the request.
    data = request.get_json()

    audio = data['audio']
    audio = audio.encode('ascii')
    audio = audio.replace('data:audio/wav;base64,', '')

    # Write the audio to a file.
    f = open('audio.wav', 'wb')
    f.write(audio.decode('base64'))
    f.close()

    # Use the Google Cloud Speech API to transcribe the audio.
    command = 'curl -s -X POST -H "Content-Type: application/json" --data-binary @request.json "https://speech.googleapis.com/v1/speech:recognize?key=AIzaSyD9_7V0dZC-S07VuYMw0QtVc4t4h4yEu8k"'
    os.system(command)

    # Read the JSON response.
    f = open('request.json', 'r')
    request = f.read()
    f.close()

    # Load the JSON into a Python object.
    request = json.loads(request)

    # Get the first result.
    result = request['results'][0]

    # Get the first alternative.
    alternative = result['alternatives'][0]

    # Return the transcription of the audio.
    return alternative['transcript']

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)