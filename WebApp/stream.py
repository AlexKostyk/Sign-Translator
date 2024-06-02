import streamlit as st
from streamlit_webrtc import webrtc_streamer
from static_hands import static_recognition
from dinamic_pose import pose_recognition, dinamic_recognition
from collections import Counter
import pandas as pd

frame_container = {"curr_frame": None}
actions_annotations_df = pd.read_csv('./actions_annotations.csv', sep=';')

def callback(frame):
    curr_frame = frame.to_ndarray(format="bgr24")

    frame_container["curr_frame"] = curr_frame

    return frame

def get_word(static_rec, dinamic_rec):
    if dinamic_rec == 'none' or dinamic_rec == 'static':
        return static_rec
    
    for index, row in actions_annotations_df.iterrows():
        if row['symbol'] == static_rec and row['action'] == dinamic_rec:
            return row['text']
    
    return static_rec

def start_stream():
   
    ctx = webrtc_streamer(
        key="example",
        video_frame_callback=callback,
        # rtc_configuration={
        #     "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        # }
    )

    keypoints_sequence = []
    static_recognitions = []
    prev_sign = None
    output_text = ''

    # streamlit_webrtc использует WebRTC для потоковой передачи видео и аудио. Ему требуется доступ к “STUN-серверу” в глобальной сети для удаленных одноранговых узлов (точнее, одноранговых узлов через NATs) для установления соединений WebRTC.
    
    progress_bar = st.progress(0)

    output_text_container = st.empty()
    output_text_container.text_area("Output Text", '', height=100, disabled=True)
    reset_button = st.button('Очистить')
    output_info_container = st.empty()

    while ctx.state.playing:
        curr_frame = frame_container["curr_frame"]

        if curr_frame is None:
            continue
        
        static_recognitions.append(static_recognition(curr_frame))

        keypoints_sequence.append(pose_recognition(curr_frame))

        progress_bar.progress(len(static_recognitions) / 30)

        if len(keypoints_sequence) >= 30:
            counter = Counter(static_recognitions)
            most_common_recognitions = counter.most_common(2)
            most_common_recognition = most_common_recognitions[0]

            if (len(most_common_recognitions) > 1 and most_common_recognition[0] == None):
                most_common_recognition = most_common_recognitions[1]

            if most_common_recognition[0] != None:
                dinamic_rec = dinamic_recognition(keypoints_sequence)
                curr_sign = get_word(most_common_recognition[0], dinamic_rec)
                if (curr_sign != prev_sign):
                    output_text += curr_sign + ' '

                    output_text_container.text_area("Output Text", output_text, height=100, disabled=True)
                    output_info_container.text(most_common_recognition[0] + ' ' + dinamic_rec)

                prev_sign = curr_sign

            static_recognitions = []
            keypoints_sequence = []
            progress_bar.progress(0)