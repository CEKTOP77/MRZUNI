import streamlit as st

# === расчет контрольной цифры по ICAO DOC 9303 ===
def mrz_check_digit(data: str) -> str:
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              "<": 0}
    weights = [7, 3, 1]
    total = sum(values.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data))
    return str(total % 10)

# === преобразование даты ДДММГГ → ГГММДД ===
def convert_date(date_str: str) -> str:
    return date_str[4:6] + date_str[2:4] + date_str[0:2] if len(date_str) == 6 else date_str

# === генерация MRZ TD3 ===
def generate_mrz_td3(doc_type, country, nationality,
                     lastname, firstname, doc_number,
                     birth, expiry, sex, extra_info):

    lastname = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    doc_number = doc_number.upper()
    nationality = nationality.upper()
    country = country.upper()
    sex = sex.upper() if sex else "<"
    extra_info = extra_info.upper().replace(" ", "<")

    birth = convert_date(birth)
    expiry = convert_date(expiry)

    # контрольные цифры
    doc_cd = mrz_check_digit(doc_number)
    birth_cd = mrz_check_digit(birth)
    expiry_cd = mrz_check_digit(expiry)

    # первая строка
    line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]

    # вторая строка
    optional = extra_info.ljust(14, "<")[:14]
    body = f"{doc_number}{doc_cd}{nationality}{birth}{birth_cd}{sex}{expiry}{expiry_cd}{optional}"

    final_cd = mrz_check_digit(body)
    line2 = body + final_cd

    # если длиннее 44 — убираем лишний заполнитель перед checksum
    if len(line2) > 44:
        diff = len(line2) - 44
        line2 = line2[:-diff-1] + final_cd
    elif len(line2) < 44:
        line2 = line2.ljust(44, "<")

    return [line1, line2]

# === генерация MRZ TD1 ===
def generate_mrz_td1(doc_type, country, nationality,
                     lastname, firstname, doc_number,
                     birth, expiry, sex, extra_info):

    lastname = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    doc_number = doc_number.upper()
    nationality = nationality.upper()
    country = country.upper()
    sex = sex.upper() if sex else "<"
    extra_info = extra_info.upper().replace(" ", "<")

    birth = convert_date(birth)
    expiry = convert_date(expiry)

    doc_cd = mrz_check_digit(doc_number)
    birth_cd = mrz_check_digit(birth)
    expiry_cd = mrz_check_digit(expiry)

    line1 = f"{doc_type}<{country}{doc_number}{doc_cd}".ljust(30, "<")[:30]
    base2 = f"{birth}{birth_cd}{sex}{expiry}{expiry_cd}{nationality}{extra_info[:14]}"
    temp2 = base2.ljust(29, "<")
    final_cd = mrz_check_digit(line1 + temp2)
    line2 = temp2 + final_cd
    line3 = f"{lastname}<<{firstname}".ljust(30, "<")[:30]
    return [line1, line2, line3]

# === Streamlit интерфейс ===
st.set_page_config(page_title="Универсальный MRZ Генератор", layout="centered")
st.title("🌍 Универсальный MRZ‑генератор (ICAO DOC 9303)")

# очистка полей
def clear_fields():
    for key in ["doc_type","country","nationality","lastname","firstname",
                "doc_number","birth","expiry","sex","extra_info"]:
        st.session_state[key] = ""

# --- форма ---
format_type = st.selectbox("Формат документа", ["TD3 (Паспорт, 2x44)", "TD1 (ID‑карта, 3x30)"])
doc_type    = st.text_input("Тип документа", "P", key="doc_type")
country     = st.text_input("Код страны (3 буквы)", "USA", key="country")
nationality = st.text_input("Гражданство (3 буквы)", "USA", key="nationality")
lastname    = st.text_input("Фамилия", "HULTON", key="lastname")
firstname   = st.text_input("Имя", "DAVID NAKAMURA", key="firstname")
doc_number  = st.text_input("Номер документа", "A09913982", key="doc_number")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383", key="birth")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133", key="expiry")
sex         = st.selectbox("Пол", ["M", "F", "<"], index=0, key="sex")
extra_info  = st.text_input("Extra Info (до 14 символов)", "534397504<2872", key="extra_info")

col1, col2 = st.columns(2)
with col1:
    gen = st.button("📄 Сгенерировать MRZ")
with col2:
    clr = st.button("🧹 Очистить все поля", on_click=clear_fields)

if gen:
    try:
        if format_type.upper().startswith("TD3"):
            mrz_lines = generate_mrz_td3(doc_type, country, nationality,
                                         lastname, firstname, doc_number,
                                         birth, expiry, sex, extra_info)
        else:
            mrz_lines = generate_mrz_td1(doc_type, country, nationality,
                                         lastname, firstname, doc_number,
                                         birth, expiry, sex, extra_info)

        st.success("✅ MRZ успешно сгенерирован!")
        st.code("\n".join(mrz_lines), language="text")
        st.markdown(
            f"""
            <div style='border:1px solid #999;background:#e0e0e0;padding:15px;width:720px;border-radius:6px;'>
              <div style='background:#fff;padding:10px;font-family:Courier;'>
                <pre style='font-weight:bold;margin:0;line-height:1.2em;'>
{'\n'.join(mrz_lines)}
                </pre>
              </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Ошибка: {e}")
