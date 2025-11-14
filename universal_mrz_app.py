# coding: utf-8
# Генератор MRZ TD3 по стандарту ICAO DOC 9303 (паспорт)
import re
import unicodedata
import streamlit as st

st.set_page_config(page_title="MRZ Generator TD3 (ICAO DOC 9303)", layout="centered")


# ---------- утилиты ----------
def sanitize(s: str) -> str:
    """Очистить строку: убрать пробелы, невидимые символы, оставить A‑Z, 0‑9, <"""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.upper()
    s = re.sub(r"[\s\u00A0\u202F\u200B\u2009]+", "<", s)
    s = re.sub(r"[^A-Z0-9<]", "", s)
    return s.strip()


def mrz_check_digit(data: str) -> str:
    """Вычисление контрольной цифры по весам 7‑3‑1 (ICAO DOC 9303)"""
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            '<': 0}
    weights = [7, 3, 1]
    total = 0
    for i, ch in enumerate(data):
        total += vals.get(ch, 0) * weights[i % 3]
    return str(total % 10)


def convert_date(d: str) -> str:
    """ДДММГГ -> ГГММДД"""
    d = re.sub(r"[^0-9]", "", d)
    if len(d) >= 6:
        return d[4:6] + d[2:4] + d[0:2]
    return d


# ---------- генератор TD3 ----------
def generate_mrz_td3(doc_type, country, nationality,
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

    # контрольные числа отдельных полей
    cd_number = mrz_check_digit(number)
    cd_birth = mrz_check_digit(birth)
    cd_expiry = mrz_check_digit(expiry)

    # --- первая строка ---
    line1 = f"{doc_type}<{country}{surname}<<{given_names}"
    line1 = line1[:44].ljust(44, "<")

    # --- вторая строка ---
    part_num = f"{number}{cd_number}"
    part_nat = nationality
    part_birth = f"{birth}{cd_birth}"
    part_sex = sex
    part_exp = f"{expiry}{cd_expiry}"
    part_opt = optional.ljust(14, "<")[:14]

    body = part_num + part_nat + part_birth + part_sex + part_exp + part_opt

    # 43‑я контрольная: номер + cd + рожд + cd + окончание + cd + optional
    field43 = number + cd_number + birth + cd_birth + expiry + cd_expiry + part_opt
    cd43 = mrz_check_digit(field43)

    # 44‑я контрольная: вся строка + cd43
    cd44 = mrz_check_digit(body + cd43)

    line2 = (body + cd43 + cd44)[:44]
    return [line1, line2]


# ---------- интерфейс ----------
st.title("🌍 MRZ‑генератор TD3 (ICAO DOC 9303)")
st.caption("Стандартный алгоритм расчёта контрольных цифр 7‑3‑1 для паспортов TD3.")

col1, col2 = st.columns(2)
with col1:
    doc_type = st.text_input("Тип документа", "P")
    country = st.text_input("Страна (3 буквы)", "USA")
    nationality = st.text_input("Гражданство (3 буквы)", "USA")
with col2:
    sex = st.selectbox("Пол", ["M","F","<"], index=0)
    birth = st.text_input("Дата рождения (ДДММГГ)", "190383")
    expiry = st.text_input("Дата окончания (ДДММГГ)", "180133")

surname = st.text_input("Фамилия", "HULTON")
given_names = st.text_input("Имя (через пробел)", "DAVID NAKAMURA")
number = st.text_input("Номер документа", "A09913982")
optional = st.text_input("Дополнительные данные (до 14 символов)", "534397504<2872")

if st.button("📄 Сгенерировать MRZ"):
    try:
        line1, line2 = generate_mrz_td3(doc_type, country, nationality,
                                        surname, given_names,
                                        number, birth, expiry, sex, optional)

        st.success("✅ !!! успешно сгенерирован")
        st.code(f"{line1}\n{line2}", language="text")
        st.write("43‑й символ:", line2[42], "44‑й символ:", line2[43])
    except Exception as e:
        st.error(f"Ошибка: {e}")
