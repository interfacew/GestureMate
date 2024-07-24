import sys
sys.path.append("..")
from TaskController import TaskController
import os

class Task:
    def __init__(self,controller: TaskController,id: str,taskType: str,nextTasks: list =[],start: bool =True,command: list =[]):
        self.controller=controller
        self.id=id
        self.taskType=taskType
        self.nextTasks=nextTasks
        self.start=start
        self.command=command

    def activate(self):
        pass

    def deactivate(self):
        pass

    def process(self):
        print(f"processing {self.id}")
        for c in self.command:
            os.system(c)
        for i in self.next_tasks:
            if i['operate']=='start':
                self.controller.activate(i['id'])
            if i['operate']=='stop':
                self.controller.deactivate(i['id'])

    def _listen(self,x):
        raise NotImplementedError
    
    def listen(self,x):
        print(f"listening {self.name}, ",end="")
        self._listen(x)

