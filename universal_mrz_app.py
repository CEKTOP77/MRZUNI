# coding: utf-8
# MRZ TD3 generator (паспорта) по стандарту ICAO DOC 9303
import re
import unicodedata
import streamlit as st

st.set_page_config(page_title="MRZ Generator TD3 (ICAO DOC 9303)", layout="centered")


# ---------- Утилиты ----------
def sanitize(s: str) -> str:
    """Оставить только A-Z 0-9 <. Все пробелы и невидимые символы заменить на <"""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.upper()
    s = re.sub(r"[\s\u00A0\u202F\u200B\u2009]+", "<", s)
    s = re.sub(r"[^A-Z0-9<]", "", s)
    return s.strip()


def mrz_check_digit(data: str) -> str:
    """Контрольная цифра по весам 7-3-1"""
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              '<': 0}
    weights = [7, 3, 1]
    total = 0
    for i, c in enumerate(data):
        total += values.get(c, 0) * weights[i % 3]
    return str(total % 10)


def convert_date(d: str) -> str:
    """ДДММГГ -> ГГММДД"""
    d = re.sub(r"[^0-9]", "", d)
    return d[4:6] + d[2:4] + d[0:2] if len(d) >= 6 else d


# ---------- Генератор TD3 ----------
def generate_mrz_td3(doc_type, country, nationality,
                     surname, given_names,
                     number, birth, expiry, sex, optional):

    # Очистка входных данных
    surname = sanitize(surname)
    given_names = sanitize(given_names).replace(" ", "<")
    number = sanitize(number)
    country = sanitize(country)
    nationality = sanitize(nationality)
    sex = sanitize(sex)
    optional = sanitize(optional)
    birth = convert_date(sanitize(birth))
    expiry = convert_date(sanitize(expiry))

    # Контрольные цифры отдельных полей
    cd_number = mrz_check_digit(number)
    cd_birth  = mrz_check_digit(birth)
    cd_expiry = mrz_check_digit(expiry)

    # Первая строка (44 символа)
    line1 = f"{doc_type}<{country}{surname}<<{given_names}"
    line1 = line1[:44].ljust(44, "<")

    # Части второй строки
    part_num   = f"{number}{cd_number}"
    part_nat   = nationality
    part_birth = f"{birth}{cd_birth}"
    part_sex   = sex
    part_exp   = f"{expiry}{cd_expiry}"
    part_opt   = optional.ljust(14, "<")[:14]

    body = part_num + part_nat + part_birth + part_sex + part_exp + part_opt

    # -------- Контрольные цифры ----------------------------------------------------------------
    # 43-я: номер + cd + дата рождения + cd + дата окончания + cd + optional
    field43 = number + cd_number + birth + cd_birth + expiry + cd_expiry + part_opt
    field43 = re.sub(r"[^A-Z0-9<]", "", field43)   # зачистка от чужих знаков
    cd43 = mrz_check_digit(field43)

    # 44-я: вся строка + cd43
    full_body = re.sub(r"[^A-Z0-9<]", "", body + cd43)
    cd44 = mrz_check_digit(full_body)
    # --------------------------------------------------------------------------------------------

    line2 = (body + cd43 + cd44)[:44]
    return [line1, line2]


# ---------- Интерфейс Streamlit ----------
st.title("🌍 MRZ‑генератор TD3 (по ICAO DOC 9303)")
st.caption("Контрольные цифры вычисляются по весам 7‑3‑1 и стандарту TD3.")

doc_type    = st.text_input("Тип документа", "P")
country     = st.text_input("Страна (3 буквы)", "USA")
nationality = st.text_input("Гражданство (3 буквы)", "USA")
surname     = st.text_input("Фамилия", "HULTON")
given_names = st.text_input("Имя", "DAVID NAKAMURA")
number      = st.text_input("Номер документа", "A09913982")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133")
sex         = st.selectbox("Пол", ["M", "F", "<"], index=0)
optional    = st.text_input("Доп. данные (до 14 символов)", "534397504<2872")

if st.button("📄 Сгенерировать MRZ"):
    line1, line2 = generate_mrz_td3(doc_type, country, nationality,
                                    surname, given_names,
                                    number, birth, expiry, sex, optional)
    st.success("✅ MRZ успешно сгенерирован")
    st.code(f"{line1}\n{line2}", language="text")
    st.write("43‑й символ:", line2[42], "44‑й символ:", line2[43])
