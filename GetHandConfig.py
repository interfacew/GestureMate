import cv2 as cv
from utils import drawLandmarks, extractLandmarks
import mediapipe.python.solutions as sol
import json
from tasks import MatchTask


def getData():
    camera = cv.VideoCapture(0, cv.CAP_DSHOW)
    camera.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    camera.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    camera.set(cv.CAP_PROP_FPS, 60)
    res = {}
    alert1 = "press s to save to result"
    alert2 = "press q to write to json file"
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

                cv.putText(image, f"{alert1}", (0, 25),
                           cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv.putText(image, f"{alert2}", (0, 50),
                           cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                if not res == {}:
                    now = extractLandmarks(results)
                    bodyDelta = MatchTask.calcDelta(['body'], now, res)
                    leftHandDelta = MatchTask.calcDelta(['leftHand'], now, res)
                    rightHandDelta = MatchTask.calcDelta(
                        ['rightHand'], now, res)
                    faceDelta = MatchTask.calcDelta(['face'], now, res)
                    cv.putText(image, f"body delta       : {bodyDelta:.5f}", (
                        0, 75), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv.putText(image, f"left hand delta  : {leftHandDelta:.5f}", (
                        0, 100), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv.putText(image, f"right hand delta : {rightHandDelta:.5f}", (
                        0, 125), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv.putText(image, f"face delta       : {faceDelta:.5f}", (
                        0, 150), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                cv.imshow('OpenCV Feed', image)
            if cv.waitKey(20) & 0xFF == ord('q'):
                break
            if cv.waitKey(20) & 0xFF == ord('s'):
                res = extractLandmarks(results)
                alert1 = "saved to result, press s to recover"
                break
        camera.release()
        cv.destroyAllWindows()
    with open("./output.json", "w") as f:
        f.write(json.dumps(res))


if __name__ == "__main__":
    getData()
