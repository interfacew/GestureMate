import json
from TaskController import TaskController
from Task import Task
import sys
sys.path.append("..")


class MatchTask(Task):
    def normalizePoints(points):
        res = []
        maxx, maxy, maxz, minx, miny, minz = -1, -1, -1, 1, 1, 1
        for point in points:
            maxx = max(maxx, point[0])
            maxy = max(maxy, point[1])
            maxz = max(maxz, point[2])
            minx = min(minx, point[0])
            miny = min(miny, point[1])
            maxz = min(minz, point[2])
        maxDelta = max(maxx-minx, maxy-miny)
        if maxDelta <= 1e-6:
            return [[0, 0, 0]]*len(points)
        for point in points:
            newx = (point[0]-(maxx+minx)/2)/maxDelta
            newy = (point[1]-(maxy+miny)/2)/maxDelta
            newz = (point[2]-(maxz+minz)/2)/(maxz-minz)/4
            if newx < -0.5-1e-6 or newx > 0.5+1e-6 or newy < -0.5-1e-6 or newy > 0.5+1e-6 or newz < -0.125-1e-6 or newz > 0.125+1e-6:
                print([point[0], point[1], point[2], newx, newy, newz,
                      maxDelta, maxx, maxy, minx, miny, maxz, minz])
                raise ValueError
            res.append([newx, newy, newz])
        return res

    def __init__(self, controller: TaskController, id: str, bodyPart: list, poseFile: list, sensetive: list, nextTasks: list = [], start: bool = True, command: list = []):
        super().__init__(controller, id, "Match", nextTasks, start, command)
        self.bodyPart = bodyPart
        self.pose = []
        self.poseName = []
        self.sensetive = sensetive
        for file in poseFile:
            print(f"reading {file}")
            with open(file, "r") as f:
                self.pose.append(json.loads(f.read()))
            self.poseName.append(file.split('/')[-1].split('\\')[-1])

    def _listen(self, x):
        print(f"poses {str(self.poseName)}:")
        for i in range(len(self.pose)):
            delta = 0.0
            for part in self.bodyPart[i]:
                flag = False
                for i in range(len(x[part])):
                    if x[part][i][0] > 1e-6 and x[part][i][1] > 1e-6 and x[part][i][2] > 1e-6:
                        flag = True
                        break
                if not flag:
                    print("")
                    return
                points = MatchTask.normalizePoints(x[part])
                match = MatchTask.normalizePoints(self.pose[i][part])
                if len(points) != len(match):
                    raise ValueError(
                        f"Point count unmatch! Expect {len(match)} but find {len(points)}")
                for i in range(len(points)):
                    delta += ((points[i][0]-match[i][0])**2+(points[i]
                              [1]-match[i][1])**2+(points[i][2]-match[i][2])**2)
            print(f"\tpose {self.poseName[i]}, delta {delta:.5f} ", end="")
            if delta < self.sensetive[i]:
                print("match")
                self.process()
                return
            print("")
