from flask import Flask, request, render_template, send_file, jsonify
from pytube import YouTube
import os
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
            "1080p": yt.streams.filter(res="1080p", mime_type="video/mp4").first().itag if yt.streams.filter(res="1080p", mime_type="video/mp4").first() else None
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
        stream = yt.streams.get_by_itag(itag)
        filename = f"{uuid.uuid4()}.mp4"
        file_path = stream.download(output_path=DOWNLOAD_DIR, filename=filename)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
