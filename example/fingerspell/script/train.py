import os
import cv2 as cv
import mediapipe as mp
from tqdm import tqdm
from utils import modify, draw_hand_landmarks_on_image, normalize, train_dir, train_detect, hand_path
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import random
import json
import numpy as np
import random
import os

token_list = []

HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult

hand_file = open(hand_path, "rb")
hand_data = hand_file.read()
hand_file.close()
base_options = mp.tasks.BaseOptions(model_asset_buffer=hand_data)
options = mp.tasks.vision.HandLandmarkerOptions(base_options=base_options,
                                                num_hands=1)
hand_detector = mp.tasks.vision.HandLandmarker.create_from_options(options)

if not os.path.exists(train_detect):
    os.mkdir(train_detect)
token_list = sorted(os.listdir(train_dir))
print(token_list)
with open(os.path.join(train_dir, "../tokenlist.json"), "w") as f:
    f.write(str(token_list))

if not os.path.exists(os.path.join(train_dir, "../datas_3d.json")):
    datas = []
    for i in range(len(token_list)):
        token = token_list[i]
        path = os.path.join(train_dir, token)
        detect_path = os.path.join(train_detect, token)
        if not os.path.exists(detect_path):
            os.mkdir(detect_path)
        files = os.listdir(path)
        cnt = 0
        for file in tqdm(files):
            image = cv.imread(os.path.join(path, file))
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                                data=np.array(
                                    cv.cvtColor(image, cv.COLOR_BGR2RGB)))
            result = hand_detector.detect(mp_image)
            if len(result.hand_landmarks) == 0:
                continue
            points = []
            for j in range(21):
                points.append([
                    result.hand_landmarks[0][j].x,
                    result.hand_landmarks[0][j].y,
                    result.hand_landmarks[0][j].z
                ])
            datas.append([i, points])
            image = draw_hand_landmarks_on_image(image, result)
            cv.imwrite(os.path.join(detect_path, file), image)
            cnt += 1
        print(f"image for {token}: total {len(files)}, detect {cnt}")

    with open(os.path.join(train_dir, "../datas_3d.json"), "w") as f:
        f.write(str(datas))

train_data = []
with open(os.path.join(train_dir, "../datas_3d.json"), "r") as f:
    train_data = json.loads(f.read())

train_data = [[x[0], normalize(x[1])] for x in tqdm(train_data)]


class myDataset(Dataset):

    def __init__(self, x):
        self.data = x

    def __getitem__(self, x):
        label = self.data[x][0]
        points = np.array(self.data[x][1])
        return label, points

    def __len__(self):
        return len(self.data)


random.shuffle(train_data)
test_data = train_data[:len(train_data) // 100]
train_data = train_data[len(train_data) // 100 + 1:]

train_dataset = myDataset(train_data)
train_loader = DataLoader(train_dataset, batch_size=64)
print(f"Loaded train data {len(train_dataset)}({len(train_loader)} batch)")

test_dataset = myDataset(test_data)
test_loader = DataLoader(test_dataset, batch_size=64)
print(f"Loaded test data {len(test_dataset)}({len(test_loader)} batch)")


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


def train(dataloader, model, loss_fn, optimizer):
    model.train()
    pbar = tqdm(dataloader)
    for y, X in pbar:
        X = [modify(i) for i in X.tolist()]
        X = torch.Tensor(X).to(device)
        y = torch.Tensor(y).to(device)
        pred = model(X)
        loss = loss_fn(pred, y)

        # Backpropagation
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        pbar.set_description(f"loss: {loss.item():.6f}")


def test(dataloader, model, loss_fn):
    model.eval()
    pbar = tqdm(dataloader)
    losssum = 0
    cnt = 0
    acc = 0
    for y, X in pbar:
        X = torch.Tensor(X).type(torch.float).to(device)
        y = torch.Tensor(y).to(device)
        pred = model(X)
        loss = loss_fn(pred, y)
        acc += (pred.argmax(1) == y).type(torch.float).sum().item()
        losssum += loss.item()
        cnt += 1
    print(f"loss {losssum/cnt} acc {acc/len(dataloader.dataset)}")


device = 'cuda'
model = SignClassifier()
model.to(device)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

epoch = 5

for i in range(epoch):
    print(f"Epoch {i+1}")
    train(train_loader, model, loss_fn, optimizer)
    test(test_loader, model, loss_fn)

torch.save(model, 'PointDetect_3d.pth')
