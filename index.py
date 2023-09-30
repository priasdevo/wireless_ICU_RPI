import socketio
import time

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to server!')

@sio.on('message')
def on_message(data):
    print('Message from server:', data)

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from server!')

# Connect to the server
sio.connect('http://fe80::d3c5:dfca:ec8b:168%10:5000')  # Replace with your website URL

try:
    while True:
        sio.emit('message', 'Hello from client every 10 seconds!')
        time.sleep(10)
except KeyboardInterrupt:
    pass
finally:
    sio.disconnect()
