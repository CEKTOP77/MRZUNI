import streamlit as st

# === контрольная цифра (по стандарту ICAO DOC 9303) ===
def mrz_check_digit(data: str) -> str:
    table = {**{str(i): i for i in range(10)},
             **{chr(i + 55): i for i in range(10, 36)},
             "<": 0}
    weights = [7, 3, 1]
    return str(sum(table.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data)) % 10)

# === преобразование даты ДДММГГ → ГГММДД ===
def convert_date(date_str: str) -> str:
    return date_str[4:6] + date_str[2:4] + date_str[0:2] if len(date_str) == 6 else date_str

# === генерация MRZ TD3 ===
def generate_mrz_td3(doc_type, country, nationality,
                     lastname, firstname, number,
                     birth, expiry, sex, extra):

    # нормализация
    lastname = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    number = number.upper()
    country = country.upper()
    nationality = nationality.upper()
    sex = sex.upper() if sex else "<"
    extra = extra.upper().replace(" ", "<")
    birth, expiry = convert_date(birth), convert_date(expiry)

    # контрольные цифры отдельных полей
    num_cd = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd = mrz_check_digit(expiry)

    # первая строка
    line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]

    # формирование второй строки (тело)
    optional_data = extra.ljust(14, "<")[:14]
    body = f"{number}{num_cd}{nationality}{birth}{birth_cd}{sex}{expiry}{exp_cd}{optional_data}"
    final_cd = mrz_check_digit(body)

    # теперь гарантируем длину 44 и ставим финальный чек‑символ последним
    if len(body) >= 44:
        line2 = body[:44] + final_cd
    else:
        line2 = body.ljust(44, ) + final_cd

    return [line1, line2]

# === генерация MRZ TD1 ===
def generate_mrz_td1(doc_type, country, nationality,
                     lastname, firstname, number,
                     birth, expiry, sex, extra):
    lastname = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    number = number.upper()
    country = country.upper()
    nationality = nationality.upper()
    sex = sex.upper() if sex else "<"
    extra = extra.upper().replace(" ", "<")
    birth, expiry = convert_date(birth), convert_date(expiry)

    num_cd = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd = mrz_check_digit(expiry)

    line1 = f"{doc_type}<{country}{number}{num_cd}".ljust(30, "<")[:30]
    base2 = f"{birth}{birth_cd}{sex}{expiry}{exp_cd}{nationality}{extra[:14]}"
    temp2 = base2.ljust(29, "<")
    final_cd = mrz_check_digit(line1 + temp2)
    line2 = temp2 + final_cd
    line3 = f"{lastname}<<{firstname}".ljust(30, "<")[:30]

    return [line1, line2, line3]

# === интерфейс Streamlit ===
st.set_page_config(page_title="Универсальный MRZ Генератор", layout="centered")
st.title("🌍 Универсальный MRZ‑генератор (ICAO DOC 9303)")

def clear_fields():
    for key in ["doc_type","country","nationality","lastname","firstname",
                "number","birth","expiry","sex","extra"]:
        st.session_state[key] = ""

format_type = st.selectbox("Формат документа", ["TD3 (Паспорт, 2×44)","TD1 (ID‑карта, 3×30)"])
doc_type    = st.text_input("Тип", "P", key="doc_type")
country     = st.text_input("Страна (3 буквы)", "USA", key="country")
nationality = st.text_input("Гражданство (3 буквы)", "USA", key="nationality")
lastname    = st.text_input("Фамилия", "HULTON", key="lastname")
firstname   = st.text_input("Имя", "DAVID NAKAMURA", key="firstname")
number      = st.text_input("Номер документа", "A09913982", key="number")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383", key="birth")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133", key="expiry")
sex         = st.selectbox("Пол", ["M","F","<"], index=0, key="sex")
extra       = st.text_input("Extra Info (до 14 символов)", "534397504", key="extra")

col1,col2 = st.columns(2)
with col1:
    gen = st.button("📄 Сгенерировать MRZ")
with col2:
    clr = st.button("🧹 Очистить все поля", on_click=clear_fields)

if gen:
    try:
        if format_type.upper().startswith("TD3"):
            lines = generate_mrz_td3(doc_type, country, nationality,
                                     lastname, firstname, number,
                                     birth, expiry, sex, extra)
        else:
            lines = generate_mrz_td1(doc_type, country, nationality,
                                     lastname, firstname, number,
                                     birth, expiry, sex, extra)

        st.success("✅ MRZ зуспешно сгенерирован!") 
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
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Ошибка: {e}")
