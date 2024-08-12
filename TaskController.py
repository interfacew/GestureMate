from tasks import *
import json
import cv2 as cv
from Utils import drawLandmarks, extractLandmarks
import mediapipe.python.solutions as sol
import time
from collections import deque


class TaskController:
    FPS_COUNT_FRAME=10

    def __init__(self):
        self.tasks = {}
        self.activate = {}

    def listen(self, x):
        print("\033[H\033[J")
        for i in self.tasks.keys():
            if self.activate[i]:
                self.tasks[i].listen(x)

    def activateTask(self, id: str, x):
        if not id in self.activate.keys():
            print(f"Unknown task id {id}")
            return
        self.activate[id] = True
        self.tasks[id].activate(x)

    def deactivateTask(self, id: str, x):
        if not id in self.activate.keys():
            print(f"Unknown task id {id}")
            return
        self.activate[id] = False
        self.tasks[id].deactivate(x)

    def removeTask(self, id: str):
        self.activate.pop(id)

    def addTask(self, task: Task):
        self.tasks[task.id] = task
        self.activate[task.id] = task.start

    def clear(self):
        self.tasks = {}
        self.Activate = {}

    def readConfig(self, path: str):
        with open(path, "r") as f:
            config = json.loads(f.read())
        for task in config:
            taskType = task['type']
            if taskType == "command":
                taskObject = CommandTask(
                    self, task['id'], task['command'], task['timeout'], task['nextTasks'], task['start'])
            elif taskType == "keypress":
                taskObject = TimeoutTask(
                    self, task['id'], task['keys'], task['nextTasks'], task['start'])
            elif taskType == "detect":
                taskObject = DetectTask(
                    self, task['id'], task['bodyPart'], task['frames'], task['nextTasks'], task['start'])
            elif taskType == "match":
                taskObject = MatchTask(self, task['id'], task['bodyPart'], task['poseFile'],
                                       task['sensetive'], task['frames'], task['nextTasks'], task['start'])
            elif taskType == "timeout":
                taskObject = TimeoutTask(
                    self, task['id'], task['timeout'], task['nextTasks'], task['start'])
            self.addTask(taskObject)

    def startListen(self):
        camera = cv.VideoCapture(0, cv.CAP_DSHOW)
        camera.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        camera.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
        camera.set(cv.CAP_PROP_FPS, 60)
        q=deque([],self.FPS_COUNT_FRAME)
        with sol.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2) as holistic:
            while camera.isOpened():
                ret, frame = camera.read()
                if ret:
                    frame = frame[:, ::-1, :]
                    # COLOR CONVERSION BGR 2 RGB
                    image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                    image.flags.writeable = False                  # Image is no longer writeable
                    # Make prediction
                    results = holistic.process(image)
                    image.flags.writeable = True                   # Image is now writeable
                    # COLOR COVERSION RGB 2 BGR
                    image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
                    drawLandmarks(image, results)
                    self.listen(extractLandmarks(results))

                    now=time.time_ns()
                    if len(q)>=self.FPS_COUNT_FRAME:
                        last=q.pop()
                        cv.putText(image,f"FPS: {self.FPS_COUNT_FRAME*1e9/(now-last)}",(10,10),cv.FONT_HERSHEY_COMPLEX,2.0,(255,0,0))

                    cv.imshow('OpenCV Feed', image)

                if cv.waitKey(20) & 0xFF == ord('q'):
                    break
            camera.release()
            cv.destroyAllWindows()
