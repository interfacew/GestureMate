import socket
import json
import cv2
import numpy as np
import math

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8888))
server.listen(1)
print("listening")
conn, address = server.accept()
server.setblocking(False)

last = 0
res = ""
image = np.zeros((90, 160, 3), np.uint8)
while True:
    try:
        msg = conn.recv(1024).decode('ascii')
    except:
        pass
    if '\0' in msg:
        res += msg[:msg.index('\0')]
        if res.replace(" ", "") == 'quit':
            break
        pack = json.loads(res)
        print(pack['time'])
        res = ""

        image = np.zeros((90, 160, 3), np.uint8)
        if pack['pose']['face'] != None:
            for a in pack['pose']['face']:
                cv2.circle(image,
                           (math.floor(a[0] * 160), math.floor(a[1] * 90)), 1,
                           (255, 0, 0), 4)
        if pack['pose']['leftHand'] != None:
            for a in pack['pose']['leftHand']:
                cv2.circle(image,
                           (math.floor(a[0] * 160), math.floor(a[1] * 90)), 1,
                           (0, 255, 0), 4)
        if pack['pose']['rightHand'] != None:
            for a in pack['pose']['rightHand']:
                cv2.circle(image,
                           (math.floor(a[0] * 160), math.floor(a[1] * 90)), 1,
                           (0, 0, 255), 4)
        cv2.imshow("recv", image)

    else:
        res += msg

    if cv2.waitKey(1) & 0xFF == ord('w'):
        break
cv2.destroyAllWindows()
