import cv2
from pyzbar.pyzbar import decode

camara = cv2.VideoCapture(0)

# View camara
while True:
    ok, frame = camara.read()
    if not ok:
        break
    

    detected_objects = decode(frame)
    # Print results
    for barcode in detected_objects:
        print('Type:', barcode.type)
        print('Data:', barcode.data.decode('utf-8'))
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 5)

    cv2.imshow("Camara", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break