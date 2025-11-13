import streamlit as st

# === контрольная цифра ===
def mrz_check_digit(data: str) -> str:
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              '<': 0}
    weights = [7, 3, 1]
    return str(sum(values.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data)) % 10)

# === формат даты ДДММГГ → ГГММДД ===
def convert_date(d: str) -> str:
    return d[4:6] + d[2:4] + d[0:2] if len(d) == 6 else d

# === генерация MRZ ===
def generate_mrz(format_type, doc_type, country, nationality,
                 lastname, firstname, doc_number,
                 birth, expiry, sex, extra_info):

    lastname = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    doc_number = doc_number.upper()
    country = country.upper()
    nationality = nationality.upper()
    sex = sex.upper() if sex else "<"
    extra_info = extra_info.upper().replace(" ", "<")
    birth, expiry = convert_date(birth), convert_date(expiry)

    doc_cd = mrz_check_digit(doc_number)
    birth_cd = mrz_check_digit(birth)
    expiry_cd = mrz_check_digit(expiry)

    # --- TD3 (паспорт)
    if format_type.upper().startswith("TD3"):
        line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]

        optional = extra_info.ljust(14, "<")[:14]
        body = f"{doc_number}{doc_cd}{nationality}{birth}{birth_cd}{sex}{expiry}{expiry_cd}{optional}"
        final_cd = mrz_check_digit(body)

        # объединяем тело и checksum
        line2 = body + final_cd
        # если получилась длиннее 44 -> обрезать только лишнее, но сохраняем последнюю цифру
        if len(line2) > 44:
            line2 = line2[:44]
        # если короче -> добить до 44
        elif len(line2) < 44:
            line2 = line2.ljust(44, "<")

        return [line1, line2]

    # --- TD1 (ID‑карта)
    if format_type.upper().startswith("TD1"):
        line1 = f"{doc_type}<{country}{doc_number}{doc_cd}".ljust(30, "<")[:30]
        base2 = f"{birth}{birth_cd}{sex}{expiry}{expiry_cd}{nationality}{extra_info[:14]}"
        temp2 = base2.ljust(29, "<")
        final_cd = mrz_check_digit(line1 + temp2)
        line2 = temp2 + final_cd
        line3 = f"{lastname}<<{firstname}".ljust(30, "<")[:30]
        return [line1, line2, line3]

    raise ValueError(f"Неизвестный формат: {format_type}")

# === Streamlit интерфейс ===
st.set_page_config(page_title="Универсальный MRZ Генератор", layout="centered")
st.title("🌍 Универсальный MRZ‑генератор (ICAO DOC 9303)")

def clear_fields():
    for f in ["doc_type","country","nationality","lastname","firstname",
              "doc_number","birth","expiry","sex","extra_info"]:
        st.session_state[f] = ""

format_type = st.selectbox("Формат документа", ["TD3 (Паспорт, 2x44)", "TD1 (ID‑карта, 3x30)"])
doc_type    = st.text_input("Тип документа", "P", key="doc_type")
country     = st.text_input("Код страны выдачи (3 буквы)", "USA", key="country")
nationality = st.text_input("Гражданство (3 буквы)", "USA", key="nationality")
lastname    = st.text_input("Фамилия", "HULTON", key="lastname")
firstname   = st.text_input("Имя", "DAVID NAKAMURA", key="firstname")
doc_number  = st.text_input("Номер документа", "A09913982", key="doc_number")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383", key="birth")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133", key="expiry")
sex         = st.selectbox("Пол", ["M", "F", "<"], index=0, key="sex")
extra_info  = st.text_input("Extra Info (до 14 символов)", "534397504", key="extra_info")

col1, col2 = st.columns(2)
with col1:
    gen = st.button("📄 Сгенерировать MRZ")
with col2:
    clr = st.button("🧹 Очистить все поля", on_click=clear_fields)

if gen:
    try:
        mrz = generate_mrz(format_type, doc_type, country, nationality,
                           lastname, firstname, doc_number,
                           birth, expiry, sex, extra_info)
        st.success("✅ MRZ успешно сгенерирован!")
        st.code("\n".join(mrz), language="text")
    except Exception as e:
        st.error(f"Ошибка: {e}")
