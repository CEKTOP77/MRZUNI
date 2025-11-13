import streamlit as st

# === Контрольная цифра (ICAO DOC 9303, 7‑3‑1) ===
def mrz_check_digit(data: str) -> str:
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            '<': 0}
    weights = [7, 3, 1]
    return str(sum(vals.get(c, 0) * weights[i % 3] for i, c in enumerate(data)) % 10)

# === Формат даты ДДММГГ → ГГММДД ===
def convert_date(d: str) -> str:
    return d[4:6] + d[2:4] + d[0:2] if len(d) == 6 else d

# === Генерация MRZ TD3 (паспорт) ===
def generate_td3(doc_type, country, nationality,
                 lastname, firstname,
                 number, birth, expiry, sex, extra):

    lastname  = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    number    = number.upper()
    country   = country.upper()
    nationality = nationality.upper()
    sex = sex.upper()
    extra = extra.upper().replace(" ", "<")
    birth, expiry = convert_date(birth), convert_date(expiry)

    n_cd = mrz_check_digit(number)
    b_cd = mrz_check_digit(birth)
    e_cd = mrz_check_digit(expiry)

    # Первая строка
    line1 = f"{doc_type}<{country}{lastname}<<{firstname}"
    line1 = line1[:44].ljust(44, "<")

    # Вторая строка
    optional = extra.ljust(14, "<")[:14]
    body = f"{number}{n_cd}{nationality}{birth}{b_cd}{sex}{expiry}{e_cd}{optional}"
    final_cd = mrz_check_digit(body)

    # Формируем ровно 44 символа: 43 данных + контрольная
    line2 = body[:43] + final_cd
    return [line1, line2]

# === Генерация MRZ TD1 (ID‑карта) ===
def generate_td1(doc_type, country, nationality,
                 lastname, firstname,
                 number, birth, expiry, sex, extra):
    lastname  = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    number    = number.upper()
    country   = country.upper()
    nationality = nationality.upper()
    sex = sex.upper()
    extra = extra.upper().replace(" ", "<")
    birth, expiry = convert_date(birth), convert_date(expiry)

    n_cd = mrz_check_digit(number)
    b_cd = mrz_check_digit(birth)
    e_cd = mrz_check_digit(expiry)

    line1 = f"{doc_type}<{country}{number}{n_cd}".ljust(30, "<")[:30]
    base2 = f"{birth}{b_cd}{sex}{expiry}{e_cd}{nationality}{extra[:14]}"
    temp2 = base2.ljust(29, "<")
    final_cd = mrz_check_digit(line1 + temp2)
    line2 = temp2 + final_cd
    line3 = f"{lastname}<<{firstname}".ljust(30, "<")[:30]
    return [line1, line2, line3]

# === Очистка полей Streamlit ===
def clear_fields():
    for key in ["doc_type","country","nationality","lastname","firstname",
                "number","birth","expiry","sex","extra"]:
        st.session_state[key] = ""

# === Интерфейс Streamlit ===
st.set_page_config(page_title="Универсальный MRZ генератор", layout="centered")
st.title("🌍 Универсальный MRZ‑генератор (ICAO DOC 9303)")

format_type = st.selectbox("Формат документа", ["TD3 (Паспорт, 2×44)", "TD1 (ID‑карта, 3×30)"])
doc_type    = st.text_input("Тип документа", "P", key="doc_type")
country     = st.text_input("Код страны выдачи (3 буквы)", "USA", key="country")
nationality = st.text_input("Гражданство (3 буквы)", "USA", key="nationality")
lastname    = st.text_input("Фамилия", "HULTON", key="lastname")
firstname   = st.text_input("Имя", "DAVID NAKAMURA", key="firstname")
number      = st.text_input("Номер документа", "A09913982", key="number")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383", key="birth")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133", key="expiry")
sex         = st.selectbox("Пол", ["M","F","<"], index=0, key="sex")
extra       = st.text_input("Extra Info (до 14 символов)", "534397504<2872", key="extra")

col1, col2 = st.columns(2)
with col1:
    gen = st.button("📄 Сгенерировать MRZ")
with col2:
    clr = st.button("🧹 Очистить все поля", on_click=clear_fields)

if gen:
    try:
        if format_type.upper().startswith("TD3"):
            lines = generate_td3(doc_type, country, nationality,
                                 lastname, firstname,
                                 number, birth, expiry, sex, extra)
        else:
            lines = generate_td1(doc_type, country, nationality,
                                 lastname, firstname,
                                 number, birth, expiry, sex, extra)

        st.success("✅ MRZ успешно сгенерирован!")
        st.code("\n".join(lines), language="text")

        st.markdown(
            f"""
            <div style='border:1px solid #777;background:#e0e0e0;padding:15px;width:720px;border-radius:6px;'>
              <div style='background:#fff;padding:10px;font-family:Courier;'>
                <pre style='font-weight:bold;margin:0;line-height:1.2em;'>
{'\n'.join(lines)}
                </pre>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Ошибка: {e}")
