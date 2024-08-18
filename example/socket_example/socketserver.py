import socket
import json
import cv2
import numpy as np
import math
from queue import Queue
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8888))
server.listen(5)
server.setblocking(False)
msgQueue=Queue()

stopServer=False

def process(conn,addr):
    global stopServer
    res=""
    while not stopServer:
        try:
            msg = conn.recv(1024).decode('ascii')
        except:
            continue
        if '\0' in msg:
            res += msg[:msg.index('\0')]
            if res.replace(" ", "") == 'quit':
                break
            pack = json.loads(res)
            # print(f"recive from {addr[0]}:{addr[1]}, timestamp {pack['time']}")
            msgQueue.put(pack)
            res = ""
        else:
            res += msg
    conn.close()
    print(f"dicsonnect from {addr[0]}:{addr[1]}")

def serverListen(s):
    global stopServer
    while not stopServer:
        try:
            conn, addr = s.accept()
        except:
            continue
        print(f"connect to {addr[0]}:{addr[1]}")
        handler=threading.Thread(target=process,args=[conn,addr])
        handler.start()

image = np.zeros((90, 160, 3), np.uint8)
serverThread=threading.Thread(target=serverListen,args=[server])
serverThread.start()

while True:
    if not msgQueue.empty():
        pack=msgQueue.get()
        print(pack['time'])

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

    if cv2.waitKey(1) & 0xFF == ord('w'):
        stopServer=True
        break
cv2.destroyAllWindows()
