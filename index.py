import socketio
import time
import cv2
import base64
import requests

sio = socketio.Client()
server_address = 'http://169.254.248.218:5000'
login_endpoint = '/authDevice/authenticate'
socket_authen = False

login_data = {
    'macAddress': '23:a7:14:9c:b0:ed',
    'password': 'password'
}

response = requests.post(server_address + login_endpoint, json=login_data)
response_data = response.json()

if response.status_code == 200:
    print("Successfully logged in!")
else:
    print("Login failed:", response)
    exit()

cap = cv2.VideoCapture(0)

@sio.on('connect')
def on_connect():
    print('Connected to server!')

@sio.on('message')
def on_message(data):
    print('Message from server:', data)

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from server!')

@sio.on('authen_success')
def on_authen_success():
    global socket_authen  # Declare the variable as global
    print('Authen confirm from server!')
    socket_authen = True

# Connect to the server
sio.connect('http://169.254.248.218:5000')  # Replace with your website URL

while not socket_authen:
    sio.emit('authenticate',response_data)
    time.sleep(2)

sio.emit('identify_streamer')
print("Confirm socket login")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        _, buffer = cv2.imencode('.jpg', frame)
        encoded_image = base64.b64encode(buffer).decode('utf-8')

        sio.emit('stream', encoded_image)
except KeyboardInterrupt:
    pass
finally:
    sio.disconnect()
