# coding: utf-8
import re
import streamlit as st

st.set_page_config(page_title="MRZ‑Generator TD3", layout="centered")

# --- Удаляем из ввода всё, кроме нужных символов ---
def clean(s):
    """Оставить только разрешённые символы: A‑Z, 0‑9, <"""
    if not s:
        return ""
    s = s.upper()
    s = re.sub(r"[^A-Z0-9<]", "", s)
    return s

def mrz_cd(data):
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            "<": 0}
    weights = [7, 3, 1]
    return str(sum(vals.get(ch, 0) * weights[i % 3]
                   for i, ch in enumerate(data)) % 10)

def conv_date(d):  # ДДММГГ -> ГГММДД
    d = re.sub(r"[^0-9]", "", d)
    return d[4:6] + d[2:4] + d[0:2]

def generate(doc_type, country, nationality,
             lastname, firstname, number,
             birth, expiry, sex, extra):

    lastname, firstname = clean(lastname), clean(firstname).replace(" ", "<")
    number, country, nationality = map(clean, [number, country, nationality])
    sex, extra = clean(sex), clean(extra)
    birth, expiry = conv_date(birth), conv_date(expiry)

    n_cd, b_cd, e_cd = mrz_cd(number), mrz_cd(birth), mrz_cd(expiry)

    line1 = f"{doc_type}<{country}{lastname}<<{firstname}"
    line1 = line1[:44].ljust(44, "<")

    part_num = f"{number}{n_cd}"
    part_nat = nationality
    part_birth = f"{birth}{b_cd}"
    part_sex = sex
    part_exp = f"{expiry}{e_cd}"
    part_opt = extra.ljust(14, "<")[:14]

    body = part_num + part_nat + part_birth + part_sex + part_exp + part_opt
    field43 = number + n_cd + birth + b_cd + expiry + e_cd + part_opt
    cd43 = mrz_cd(field43)
    cd44 = mrz_cd(body + cd43)
    line2 = (body + cd43 + cd44)[:44]

    return [line1, line2]


st.title("MRZ‑Генератор TD3 (очищает всё лишнее)")

doc_type    = st.text_input("Тип", "P")
country     = st.text_input("Страна", "USA")
nationality = st.text_input("Гражданство", "USA")
lastname    = st.text_input("Фамилия", "HULTON")
firstname   = st.text_input("Имя", "DAVID NAKAMURA")
number      = st.text_input("Номер", "A09913982")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133")
sex         = st.selectbox("Пол", ["M", "F", "<"], index=0)
extra       = st.text_input("Доп. данные", "534397504<2872")

if st.button("📄 Сгенерировать MRZ"):
    lines = generate(doc_type, country, nationality,
                     lastname, firstname, number,
                     birth, expiry, sex, extra)
    st.code("\n".join(lines), language="text")
    st.write("43‑й :", lines[1][42], "44‑й :", lines[1][43])
