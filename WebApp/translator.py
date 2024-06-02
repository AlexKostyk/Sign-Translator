import streamlit as st
import re

def reset_state():
    st.session_state.curr_index = 0
    st.session_state.input_text = []
    st.session_state.show_letters = False
    st.session_state.letter_index = 0

def get_video_path(text, annotations_df):
    for index, row in annotations_df.iterrows():
        row_text = row['text']
        if len(row_text) > 1:
            row_text = row_text.lower()
        if row_text == text and (row['height'] == 1920 or row['height'] == 1280):
            return f"./slovo/data/{row['attachment_id']}.mp4"
    return None

def highlight_word(text, word):
    highlighted_text = re.sub(
        r'(\b{}\b)'.format(re.escape(word)),
        r'<b class="highlighted-word">\1</b>',
        text,
        flags=re.IGNORECASE
    )
    return f'<div class="translate-sentence translate-border">{highlighted_text}</div>'

def highlight_letter(word, letter_index):
    highlighted_word = word[:letter_index] + f'<b class="highlighted-word">{word[letter_index]}</b>' + word[letter_index+1:]
    return f'<div class="translate-word translate-border">{highlighted_word}</div>'

def show_translator(annotations_df):
    # Инициализация состояния
    if 'input_text' not in st.session_state:
        st.session_state.input_text = []
    if 'curr_index' not in st.session_state:
        st.session_state.curr_index = 0
    if 'show_letters' not in st.session_state:
        st.session_state.show_letters = False
    if 'letter_index' not in st.session_state:
        st.session_state.letter_index = 0

    def prev():
        if st.session_state.show_letters:
            st.session_state.letter_index = (st.session_state.letter_index - 1) % len(st.session_state.input_text[st.session_state.curr_index])
        else:
            st.session_state.curr_index = (st.session_state.curr_index - 1) % len(st.session_state.input_text)

    def next():
        if st.session_state.show_letters:
            st.session_state.letter_index = (st.session_state.letter_index + 1) % len(st.session_state.input_text[st.session_state.curr_index])
        else:
            st.session_state.curr_index = (st.session_state.curr_index + 1) % len(st.session_state.input_text)

    def show_letters(word):
        st.session_state.show_letters = True
        st.session_state.letter_index = 0

    def show_video(index):
        word = st.session_state.input_text[index]
        if st.session_state.show_letters:
            letter = word[st.session_state.letter_index]
            video_path = get_video_path(letter.upper(), annotations_df)
            highlighted_word = highlight_letter(word, st.session_state.letter_index)
            col2.markdown(highlighted_word, unsafe_allow_html=True)
            if video_path:
                col2.video(video_path)
            else:
                st.markdown("<div style='margin-top: 265px;'></div>", unsafe_allow_html=True)

                col2.error(f'*Буква "{letter}" не найдена в базе данных*')

            _, back_col, _ = st.columns([1, 1.01, 1])
            with back_col:
                st.button('Вернуться к слову', on_click=lambda: setattr(st.session_state, 'show_letters', False))
        else:
            video_path = get_video_path(word.lower(), annotations_df)
            highlighted_sentence = highlight_word(textarea, word)
            col2.markdown(highlighted_sentence, unsafe_allow_html=True)
            if video_path:
                col2.video(video_path)
            else:
                st.markdown("<div style='margin-top: 250px;'></div>", unsafe_allow_html=True)

                col2.error(f'*Слово "{word}" представлено в виде последовательности дактильных букв*')

                _, show_lett_col, _ = st.columns([0.5, 1, 0.5])
                with show_lett_col:
                    st.button('Показать дактильные буквы', on_click=lambda: show_letters(word))

    textarea = st.text_area("Введите текст здесь")
    textarea_apply = st.button('Отправить')

    if textarea_apply and textarea != '':
        st.session_state.input_text = []
        st.session_state.curr_index = 0

        words = re.findall(r"[\w']+|[.,!?;]| ", textarea)
        st.session_state.input_text = [word for word in words if word.strip() not in [",", ".", "!", "?", ";", ""]]

    if len(st.session_state.input_text) > 0:
        col1, col2, col3, _ = st.columns([1, 5, 0.81, 0.19])

        with col1:
            col1.markdown("<div style='margin-top: 350px;'></div>", unsafe_allow_html=True)
            st.button('Назад', on_click=prev, key='nav_prev')

        with col2:
            show_video(st.session_state.curr_index)

        with col3:
            col3.markdown("<div style='margin-top: 350px;'></div>", unsafe_allow_html=True)
            st.button('Далее', on_click=next, key='nav_next')

