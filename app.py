from flask import Flask, render_template, Response
import cv2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Dictionary to hold multiple video streams
streams = {
    "stream1": "rtsp://admin:huem92000@10.5.50.247:554/Streaming/Channels/101",
    "stream2": "rtsp://admin:huem92000@10.5.50.191:554/Streaming/Channels/101"  # Example additional stream
}

def gen_frames(stream_url):
    vid = cv2.VideoCapture(stream_url)
    vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
    while True:
        success, frame = vid.read()
        if not success:
            vid.release()
            vid.open(stream_url)
            continue
        else:
            frame = cv2.resize(frame, (640, 480))
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed/<stream_id>')
def video_feed(stream_id):
    if stream_id in streams:
        return Response(gen_frames(streams[stream_id]), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Stream not found", 404

@app.route('/embed/<stream_id>')
def embed(stream_id):
    if stream_id in streams:
        return render_template('embed.html', stream_id=stream_id)
    else:
        return "Stream not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
