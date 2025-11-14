# coding: utf-8
# MRZ TD3 (паспорт) — корректный алгоритм + отладочная печать
import re
import unicodedata
import streamlit as st

st.set_page_config(page_title="MRZ TD3 (ICAO DOC 9303) — Debug & Clean", layout="wide")

# ---------- Вспомогательные ----------
def clean_field(s: str) -> str:
    """Удаляет всё кроме A-Z, 0-9 и '<'."""
    s = unicodedata.normalize("NFKC", s)
    s = s.upper()
    s = s.replace(" ", "<")
    s = re.sub(r"[^A-Z0-9<]", "", s)
    return s

def mrz_check_digit(data: str) -> str:
    """Контрольная цифра по весам 7-3-1 (ICAO)."""
    data = clean_field(data)
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            '<': 0}
    weights = [7, 3, 1]
    total = sum(vals.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data))
    return str(total % 10)

def convert_date(d: str) -> str:
    """ДДММГГ → ГГММДД"""
    d = re.sub(r"[^0-9]", "", d)
    return d[4:6] + d[2:4] + d[0:2] if len(d) >= 6 else d

# ---------- Основная функция ----------
def generate_td3_full(doc_type, country, nationality,
                      surname, given_names,
                      number, birth, expiry, sex, optional):

    # очистка
    surname = clean_field(surname)
    given_names = clean_field(given_names)
    number = clean_field(number)
    country = clean_field(country)
    nationality = clean_field(nationality)
    sex = clean_field(sex)
    optional = clean_field(optional)
    birth, expiry = convert_date(clean_field(birth)), convert_date(clean_field(expiry))

    # контрольные
    c_number = mrz_check_digit(number)
    c_birth = mrz_check_digit(birth)
    c_expiry = mrz_check_digit(expiry)

    # первая строка
    line1 = f"{doc_type}<{country}{surname}<<{given_names}"
    line1 = line1[:44].ljust(44, "<")

    # части второй строки
    part_num = f"{number}{c_number}"
    part_nat = nationality
    part_birth = f"{birth}{c_birth}"
    part_sex = sex
    part_exp = f"{expiry}{c_expiry}"
    part_opt = optional.ljust(14, "<")[:14]
    body = part_num + part_nat + part_birth + part_sex + part_exp + part_opt

    # --- контрольные ---
    field43 = clean_field(number) + c_number + clean_field(birth) + c_birth + clean_field(expiry) + c_expiry + clean_field(part_opt)
    cd43 = mrz_check_digit(field43)

    body_all = clean_field(body) + cd43
    cd44 = mrz_check_digit(body_all)

    line2 = (body + cd43 + cd44)[:44]

    debug = {
        "number": number, "birth": birth, "expiry": expiry, "optional": part_opt,
        "cd_number": c_number, "cd_birth": c_birth, "cd_expiry": c_expiry,
        "field43": field43, "len_field43": len(field43),
        "codes_tail": [ord(c) for c in field43[-15:]],
        "cd43": cd43, "cd44": cd44
    }

    return line1, line2, debug


# ---------- Интерфейс ----------
st.title("🌍 MRZ TD3 (ICAO DOC 9303) — Debug & Clean")
st.caption("Полный расчёт контрольных цифр 7‑3‑1, вывод промежуточных значений и очистка всех данных.")

col1, col2 = st.columns(2)
with col1:
    doc_type = st.text_input("Тип документа", "P")
    country = st.text_input("Страна (3 буквы)", "USA")
    nationality = st.text_input("Гражданство (3 буквы)", "USA")
    surname = st.text_input("Фамилия", "HULTON")
    given_names = st.text_input("Имя", "DAVID NAKAMURA")
with col2:
    number = st.text_input("Номер паспорта", "A09913982")
    birth = st.text_input("Дата рождения (ДДММГГ)", "190383")
    expiry = st.text_input("Дата окончания (ДДММГГ)", "180133")
    sex = st.selectbox("Пол", ["M","F","<"], index=0)
    optional = st.text_input("Доп. данные (до 14 символов)", "534397504<2872")

if st.button("📄 Рассчитать MRZ"):
    line1, line2, debug = generate_td3_full(doc_type, country, nationality,
                                            surname, given_names,
                                            number, birth, expiry, sex, optional)
    st.header("Результат MRZ")
    st.code(f"{line1}\n{line2}", language="text")
    st.write("43‑й символ:", line2[42], "44‑й символ:", line2[43])

    st.header("Отладочная информация")
    for k, v in debug.items():
        st.write(f"**{k}:**", v)
