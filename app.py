from flask import Flask, Response, render_template
from flask_socketio import SocketIO
from pyzbar.pyzbar import decode
import cv2
import numpy as np

app = Flask(__name__)
socketio = SocketIO(app) #, cors_allowed_origins="*"

def obtain_camera_frame(camera):
    ok, frame = camera.read()
    if not ok:
        return False, None
    return True, frame

def to_bytes(image):
    _, buffer = cv2.imencode('.jpg', image)
    return buffer.tobytes()

def generador_frames():
    
    camera = cv2.VideoCapture(0)

    while True:
        ok, image = obtain_camera_frame(camera)
        if not ok: break

        detected_objects = decode(image)
        # Print results
        for barcode in detected_objects:
            print('Type:', barcode.type)
            print('Data:', barcode.data.decode('utf-8'))
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 5)
        
        bytes_image = to_bytes(image)

        # Regresar la image en modo de respuesta HTTP
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + bytes_image + b"\r\n"

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.route("/hello")
def hello_world():
    return "<p>Hello, World!!!!</p>"

@app.route("/test")
def index():
    return Response(generador_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/")
def streaming_camara():
    return render_template("camera.html")

@socketio.on('frame')
def handle_frame(data):
    print('Received frame:', len(data), 'bytes')

    nparr = np.frombuffer(data, np.uint8)  # Convert frame bytes to numpy array
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Decode the image
    # Process the image (e.g., apply some computer vision tasks)
    # For example, let's convert the image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Do something with the processed image (e.g., save it, display it, etc.)
    print(gray_img.shape)
    cv2.imwrite('received_frame.jpg', img)

@socketio.on('stream')
def handle_video_frame(data):
    # Process the received video data here
    print('Received video data:', len(data), 'bytes')

    nparr = np.frombuffer(data, np.uint8)
    print(nparr.shape)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is not None:
        print(img.shape)

    #gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #cv2.imshow("Processed Frame", gray_img)
    #cv2.waitKey(1)


    # decoded_data = base64.b64decode(data)
    
    # # Convert the image data to a numpy array
    # nparr = np.frombuffer(decoded_data, np.uint8)

    # frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # if frame is not None and frame.size > 0:
    #     # Process the image using OpenCV
    #     # For example, you can perform any image processing operations here
        
    #     # Display the processed image
    #     cv2.imshow('Processed Image', frame)
    #     cv2.waitKey(1)  # Necessary for the imshow to work properly
    # else:
    #     print("Invalid image data received")

if __name__ == '__main__':
    print('lol')
    #app.run(debug=True, port=5000, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
    socketio.run(app, debug=True, port=5000, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))