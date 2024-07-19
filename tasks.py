import json
from datetime import datetime
from utils import normalize_points
import os
import cv2 as cv
from utils import draw_styled_landmarks,extract_landmarks
import mediapipe.python.solutions as sol

class Task_controller:
    def __init__(self):
        self.tasks={}
        self.Activate={}
    def listen(self,x):
        for i in self.tasks.keys():
            if self.Activate[i]:
                self.tasks[i].listen(x)
    def activate(self,id):
        self.Activate[id]=True
        self.tasks[id].activate()
    def deactivate(self,id):
        self.Activate[id]=False
        self.tasks[id].deactivate()
    def add_task(self,id,name,data_type,match_data,sensetive,command="",start=True,next_tasks=[]):
        a=Task(self,id,name,data_type,match_data,sensetive,command,start,next_tasks)
        self.tasks[id]=a
        self.Activate[id]=start
    def clear(self):
        self.tasks={}
        self.Activate={}
    def read_config(self,path):
        with open(path,"r") as f:
            config=json.loads(f.read())
        for task in config:
            # print(task)
            self.add_task(task['id'],task['name'],task['data_type'],task['match_data'],
                          task['sensetive'],task['command'],task['start'],task['next_tasks'])
    def start_listen(self):
        camera=cv.VideoCapture(0,cv.CAP_DSHOW)
        camera.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        camera.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
        camera.set(cv.CAP_PROP_FPS,60)
        with sol.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2) as holistic:
            while camera.isOpened():
                ret, frame = camera.read()
                if ret:
                    frame=frame[:,::-1,:]

                    image = cv.cvtColor(frame, cv.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
                    image.flags.writeable = False                  # Image is no longer writeable
                    results = holistic.process(image)                 # Make prediction
                    image.flags.writeable = True                   # Image is now writeable
                    image = cv.cvtColor(image, cv.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR

                    draw_styled_landmarks(image, results)
                    self.listen(extract_landmarks(results))

                    cv.imshow('OpenCV Feed', image)

                if cv.waitKey(20) & 0xFF == ord('q'):
                    break
            camera.release()
            cv.destroyAllWindows()


class Task:
    def __init__(self,controller,id,name,data_type,match_data,sensetive,command="",start=True,next_tasks=[]):
        self.controller=controller
        self.id=id
        self.name=name
        if data_type=="time":
            self.data_type=data_type
            self.match_data=match_data
            self.activate_time=0
        else:
            self.data_type=data_type
            if match_data=="contain":
                self.match_data=match_data
            else:
                print(f"reading {match_data}")
                with open(match_data,"r") as f:
                    self.match_data=json.loads(f.read())
                self.pose_name=match_data.split('/')[-1].split('\\')[-1]
        self.sensetive=sensetive
        self.command=command
        self.start=start
        self.next_tasks=next_tasks
    def process(self):
        print(f"processing {self.name}")
        os.system(self.command)
        for i in self.next_tasks:
            if i['operator']=='start':
                self.controller.activate(i['id'])
            if i['operator']=='stop':
                self.controller.deactivate(i['id'])
    def activate(self):
        if self.data_type=="time":
            self.activate_time=datetime.now().timestamp()*1000
    def deactivate(self):
        pass
    def listen(self,x):
        print(f"listening {self.name}",end="")
        if self.data_type=="time":
            print(f", time last {self.match_data-(datetime.now().timestamp()*1000-self.activate_time)}")
            if datetime.now().timestamp()*1000-self.activate_time>=self.match_data:
                self.activate_time=0
                self.process()
            return
        if self.match_data=="contain":
            print(f", contain {self.data_type}")
            for data in self.data_type:
                if x[data][0][0]<=1e-6 and x[data][0][1]<=1e-6:
                    print("")
                    return
            self.process()
            return
        delta=0
        for data in self.data_type:
            if x[data][0][0]<=1e-6 and x[data][0][1]<=1e-6:
                print("")
                return
            points=normalize_points(x[data])
            match=normalize_points(self.match_data[data])
            if len(points)!=len(match):
                raise ValueError(f"Point count unmatch! Expect {len(match)} but find {len(points)}")
            for i in range(len(points)):
                delta+=((points[i][0]-match[i][0])**2+(points[i][1]-match[i][1])**2)**0.5
        print(f", pose {self.pose_name}, delta {delta:.5f}")
        if delta<self.sensetive:
            self.process()