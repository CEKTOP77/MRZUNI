# coding: utf-8
import re
import streamlit as st

st.set_page_config(page_title="MRZ Генератор (гарантированный результат)", layout="centered")


# -------- 1. Чистка входных данных --------
def sanitize(s: str) -> str:
    """
    Превращает любую строку в допустимую для MRZ:
    только A-Z, 0-9 и <.
    Все пробелы, невидимые и не-ASCII символы заменяются на <.
    """
    if not s:
        return ""
    # в верхний регистр
    s = s.upper()
    # заменить пробелы и невидимые символы на <
    s = re.sub(r"[\s\u00A0\u202F\u200B\u2009]+", "<", s)
    # оставить только разрешённые знаки
    s = re.sub(r"[^A-Z0-9<]", "", s)
    return s.strip()


# -------- 2. Контрольная цифра --------
def mrz_check_digit(data: str) -> str:
    """По стандарту ICAO DOC 9303 (веса 7‑3‑1)"""
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              "<": 0}
    weights = [7, 3, 1]
    total = 0
    for i, c in enumerate(data):
        total += values.get(c, 0) * weights[i % 3]
    return str(total % 10)


# -------- 3. Преобразование даты --------
def convert_date(d: str) -> str:
    d = re.sub(r"[^0-9]", "", d)
    if len(d) >= 6:
        return d[4:6] + d[2:4] + d[0:2]
    return d


# -------- 4. Генератор TD3 --------
def generate_td3(doc_type, country, nationality,
                 lastname, firstname, number,
                 birth, expiry, sex, extra):

    # Очистка всех данных
    lastname  = sanitize(lastname)
    firstname = sanitize(firstname)
    number    = sanitize(number)
    country   = sanitize(country)
    nationality = sanitize(nationality)
    sex       = sanitize(sex)
    extra     = sanitize(extra)
    birth, expiry = convert_date(sanitize(birth)), convert_date(sanitize(expiry))

    # Контрольные цифры отдельных полей
    num_cd   = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd   = mrz_check_digit(expiry)

    # Первая строка
    line1 = f"{doc_type}<{country}{lastname}<<{firstname}"
    line1 = line1[:44].ljust(44, "<")

    # Части второй строки
    part1 = f"{number}{num_cd}"
    part2 = nationality
    part3 = f"{birth}{birth_cd}"
    part4 = sex
    part5 = f"{expiry}{exp_cd}"
    part6 = extra.ljust(14, "<")[:14]

    # Тело (без итоговых контрольных)
    body = part1 + part2 + part3 + part4 + part5 + part6

    # 43‑я контрольная (по номеру, датам и optional)
    composite = number + num_cd + birth + birth_cd + expiry + exp_cd + part6
    cd43 = mrz_check_digit(composite)

    # 44‑я контрольная (для всей строки + предыдущая)
    cd44 = mrz_check_digit(body + cd43)

    line2 = (body + cd43 + cd44)[:44]
    return [line1, line2]


# -------- 5. Интерфейс Streamlit --------
st.title("🌍 MRZ‑генератор (устойчивый ко всем ошибкам ввода)")

doc_type    = st.text_input("Тип документа", "P")
country     = st.text_input("Код страны (3 буквы)", "USA")
nationality = st.text_input("Гражданство (3 буквы)", "USA")
lastname    = st.text_input("Фамилия", "HULTON")
firstname   = st.text_input("Имя", "DAVID NAKAMURA")
number      = st.text_input("Номер документа", "A09913982")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133")
sex         = st.selectbox("Пол", ["M","F","<"], index=0)
extra       = st.text_input("Доп. данные (до 14 символов)", "534397504<2872")

if st.button("📄 Сгенерировать MRZ"):
    try:
        lines = generate_td3(doc_type, country, nationality,
                             lastname, firstname, number,
                             birth, expiry, sex, extra)

        st.success("✅ MRZ успеш!!!!!!!!!!!!!!!!!!!!!!!!!!!!!сгенерирован")
        st.code("\n".join(lines), language="text")
        st.write("43‑й символ:", lines[1][42], "44‑й символ:", lines[1][43])

    except Exception as e:
        st.error(f"Ошибка: {e}")
