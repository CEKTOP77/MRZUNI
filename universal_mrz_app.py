# coding: utf-8
# MRZ TD3 Debug App — расчёт по стандарту ICAO DOC 9303 + отладочный вывод
import re
import unicodedata
import streamlit as st

st.set_page_config(page_title="MRZ TD3 Debug (ICAO DOC 9303)", layout="wide")

# ---------- Утилиты ----------
def sanitize(s: str) -> str:
    """Нормализовать строку: оставить только A-Z, 0-9, <"""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.upper()
    s = re.sub(r"[\s\u00A0\u202F\u200B\u2009]+", "<", s)
    s = re.sub(r"[^A-Z0-9<]", "", s)
    return s.strip()

def mrz_check_digit(data: str) -> str:
    """Контрольная цифра по весам 7-3-1 (ICAO)."""
    data = re.sub(r"[^A-Z0-9<]", "", data)
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            '<': 0}
    weights = [7, 3, 1]
    total = sum(vals.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data))
    return str(total % 10)

def convert_date(d: str) -> str:
    d = re.sub(r"[^0-9]", "", d)
    if len(d) >= 6:
        return d[4:6] + d[2:4] + d[0:2]
    return d

# ---------- Основной алгоритм ----------
def generate_and_debug(doc_type, country, nationality,
                       surname, given_names,
                       number, birth, expiry, sex, optional):

    surname = sanitize(surname)
    given_names = sanitize(given_names).replace(" ", "<")
    number = sanitize(number)
    country = sanitize(country)
    nationality = sanitize(nationality)
    sex = sanitize(sex)
    optional = sanitize(optional)
    birth, expiry = convert_date(sanitize(birth)), convert_date(sanitize(expiry))

    c_num = mrz_check_digit(number)
    c_birth = mrz_check_digit(birth)
    c_expiry = mrz_check_digit(expiry)

    # первая строка
    line1 = f"{doc_type}<{country}{surname}<<{given_names}"
    line1 = line1[:44].ljust(44, "<")

    # части второй строки
    part_num = f"{number}{c_num}"
    part_nat = nationality
    part_birth = f"{birth}{c_birth}"
    part_sex = sex
    part_exp = f"{expiry}{c_expiry}"
    part_opt = optional.ljust(14, "<")[:14]

    body = part_num + part_nat + part_birth + part_sex + part_exp + part_opt

    # field43 по стандарту TD3
    field43 = number + c_num + birth + c_birth + expiry + c_expiry + part_opt
    field43 = re.sub(r"[^A-Z0-9<]", "", field43)
    c43 = mrz_check_digit(field43)

    # финальная контрольная (44)
    body_clean = re.sub(r"[^A-Z0-9<]", "", body + c43)
    c44 = mrz_check_digit(body_clean)

    line2 = (body + c43 + c44)[:44]

    # отладочная информация
    debug_info = {
        "Номер": number,
        "Дата рождения (YYMMDD)": birth,
        "Дата окончания (YYMMDD)": expiry,
        "Optional (очищен)": part_opt,
        "CD номера": c_num,
        "CD рожд.": c_birth,
        "CD оконч.": c_expiry,
        "field43": field43,
        "Коды field43": [ord(c) for c in field43[-15:]],
        "43‑я цифра": c43,
        "44‑я цифра": c44
    }

    return line1, line2, debug_info


# ---------- Интерфейс ----------
st.title("🌍 MRZ TD3 Debug (по стандарту ICAO DOC 9303)")
st.caption("Показаны все промежуточные строки: номер, даты, контрольные, field43.")

col1, col2 = st.columns(2)
with col1:
    doc_type = st.text_input("Тип документа", "P")
    country = st.text_input("Страна (3 буквы)", "USA")
    nationality = st.text_input("Гражданство (3 буквы)", "USA")
with col2:
    sex = st.selectbox("Пол", ["M", "F", "<"], index=0)
    birth = st.text_input("Дата рождения (ДДММГГ)", "190383")
    expiry = st.text_input("Дата окончания (ДДММГГ)", "180133")

surname = st.text_input("Фамилия", "HULTON")
given_names = st.text_input("Имя (через пробел)", "DAVID NAKAMURA")
number = st.text_input("Номер документа", "A09913982")
optional = st.text_input("Доп. данные (до 14 символов)", "534397504<2872")

if st.button("📄 Посчитать MRZ"):
    line1, line2, debug = generate_and_debug(
        doc_type, country, nationality,
        surname, given_names, number,
        birth, expiry, sex, optional)

    st.header("Результат MRZ")
    st.code(f"{line1}\n{line2}", language="text")
    st.write("43‑й символ:", line2[42], "| 44‑й символ:", line2[43])
    st.header("Отладочная информация")
    for k, v in debug.items():
        st.write(f"**{k}:**", v)
