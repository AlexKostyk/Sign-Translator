import streamlit as st
from stream import start_stream
from translator import show_translator, reset_state
import pandas as pd

annotations_df = pd.read_csv('./slovo/annotations.csv', sep='\t')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

header = st.header("")

toggle_input = st.toggle('Сменить ввод', on_change=reset_state)

if toggle_input:
    header.text('Представление текста в жестах')

    show_translator(annotations_df)

else:
    header.text('Распознавание жестов')
    
    start_stream()
