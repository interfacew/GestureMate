import json
from .Task import Task


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
            minz = min(minz, point[2])
        maxDelta = max(maxx-minx, maxy-miny)
        if maxDelta <= 1e-8:
            return [[0, 0, 0]]*len(points)
        for point in points:
            newx = (point[0]-(maxx+minx)/2)/maxDelta
            newy = (point[1]-(maxy+miny)/2)/maxDelta
            newz = (point[2]-(maxz+minz)/2)/(maxz-minz)/4
            if newx < -0.5-1e-8 or newx > 0.5+1e-8 or newy < -0.5-1e-8 or newy > 0.5+1e-8 or newz < -0.125-1e-8 or newz > 0.125+1e-8:
                print([point[0], point[1], point[2], newx, newy, newz,
                      maxDelta, maxx, maxy, minx, miny, maxz, minz])
                raise ValueError
            res.append([newx, newy, newz])
        return res

    def calcDelta(bodyPart, x, pose):
        delta = 0.0
        for part in bodyPart:
            if x[part] == None or pose[part] == None:
                return -1
            points = MatchTask.normalizePoints(x[part])
            match = MatchTask.normalizePoints(pose[part])
            if len(points) != len(match):
                raise ValueError(
                    f"Point count unmatch! Expect {len(match)} but find {len(points)}")
            for i in range(len(points)):
                delta += ((points[i][0]-match[i][0])**2+(points[i]
                          [1]-match[i][1])**2+(points[i][2]-match[i][2])**2)
        return delta

    def __init__(self, controller: object, id: str, bodyPart: list, poseFile: list, sensetive: list, frames: list,nextTasks: list = [], start: bool = True):
        super().__init__(controller, id, "Match", nextTasks, start)
        self.bodyPart = bodyPart
        self.pose = []
        self.poseName = []
        self.sensetive = sensetive
        self.frames=frames
        for file in poseFile:
            print(f"reading {file}")
            with open(file, "r") as f:
                self.pose.append(json.loads(f.read()))
            self.poseName.append(file.split('/')[-1].split('\\')[-1])

    def activate(self, x):
        self.count=[0]*len(self.pose)
        self.listen(x)

    def _listen(self, x):
        print(f"poses {str(self.poseName)}:")
        for i in range(len(self.pose)):
            delta = MatchTask.calcDelta(self.bodyPart[i], x, self.pose[i])
            print(f"\tpose {self.poseName[i]}, delta {delta:.5f} ({self.count[i]}/{self.frames[i]})", end="")
            if delta != -1 and delta < self.sensetive[i]:
                print("match")
                self.count[i]+=1
                if self.count[i]>=self.frames[i]:
                    self.process(x)
                    return
                continue
            print("")
            self.count[i]=0
