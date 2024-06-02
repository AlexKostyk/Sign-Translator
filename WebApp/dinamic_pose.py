import numpy as np
import cv2
import tensorflow as tf
import mediapipe as mp

mp_pose = mp.solutions.pose # модель mediapipe hands для обнаружения ключевых точек
pose = mp_pose.Pose( 
    static_image_mode=False,
    model_complexity=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) # чем больше значение тем больше задержка, но и лучшая надёжность решения

# Загружаем модель
loaded_model = tf.keras.models.load_model('./models/dinamic_model.h5')

# Словарь действий
actions = ['none', 'down', 'right', 'shake', 'static', 'to_fist', 'up', 'z_write']

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)

    return pose

def pose_detection(frame):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image, results


def pose_recognition(img):
    _, result = pose_detection(img)
    keypoints = extract_keypoints(result)

    return keypoints


def dinamic_recognition(sequence):
    sequence = np.array(sequence)[:30].reshape(1, 30, -1)

    res = np.argmax(loaded_model.predict(sequence))
    
    return actions[res]


# images = []
# for i in range(30):
#     image = cv2.imread('./test_dinamic/' + str(i) + '.jpg')
#     images.append(image)

# dinamic_recognition(images)