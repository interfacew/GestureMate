import cv2 as cv
from utils import draw_styled_landmarks, extract_landmarks
import mediapipe.python.solutions as sol
import json


def get_data():
    camera = cv.VideoCapture(0, cv.CAP_DSHOW)
    camera.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    camera.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    camera.set(cv.CAP_PROP_FPS, 60)
    res = {}
    with sol.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2) as holistic:
        seq = []
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

                draw_styled_landmarks(image, results)

                cv.imshow('OpenCV Feed', image)

            if cv.waitKey(20) & 0xFF == ord('q'):
                break
            if cv.waitKey(20) & 0xFF == ord(' '):
                res = extract_landmarks(results)
                break
        camera.release()
        cv.destroyAllWindows()
    with open("./output.json", "w") as f:
        f.write(json.dumps(res))


if __name__ == "__main__":
    get_data()
