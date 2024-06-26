from flask import Flask, request, render_template, jsonify, Response
import whisper
import os
import requests
from pytube import YouTube

app = Flask(__name__)
model = whisper.load_model("base")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        # Save uploaded file
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Transcribe audio file
        result = model.transcribe(file_path)
        transcription = result['text']
        print(result)

        return jsonify({'transcription': transcription})

@app.route('/transcribe_url', methods=['POST'])
def transcribe_url():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return 'No URL provided', 400

    # Determine the source of the URL and download the file
    try:
        if 'youtube.com' in url or 'youtu.be' in url:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            file_path = os.path.join('uploads', yt.title + '.mp4')
            stream.download(output_path='uploads', filename=yt.title + '.mp4')
        else:
            response = requests.get(url)
            if response.status_code == 200:
                file_path = os.path.join('uploads', 'temp_file')
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                return 'Error downloading file', 400

        # Transcribe audio file
        result = model.transcribe(file_path)
        transcription = result['text']
        #print(result)

        return jsonify({'transcription': transcription})

    except Exception as e:
        print(e)
        return 'Error processing URL', 500

@app.route('/download')
def download():
    transcription = request.args.get('transcription', '')
    if transcription:
        return Response(
            transcription,
            mimetype='text/plain',
            headers={'Content-Disposition': 'attachment;filename=transcription.txt'}
        )
    else:
        return "Error: Text content not found"

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, port=5001)
