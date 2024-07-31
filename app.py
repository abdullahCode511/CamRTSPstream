from flask import Flask, render_template, Response
import cv2
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)

# Dictionary to hold multiple video streams
streams = {
    "stream1": "rtsp://admin:huem92000@10.5.50.247:554/Streaming/Channels/101",
    "stream2": "rtsp://admin:huem92000@10.5.50.248:554/Streaming/Channels/101"  # Example additional stream
}

class VideoStream:
    def __init__(self, url):
        self.url = url
        self.capture = cv2.VideoCapture(url)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
        self.latest_frame = None
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.update_frames, daemon=True)
        self.thread.start()

    def update_frames(self):
        while True:
            success, frame = self.capture.read()
            if success:
                frame = cv2.resize(frame, (640, 480))
                with self.lock:
                    self.latest_frame = frame

    def get_frame(self):
        with self.lock:
            if self.latest_frame is not None:
                ret, buffer = cv2.imencode('.jpg', self.latest_frame)
                return buffer.tobytes()
            else:
                return None

video_streams = {key: VideoStream(url) for key, url in streams.items()}

def gen_frames(stream_id):
    stream = video_streams[stream_id]
    while True:
        frame = stream.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed/<stream_id>')
def video_feed(stream_id):
    if stream_id in video_streams:
        return Response(gen_frames(stream_id), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Stream not found", 404

@app.route('/embed/<stream_id>')
def embed(stream_id):
    if stream_id in video_streams:
        return render_template('embed.html', stream_id=stream_id)
    else:
        return "Stream not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
