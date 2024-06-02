import numpy as np
import cv2
import pandas as pd
import tensorflow as tf
import mediapipe as mp

mp_hands = mp.solutions.hands # модель mediapipe hands для обнаружения ключевых точек
hands = mp_hands.Hands( 
    static_image_mode=False, 
    model_complexity=1, 
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5, 
    max_num_hands=2)

# Загружаем модель
loaded_model = tf.keras.models.load_model('./models/static_model.h5')

actions_annotations_df = pd.read_csv('actions_annotations.csv', sep=';')

def extract_keypoints(results):
    # в results.multi_hand_landmarks первые ключевые точки это правая рука, а вторые - левая
    right_hand_landmarks = None
    left_hand_landmarks = None

    if results.multi_handedness != None:
        if len(results.multi_handedness) == 2:
            right_hand_landmarks = results.multi_hand_landmarks[0]
            left_hand_landmarks = results.multi_hand_landmarks[1]
        else:
            if results.multi_handedness[0].classification[0].index == 1: #index right hand
                right_hand_landmarks = results.multi_hand_landmarks[0]
            else:
                left_hand_landmarks = results.multi_hand_landmarks[0]
            

    # 21 ориентир и 3 координаты у каждого x, y, z
    right_hand_np = np.array([[res.x, res.y, res.z] for res in right_hand_landmarks.landmark]).flatten() if right_hand_landmarks != None else np.zeros(21 * 3)
    left_hand_np = np.array([[res.x, res.y, res.z] for res in left_hand_landmarks.landmark]).flatten() if left_hand_landmarks != None else np.zeros(21 * 3)

    return np.concatenate([right_hand_np, left_hand_np]) # содержит ключевые точки элементов, которые представляют сглаженный массив значений x, y, z


def hand_detection(frame):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image, results

def static_recognition(img):
    _, result = hand_detection(img)

    keypoints = extract_keypoints(result)

    if np.array_equal(keypoints, np.zeros(21 * 6)):
        return None

    # Изменяем форму массива на (1, 126)
    np_arr = keypoints.reshape(1, -1)

    return actions_annotations_df.at[np.argmax(loaded_model.predict(np_arr)), 'text']



# print(static_recognition(cv2.imread('./test_dinamic/' + str(0) + '.jpg')))