import socketio
import time
import cv2
import base64
import requests
from gpiozero import MotionSensor

# pir = MotionSensor(5)
motion_detected = False
pir = False


def compress_image(frame, jpeg_quality=50):
    # Resize image if needed (for example, reducing resolution by half)
    # frame = cv2.resize(frame, (int(frame.shape[1]*0.5), int(frame.shape[0]*0.5)))
    
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
    _, buffer = cv2.imencode('.jpg', frame, encode_param)
    return buffer

def compress_image_size(frame, scale_factor=0.5):
    # Resize the image by the scale factor (e.g., 0.5 will halve the resolution)
    new_width = int(frame.shape[1] * scale_factor)
    new_height = int(frame.shape[0] * scale_factor)
    resized_frame = cv2.resize(frame, (new_width, new_height))
    
    return resized_frame


sio = socketio.Client()
server_address = 'http://localhost:5000'
login_endpoint = '/authDevice/authenticate'
socket_authen = False
receive_setting = False
isHome = True

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

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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

@sio.on('identify_success')
def on_authen_success(data):
    global receive_setting  # Declare the variable as global
    global isHome
    print('Identify confirm from server!',data)
    
    isHome = data
    receive_setting = True

# Connect to the server 169.254.248.218
sio.connect('http://localhost:5000')  # Replace with your website URL

while not socket_authen:
    sio.emit('authenticate',response_data)
    time.sleep(2)

while not receive_setting:
    sio.emit('identify_streamer')
    time.sleep(2)

print("Confirm socket login",isHome)

x = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        _, buffer = cv2.imencode('.jpg', frame)
        # compressed_frame = compress_image_size(frame)
        # buffer = compress_image(compressed_frame)
        encoded_image = base64.b64encode(buffer).decode('utf-8')

        sio.emit('stream', encoded_image)

        x = x+1
        if(x==300):
            sio.emit('movement_detected')

        # if pir.motion_detected and not isHome and not motion_detected:
        #     motion_detected = True
        #     print("You moved")
        #     sio.emit('movement_detected', encoded_image)


        #Reset the motion_detected flag if no motion is detected
        # elif not pir.motion_detected:
        #     print("You moved not")
        #     motion_detected = False

except KeyboardInterrupt:
    pass
finally:
    sio.disconnect()
