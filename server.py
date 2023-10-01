from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return "Server is running..."

@socketio.on('video_frame')
def handle_frame(data):
    image = data['image']
    # You can process or display the image here

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
