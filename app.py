from flask import Flask, render_template, Response
import cv2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

vid = cv2.VideoCapture("rtsp://admin:Mstech12@10.5.50.227:554/Streaming/Channels/101")

vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))

def gen_frames():
    while True:
        success, frame = vid.read()
        if not success:
            vid.release()
            vid.open("rtsp://admin:Mstech12@192.168.0.153:554/Streaming/Channels/101")
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

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/embed')
def embed():
    return render_template('embed.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=8080)
