import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import mediapipe.python.solutions as sol
import cv2
import random


def extract_landmarks(x):
    result = []
    if not x.pose_landmarks is None:
        a = x.pose_landmarks.landmark
        for i in range(len(a)):
            result.append([a[i].x, a[i].y, a[i].z])
    else:
        result += [[0, 0, 0]] * 33
    if not x.left_hand_landmarks is None:
        a = x.left_hand_landmarks.landmark
        for i in range(len(a)):
            result.append([a[i].x, a[i].y, a[i].z])
    else:
        result += [[0, 0, 0]] * 21
    if not x.right_hand_landmarks is None:
        a = x.right_hand_landmarks.landmark
        for i in range(len(a)):
            result.append([a[i].x, a[i].y, a[i].z])
    else:
        result += [[0, 0, 0]] * 21
    if not x.face_landmarks is None:
        a = x.face_landmarks.landmark
        for i in range(len(a)):
            result.append([a[i].x, a[i].y, a[i].z])
    else:
        result += [[0, 0, 0]] * 468
    assert len(result) == 543
    return result


MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green


def draw_hand_landmarks_on_image(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)
    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]
        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x,
                                            y=landmark.y,
                                            z=landmark.z)
            for landmark in hand_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            annotated_image, hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style())
        # Get the top left corner of the detected hand's bounding box.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN
        # Draw handedness (left or right hand) on the image.
        cv2.putText(annotated_image, f"{handedness[0].category_name}",
                    (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE,
                    HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)
    return annotated_image


def normalize(points):
    res = []
    maxx, maxy, minx, miny = -1, -1, 1, 1
    maxz, minz = -1, 1
    for point in points:
        maxx = max(maxx, point[0])
        maxy = max(maxy, point[1])
        minx = min(minx, point[0])
        miny = min(miny, point[1])
        maxz = max(maxz, point[2])
        minz = min(minz, point[2])
    max_delta = max(maxx - minx, maxy - miny)
    if max_delta <= 1e-5:
        return [[0, 0, 0]] * 21
    for point in points:
        newx = (point[0] - (maxx + minx) / 2) / max_delta
        newy = (point[1] - (maxy + miny) / 2) / max_delta
        newz = (point[2] - (maxz + minz) / 2) / (maxz - minz)
        if newx < -0.5 - 1e-6 or newx > 0.5 + 1e-6 or newy < -0.5 - 1e-6 or newy > 0.5 + 1e-6 or newz < -0.5 - 1e-6 or newz > 0.5 + 1e-6:
            print([
                point[0], point[1], newx, newy, max_delta, maxx, maxy, minx,
                miny
            ])
            raise ValueError
        res.append([newx, newy, newz])
    return res


def rotate_points(points):
    output_rotated_points = []
    angle = random.randint(-15, 15)
    rad_angle = np.deg2rad(angle)
    rotation_matrix = np.array([[np.cos(rad_angle), -np.sin(rad_angle), 0],
                                [np.sin(rad_angle),
                                 np.cos(rad_angle), 0], [0, 0, 1]])
    for point in points:
        rotated_points = np.dot(point, rotation_matrix)
        output_rotated_points.append(rotated_points.tolist())
    return output_rotated_points


def modify(x):
    normalize(rotate_points(np.array(x)))
    if random.randint(0, 1) == 0:
        x = [[-i[0], -i[1], i[2]] for i in x]
    return x


def draw_styled_landmarks(image, results):
    # Draw face connections
    sol.drawing_utils.draw_landmarks(
        image,
        results.face_landmarks,
        sol.holistic.FACEMESH_TESSELATION,
        landmark_drawing_spec=None,
        connection_drawing_spec=sol.drawing_styles.
        get_default_face_mesh_tesselation_style())
    sol.drawing_utils.draw_landmarks(
        image,
        results.face_landmarks,
        sol.holistic.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=sol.drawing_styles.
        get_default_face_mesh_contours_style())
    # Draw pose connections
    sol.drawing_utils.draw_landmarks(
        image, results.pose_landmarks, sol.holistic.POSE_CONNECTIONS,
        sol.drawing_styles.get_default_pose_landmarks_style())
    # Draw left hand connections
    sol.drawing_utils.draw_landmarks(
        image, results.left_hand_landmarks, sol.holistic.HAND_CONNECTIONS,
        sol.drawing_styles.get_default_hand_landmarks_style(),
        sol.drawing_styles.get_default_hand_connections_style())
    # Draw right hand connections
    sol.drawing_utils.draw_landmarks(
        image, results.right_hand_landmarks, sol.holistic.HAND_CONNECTIONS,
        sol.drawing_styles.get_default_hand_landmarks_style(),
        sol.drawing_styles.get_default_hand_connections_style())


train_dir = "..\\dataset\\data\\"
train_detect = "..\\dataset\\data_detect\\"
hand_path = '.\\hand_landmarker.task'
