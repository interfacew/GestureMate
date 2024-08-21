import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import cv2 as cv
from utils import extract_landmarks, draw_styled_landmarks, normalize, train_dir, train_detect
import mediapipe.python.solutions as sol
import torch
import torch.nn as nn
import torch.nn.functional as F
import json


def start_listen(detect):
    camera = cv.VideoCapture(0, cv.CAP_DSHOW)
    camera.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    camera.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    camera.set(cv.CAP_PROP_FPS, 60)
    with sol.holistic.Holistic(min_detection_confidence=0.5,
                               min_tracking_confidence=0.5,
                               model_complexity=2) as holistic:
        while camera.isOpened():
            ret, frame = camera.read()
            if ret:
                frame = frame[:, ::-1, :]

                image = cv.cvtColor(
                    frame, cv.COLOR_BGR2RGB)  # COLOR CONVERSION BGR 2 RGB
                image.flags.writeable = False  # Image is no longer writeable
                results = holistic.process(image)  # Make prediction
                image.flags.writeable = True  # Image is now writeable
                image = cv.cvtColor(
                    image, cv.COLOR_RGB2BGR)  # COLOR COVERSION RGB 2 BGR

                draw_styled_landmarks(image, results)
                image = detect(image, extract_landmarks(results))

                cv.imshow('OpenCV Feed', image)
            if cv.waitKey(20) & 0xFF == ord('q'):
                break
        camera.release()
        cv.destroyAllWindows()

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
import math
from datetime import datetime

start_time = 0
last_token = "@"
sentence = "@"
ACTIVATE_RATE = 60 / 100


def detection(image, x):
    global last_token, start_time, sentence, ACTIVATE_RATE
    a = normalize(x[33:54])
    b = normalize(x[54:75])
    data = torch.Tensor([a, b]).to(device)
    res = F.softmax(model(data))
    a = res.argmax(1)

    for i in range(len(token_list)):
        if x[54][0] != 0:
            cv.rectangle(image, (0, 25 * i + 25),
                         (math.ceil(200 * res[1][i]), 25 * i), (0, 255, 0), -1)
            cv.putText(image, f"{res[1][i]*100:>.3f}%", (210, 25 * i + 25),
                       cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv.putText(image, f"Token {token_list[i]}", (0, 25 * i + 25),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    if x[54][0] == 0:
        cv.putText(image, f"{sentence[1:]}", (400, 200),
                   cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        start_time = 0
        last_token = "@"
        return image
    if res[1][a[1]] >= ACTIVATE_RATE:
        now = datetime.now().timestamp() * 1000
        if start_time == 0 or not last_token == a[1]:
            start_time = now
            last_token = a[1]
        elif now - start_time > 1000:
            if token_list[a[1]] == 'space':
                sentence += '_'
            else:
                sentence += token_list[a[1]]
            start_time = 1e18
            cv.putText(image, f"Recognize: {token_list[a[1]]}", (400, 100),
                       cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
    else:
        start_time == 0
    cv.putText(image, f"{sentence[1:]}", (400, 200), cv.FONT_HERSHEY_SIMPLEX,
               2, (0, 0, 255), 2)
    return image


model.eval()
start_listen(detection)
