# coding: utf-8
import streamlit as st
import re
import unicodedata

st.set_page_config(page_title="MRZ генератор (финальный)", layout="centered")

# --- очистка ввода ---
def normalize_input(s: str) -> str:
    """Удаляет невидимые символы, неразрывные пробелы и оставляет только корректные ASCII."""
    if not s:
        return ""
    # ещё раз нормализуем юникод
    s = unicodedata.normalize("NFKC", s)
    # убрать все невидимые символы и не-ASCII
    s = "".join(ch for ch in s if 32 <= ord(ch) <= 126)
    # заменить пробелы на '<'
    s = s.replace(" ", "<")
    return s.upper().strip()

# --- контрольная цифра ---
def mrz_check_digit(data: str) -> str:
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            '<': 0}
    weights = [7, 3, 1]
    total = 0
    for i, c in enumerate(data):
        total += vals.get(c, 0) * weights[i % 3]
    return str(total % 10)

# --- преобразование даты ---
def convert_date(d: str) -> str:
    d = re.sub(r"[^0-9]", "", d)
    if len(d) == 6:
        return d[4:6] + d[2:4] + d[0:2]
    return d

# --- генерация MRZ TD3 ---
def generate_td3(doc_type, country, nationality,
                 lastname, firstname, number,
                 birth, expiry, sex, extra):

    lastname  = normalize_input(lastname)
    firstname = normalize_input(firstname)
    number    = normalize_input(number)
    country   = normalize_input(country)
    nationality = normalize_input(nationality)
    sex = normalize_input(sex)
    extra = normalize_input(extra)
    birth, expiry = convert_date(birth), convert_date(expiry)

    # индивидуальные контрольные цифры
    num_cd   = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd   = mrz_check_digit(expiry)

    # первая строка
    line1 = f"{doc_type}<{country}{lastname}<<{firstname}"
    line1 = line1[:44].ljust(44, "<")

    # части второй строки
    part_num = f"{number}{num_cd}"
    part_nat = nationality
    part_birth = f"{birth}{birth_cd}"
    part_sex = sex
    part_exp = f"{expiry}{exp_cd}"
    part_opt = extra.ljust(14, "<")[:14]

    body = part_num + part_nat + part_birth + part_sex + part_exp + part_opt

    # контрольные суммы
    field43 = number + num_cd + birth + birth_cd + expiry + exp_cd + part_opt
    cd43 = mrz_check_digit(field43)
    cd44 = mrz_check_digit(body + cd43)

    line2 = (body + cd43 + cd44)[:44]
    return [line1, line2]

# --- интерфейс Streamlit ---
st.title("🌍 MRZ‑генератор TD3 (финальный, стабильный)")

doc_type    = st.text_input("Тип документа", "P")
country     = st.text_input("Страна (3 буквы)", "USA")
nationality = st.text_input("Гражданство (3 буквы)", "USA")
lastname    = st.text_input("Фамилия", "HULTON")
firstname   = st.text_input("Имя", "DAVID NAKAMURA")
number      = st.text_input("Номер документа", "A09913982")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133")
sex         = st.selectbox("Пол", ["M","F","<"], index=0)
extra       = st.text_input("Доп. данные (до 14 символов)", "534397504<2872")

if st.button("📄 Сгенерировать MRZ"):
    lines = generate_td3(doc_type, country, nationality,
                         lastname, firstname, number,
                         birth, expiry, sex, extra)
    st.subheader("Результат:")
    st.code("\n".join(lines), language="text")
    st.write("43‑й символ:", lines[1][42], "44‑й:", lines[1][43])
