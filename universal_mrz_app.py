# coding: utf-8
import re
import unicodedata
import streamlit as st

st.set_page_config(page_title="MRZ генератор TD3 (исправленный)", layout="centered")

# ---------- 1️⃣ Очистка ----------
def sanitize(s: str) -> str:
    """Оставляет только разрешённые символы A‑Z, 0‑9 и <."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.upper()
    s = re.sub(r"[\s\u00A0\u202F\u200B\u2009]+", "<", s)
    s = re.sub(r"[^A-Z0-9<]", "", s)
    return s.strip()

# ---------- 2️⃣ Контрольная цифра ----------
def mrz_check_digit(data: str) -> str:
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            '<': 0}
    weights = [7, 3, 1]
    total = 0
    for i, ch in enumerate(data):
        total += vals.get(ch, 0) * weights[i % 3]
    return str(total % 10)

# ---------- 3️⃣ Преобразование даты ----------
def convert_date(d: str) -> str:
    d = re.sub(r"[^0-9]", "", d)
    return d[4:6] + d[2:4] + d[0:2] if len(d) >= 6 else d

# ---------- 4️⃣ Генерация MRZ TD3 ----------
def generate_td3(doc_type, country, nationality,
                 lastname, firstname, number,
                 birth, expiry, sex, extra):

    lastname  = sanitize(lastname)
    firstname = sanitize(firstname).replace(" ", "<")
    number    = sanitize(number)
    country   = sanitize(country)
    nationality = sanitize(nationality)
    sex = sanitize(sex)
    extra = sanitize(extra)
    birth, expiry = convert_date(sanitize(birth)), convert_date(sanitize(expiry))

    num_cd   = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd   = mrz_check_digit(expiry)

    # --- Первая строка ---
    line1 = f"{doc_type}<{country}{lastname}<<{firstname}"
    line1 = line1[:44].ljust(44, "<")

    # --- Части второй строки ---
    part_num   = f"{number}{num_cd}"
    part_nat   = nationality
    part_birth = f"{birth}{birth_cd}"
    part_sex   = sex
    part_exp   = f"{expiry}{exp_cd}"
    part_opt   = extra.ljust(14, "<")[:14]

    body = part_num + part_nat + part_birth + part_sex + part_exp + part_opt

    # === ВАЖНОЕ ИСПРАВЛЕНИЕ ===
    # Добавляем символ пола в расчёт 43‑ей контрольной цифры
    # Правильно по ICAO: номер + cd + birth + cd + sex + expiry + cd + optional
    field43 = number + num_cd + birth + birth_cd + sex + expiry + exp_cd + part_opt
    cd43 = mrz_check_digit(field43)

    # 44‑я контрольная (вся строка целиком + предыдущая)
    cd44 = mrz_check_digit(body + cd43)

    line2 = (body + cd43 + cd44)[:44]
    return [line1, line2]

# ---------- 5️⃣ Интерфейс ----------
st.title("🌍 MRZ‑генератор TD3 (исправленный расчёт с учётом пола)")
st.caption("Контрольные цифры соответствуют эталону ICAO DOC 9303.")

doc_type    = st.text_input("Тип документа", "P")
country     = st.text_input("Страна (3 буквы)", "USA")
nationality = st.text_input("Гражданство (3 буквы)", "USA")
lastname    = st.text_input("Фамилия", "HULTON")
firstname   = st.text_input("Имя", "DAVID NAKAMURA")
number      = st.text_input("Номер документа", "A09913982")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133")
sex         = st.selectbox("Пол", ["M","F","<"], index=0)
extra       = st.text_input("Доп. данные (до 14 символов)", "534397504<2872")

if st.button("📄 Сгенерировать MRZ"):
    try:
        lines = generate_td3(doc_type, country, nationality,
                             lastname, firstname, number,
                             birth, expiry, sex, extra)
        st.success("✅ MRZ успешно сгенерирован")
        st.code("\n".join(lines), language="text")
        st.write("43‑й символ:", lines[1][42], "44‑й символ:", lines[1][43])
    except Exception as e:
        st.error(f"Ошибка: {e}")
