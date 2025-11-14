# coding: utf-8
import streamlit as st
import unicodedata

st.set_page_config(page_title="MRZ генератор (точный)", layout="centered")

def clean_text(s: str) -> str:
    """Убираем неразрывные и невидимые пробелы"""
    s = unicodedata.normalize("NFKC", s)
    invisible = ["\u202f", "\u00a0", "\u200b", "\u2009"]
    for ch in invisible:
        s = s.replace(ch, "")
    return s

def mrz_check_digit(data: str) -> str:
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            '<': 0}
    weights = [7, 3, 1]
    return str(sum(vals.get(c, 0) * weights[i % 3] for i, c in enumerate(data)) % 10)

def convert_date(d: str) -> str:
    return d[4:6] + d[2:4] + d[0:2]

def generate_td3(doc_type, country, nationality,
                 lastname, firstname, number,
                 birth, expiry, sex, extra):

    lastname  = clean_text(lastname.upper().replace(" ", "<"))
    firstname = clean_text(firstname.upper().replace(" ", "<"))
    number    = clean_text(number.upper())
    country   = clean_text(country.upper())
    nationality = clean_text(nationality.upper())
    sex = clean_text(sex.upper())
    extra = clean_text(extra.upper().replace(" ", "<"))
    birth, expiry = convert_date(clean_text(birth)), convert_date(clean_text(expiry))

    num_cd   = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd   = mrz_check_digit(expiry)

    line1 = f"{doc_type}<{country}{lastname}<<{firstname}"
    line1 = line1[:44].ljust(44, "<")

    part_num   = f"{number}{num_cd}"
    part_nat   = nationality
    part_birth = f"{birth}{birth_cd}"
    part_sex   = sex
    part_exp   = f"{expiry}{exp_cd}"
    part_opt   = extra.ljust(14, "<")[:14]

    body = part_num + part_nat + part_birth + part_sex + part_exp + part_opt
    field43 = number + num_cd + birth + birth_cd + expiry + exp_cd + part_opt
    cd43 = mrz_check_digit(field43)
    cd44 = mrz_check_digit(body + cd43)
    line2 = (body + cd43 + cd44)[:44]

    return [line1, line2]

# ----- интерфейс -----
st.title("🌍 MRZ‑генератор (устойчивый к пробелам)")
doc_type    = st.text_input("Тип", "P")
country     = st.text_input("Страна (3 буквы)", "USA")
nationality = st.text_input("Гражданство (3 буквы)", "USA")
lastname    = st.text_input("Фамилия", "HULTON")
firstname   = st.text_input("Имя", "DAVID NAKAMURA")
number      = st.text_input("Номер", "A09913982")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133")
sex         = st.selectbox("Пол", ["M","F","<"], index=0)
extra       = st.text_input("Доп. данные", "534397504<2872")

if st.button("📄 Сгенерировать MRZ"):
    lines = generate_td3(doc_type, country, nationality,
                         lastname, firstname, number,
                         birth, expiry, sex, extra)
    st.code("\n".join(lines), language="text")
    st.write("43‑й символ:", lines[1][42], "44‑й символ:", lines[1][43])
