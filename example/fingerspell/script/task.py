import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import torch
import torch.nn as nn
import torch.nn.functional as F
from utils import train_dir,normalize
import json
import cv2 as cv
import socket
from queue import Queue
import numpy as np
import threading
import math

class SignClassifier(nn.Module):

    def __init__(self):
        super(SignClassifier, self).__init__()
        self.ff1 = nn.Linear(21 * 3, 1024)
        self.ff2 = nn.Linear(1024, 512)
        self.ff3 = nn.Linear(512, 28)
        self.relu = nn.ReLU()
        self.flatten = nn.Flatten()
        self.dropout1 = nn.Dropout(0.2)
        self.dropout2 = nn.Dropout(0.2)

    def forward(self, x):
        x = self.flatten(x)
        x = self.dropout1(self.relu(self.ff1(x)))
        x = self.dropout2(self.relu(self.ff2(x)))
        return self.ff3(x)

model = torch.load('PointDetect_3d.pth')
token_list = []
with open(os.path.join(train_dir, "../tokenlist.json"), "r") as f:
    token_list = json.loads(f.read())
print(token_list)
device = 'cuda'

start_time = 0
last_token = "@"
sentence = "@"
ACTIVATE_RATE = 60 / 100

def handlePack(pack,image):
    global last_token, start_time, sentence, ACTIVATE_RATE

    a=[[0,0,0]]*21 if pack['pose']['leftHand']==None else pack['pose']['leftHand']
    a=normalize(a)
    data = torch.Tensor([a]).to(device)
    res = F.softmax(model(data))
    a = res.argmax(1)


    image = np.zeros((800, 1200, 3), np.uint8)

    for i in range(len(token_list)):
        if pack['pose']['leftHand'] != None:
            cv.rectangle(image, (0, 25 * i + 25),
                         (math.ceil(200 * res[0][i]), 25 * i), (0, 255, 0), -1)
            cv.putText(image, f"{res[0][i]*100:>.3f}%", (210, 25 * i + 25),
                       cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv.putText(image, f"Token {token_list[i]}", (0, 25 * i + 25),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if pack['pose']['leftHand'] == None:
        cv.putText(image, f"{sentence[1:]}", (400, 200),
                   cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        start_time = 0
        last_token = "@"
        return image

    if res[0][a[0]] >= ACTIVATE_RATE:
        now = pack['time']*1000
        print(now,start_time)
        if start_time == 0 or not last_token == a[0]:
            start_time = now
            last_token = a[0]
        elif now - start_time > 1000:
            if token_list[a[0]] == 'space':
                sentence += '_'
            else:
                sentence += token_list[a[0]]
            start_time = 1e18
            cv.putText(image, f"Recognize: {token_list[a[0]]}", (400, 100),
                       cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
    else:
        start_time == 0
    cv.putText(image, f"{sentence[1:]}", (400, 200), cv.FONT_HERSHEY_SIMPLEX,
               2, (0, 0, 255), 2)
    return image



server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8888))
server.listen(5)
server.setblocking(False)
msgQueue = Queue()

stopServer = False


def process(conn, addr):
    global stopServer
    res = ""
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
        handler = threading.Thread(target=process, args=[conn, addr])
        handler.start()


image = np.zeros((800, 1200, 3), np.uint8)
serverThread = threading.Thread(target=serverListen, args=[server])
serverThread.start()

while True:
    if not msgQueue.empty():
        pack = msgQueue.get()
        image=handlePack(pack,image)
    cv.imshow("recv", image)

    if cv.waitKey(1) & 0xFF == ord('w'):
        stopServer = True
        break
cv.destroyAllWindows()

