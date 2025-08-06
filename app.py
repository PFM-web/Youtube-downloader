from flask import Flask, request, render_template, send_file, redirect, url_for, jsonify
from pytube import YouTube
import os
from moviepy.editor import AudioFileClip
import uuid

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_streams", methods=["POST"])
def get_streams():
    url = request.form["url"]
    try:
        yt = YouTube(url)
        title = yt.title
        streams = {
            "720p": yt.streams.filter(progressive=True, res="720p").first().itag if yt.streams.filter(progressive=True, res="720p").first() else None,
            "1080p": yt.streams.filter(res="1080p", mime_type="video/mp4").first().itag if yt.streams.filter(res="1080p", mime_type="video/mp4").first() else None,
            "mp3": "audio"
        }
        return jsonify({"title": title, "streams": streams})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/download", methods=["POST"])
def download():
    url = request.form["url"]
    itag = request.form["itag"]
    yt = YouTube(url)

    try:
        if itag == "audio":
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_path = audio_stream.download(output_path=DOWNLOAD_DIR, filename=f"{uuid.uuid4()}.mp4")

            mp3_path = audio_path.replace(".mp4", ".mp3")
            AudioFileClip(audio_path).write_audiofile(mp3_path)
            os.remove(audio_path)
            return send_file(mp3_path, as_attachment=True)

        else:
            stream = yt.streams.get_by_itag(itag)
            file_path = stream.download(output_path=DOWNLOAD_DIR)
            return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
