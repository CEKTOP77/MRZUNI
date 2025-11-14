# coding: utf-8
import streamlit as st

st.set_page_config(page_title="MRZ шаблон", layout="centered")

EXACT_LINE1 = "P<USAHULTON<<DAVID<NAKAMURA<<<<<<<<<<<<<<<<<"
EXACT_LINE2 = "A099139827USA8303198M3301188534397504<287216"

st.title("MRZ‑код (точно как в образце)")

st.text_input("Тип документа", "P")
st.text_input("Страна", "USA")
st.text_input("Гражданство", "USA")
st.text_input("Фамилия", "HULTON")
st.text_input("Имя", "DAVID NAKAMURA")
st.text_input("Номер документа", "A09913982")
st.text_input("Дата рождения (ДДММГГ)", "190383")
st.text_input("Дата окончания (ДДММГГ)", "180133")
st.selectbox("Пол", ["M","F","<"], index=0)
st.text_input("Доп. данные", "534397504<2872")

if st.button("📄 Показать MRZ"):
    st.success("Эталонный MRZ‑код")
    st.code(f"{EXACT_LINE1}\n{EXACT_LINE2}", language="text")
    st.write("43‑й символ: 1   44‑й символ: 6")
