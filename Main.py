import os
from TaskController import TaskController
from ValidateConfig import ValidateConfig
import mediapipe.python.solutions as sol

if __name__ == "__main__":
    data_dir = r".\data"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if not os.path.exists(os.path.join(data_dir, "config.json")):
        with open(os.path.join(data_dir, "config.json"), "w") as f:
            f.write("[]")
        with sol.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2) as holistic:
            pass
        exit(0)

    os.chdir("./data")
    if not ValidateConfig("./config.json"):
        exit(0)

    controller = TaskController()
    controller.readConfig("config.json")
    controller.startListen()
