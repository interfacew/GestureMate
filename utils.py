import mediapipe.python.solutions as sol
def normalize_points(points):
    res=[]
    maxx,maxy,minx,miny=-1,-1,1,1
    for point in points:
        maxx=max(maxx,point[0])
        maxy=max(maxy,point[1])
        minx=min(minx,point[0])
        miny=min(miny,point[1])
    max_delta=max(maxx-minx,maxy-miny)
    if max_delta<=1e-5:
        return [[0,0]]*21
    for point in points:
        newx=(point[0]-(maxx+minx)/2)/max_delta
        newy=(point[1]-(maxy+miny)/2)/max_delta
        if newx<-0.5-1e-6 or newx>0.5+1e-6 or newy<-0.5-1e-6 or newy>0.5+1e-6:
            print([point[0],point[1],newx,newy,max_delta,maxx,maxy,minx,miny])
            raise ValueError
        res.append([newx,newy])
    return res

def draw_styled_landmarks(image, results):
    # Draw face connections
    sol.drawing_utils.draw_landmarks(image, results.face_landmarks,
                                     sol.holistic.FACEMESH_TESSELATION,
                                     landmark_drawing_spec=None,
                                     connection_drawing_spec=sol.drawing_styles.get_default_face_mesh_tesselation_style())
    sol.drawing_utils.draw_landmarks(image, results.face_landmarks,
                                     sol.holistic.FACEMESH_CONTOURS,
                                     landmark_drawing_spec=None,
                                     connection_drawing_spec=sol.drawing_styles.get_default_face_mesh_contours_style())
    # Draw pose connections
    sol.drawing_utils.draw_landmarks(image, results.pose_landmarks,
                                     sol.holistic.POSE_CONNECTIONS,
                                     sol.drawing_styles.get_default_pose_landmarks_style())
    # Draw left hand connections
    sol.drawing_utils.draw_landmarks(image, results.left_hand_landmarks,
                                     sol.holistic.HAND_CONNECTIONS,
                                     sol.drawing_styles.get_default_hand_landmarks_style(),sol.drawing_styles.get_default_hand_connections_style())
    # Draw right hand connections
    sol.drawing_utils.draw_landmarks(image, results.right_hand_landmarks,
                                     sol.holistic.HAND_CONNECTIONS,
                                     sol.drawing_styles.get_default_hand_landmarks_style(),sol.drawing_styles.get_default_hand_connections_style())

def extract_landmarks(x):
    res={}
    if not x.pose_landmarks is None:
        a=x.pose_landmarks.landmark
        b=[]
        for i in range(len(a)):
            b.append([a[i].x,a[i].y,a[i].z])
        res['pose']=b
    else:
        res['pose']=[[0,0,0]]*33
    if not x.left_hand_landmarks is None:
        a=x.left_hand_landmarks.landmark
        b=[]
        for i in range(len(a)):
            b.append([a[i].x,a[i].y,a[i].z])
        res['right_hand']=b
    else:
        res['right_hand']=[[0,0,0]]*21
    if not x.right_hand_landmarks is None:
        a=x.right_hand_landmarks.landmark
        b=[]
        for i in range(len(a)):
            b.append([a[i].x,a[i].y,a[i].z])
        res['left_hand']=b
    else:
        res['left_hand']=[[0,0,0]]*21
    if not x.face_landmarks is None:
        a=x.face_landmarks.landmark
        b=[]
        for i in range(len(a)):
            b.append([a[i].x,a[i].y,a[i].z])
        res['face']=b
    else:
        res['face']=[[0,0,0]]*468
    return res

