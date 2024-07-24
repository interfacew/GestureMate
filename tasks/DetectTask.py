from Task import Task
import sys
sys.path.append("..")
from TaskController import TaskController

class DetectTask(Task):
    def __init__(self,controller: TaskController,id: str,bodyPart: list,nextTasks: list =[],start: bool =True,command: list =[]):
        super().__init__(controller,id,"Detect",nextTasks,start,command)
        self.bodyPart=bodyPart

    def _listen(self,x):
        print(f"detect {self.bodyPart}")
        for part in self.bodyPart:
            flag=False
            for i in range(len(x[part])):
                if x[part][i][0]>1e-6 and x[part][i][1]>1e-6 and x[part][i][2]>1e-6:
                    flag=True
                    break
            if not flag:
                print("")
                return
        print("")
        self.process()