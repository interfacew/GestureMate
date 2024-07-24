from tasks import *
import json
import cv2 as cv
from utils import drawLandmarks, extractLandmarks
import mediapipe.python.solutions as sol


class TaskController:
    def __init__(self):
        self.tasks = {}
        self.activate = {}

    def listen(self, x):
        for i in self.tasks.keys():
            if self.activate[i]:
                self.tasks[i].listen(x)

    def activateTask(self, id: str):
        if not id in self.activate.keys():
            print(f"Unknown task id {id}")
            return
        self.activate[id] = True
        self.tasks[id].activate()

    def deactivateTask(self, id: str):
        if not id in self.activate.keys():
            print(f"Unknown task id {id}")
            return
        self.activate[id] = False
        self.tasks[id].deactivate()

    def removeTask(self, id: str):
        self.activate.pop(id)

    def addTask(self, task: Task):
        self.tasks[id] = task
        self.activate[id] = task.start

    def clear(self):
        self.tasks = {}
        self.Activate = {}

    def readConfig(self, path: str):
        with open(path, "r") as f:
            config = json.loads(f.read())
        for task in config:
            taskType = task['type']
            if taskType == "detect":
                taskObject = DetectTask(
                    self, task['id'], task['bodyPart'], task['nextTasks'], task['start'], task['command'])
            elif taskType == "match":
                taskObject = MatchTask(self, task['id'], task['bodyPart'], task['poseFile'],
                                       task['sensetive'], task['nextTasks'], task['start'], task['command'])
            elif taskType == "timeout":
                taskObject = TimeoutTask(
                    self, task['id'], task['timeout'], task['loop'], task['nextTasks'], task['start'], task['command'])
            self.addTask(taskObject)

    def startListen(self):
        camera = cv.VideoCapture(0, cv.CAP_DSHOW)
        camera.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        camera.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
        camera.set(cv.CAP_PROP_FPS, 60)
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
                    cv.imshow('OpenCV Feed', image)
                if cv.waitKey(20) & 0xFF == ord('q'):
                    break
            camera.release()
            cv.destroyAllWindows()
