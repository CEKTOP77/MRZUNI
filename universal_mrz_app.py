# coding: utf-8
import streamlit as st

st.set_page_config(page_title="Универсальный MRZ генератор",
                   page_icon="🪪",
                   layout="centered")
    total = sum(values.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data))
    return str(total % 10)

# === Преобразование даты ДДММГГ → ГГММДД ===
def convert_date(d: str) -> str:
    return d[4:6] + d[2:4] + d[0:2] if len(d) == 6 else d

# === Генерация MRZ TD3 (паспорт, 2×44) ===
def generate_td3(doc_type, country, nationality,
                 lastname, firstname, number,
                 birth, expiry, sex, extra):

    lastname  = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    number    = number.upper()
    country   = country.upper()
    nationality = nationality.upper()
    sex = sex.upper() if sex else "<"
    extra = extra.upper().replace(" ", "<")
    birth, expiry = convert_date(birth), convert_date(expiry)

    # Контрольные цифры отдельных полей
    num_cd   = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd   = mrz_check_digit(expiry)

    # Первая строка
    line1 = f"{doc_type}<{country}{lastname}<<{firstname}"
    line1 = line1[:44].ljust(44, "<")

    # Части второй строки (структура по ICAO DOC 9303)
    part1 = f"{number}{num_cd}"   # номер + cd
    part2 = nationality
    part3 = f"{birth}{birth_cd}"
    part4 = sex
    part5 = f"{expiry}{exp_cd}"
    part6 = extra.ljust(14, "<")[:14]

    # Тело без финальных контрольных чисел
    body = part1 + part2 + part3 + part4 + part5 + part6

    # 43‑я контрольная цифра — сводная по ключевым полям
    composite_data = part1 + part3 + part5 + part6
    check43 = mrz_check_digit(composite_data)

    # 44‑я контрольная цифра — для всей строки вместе с предыдущей
    check44 = mrz_check_digit(body + check43)

    # Финальная строка MRZ (44 символа)
    line2 = (body + check43 + check44)[:44]
    return [line1, line2]

# === Генерация MRZ TD1 (ID‑карта, 3×30) ===
def generate_td1(doc_type, country, nationality,
                 lastname, firstname, number,
                 birth, expiry, sex, extra):
    lastname  = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    number    = number.upper()
    country   = country.upper()
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

# === Очистка полей ===
def clear_fields():
    for key in ["doc_type","country","nationality","lastname","firstname",
                "number","birth","expiry","sex","extra"]:
        st.session_state[key] = ""

# === Интерфейс Streamlit ===
st.set_page_config(page_title="Универсальный MRZ генератор", layout="centered")
st.title("🌍 Универсальный MRZ‑генератор (ICAO DOC 9303)")

format_type = st.selectbox("Формат документа", ["TD3 (Паспорт 2×44)", "TD1 (ID‑карта 3×30)"])
doc_type    = st.text_input("Тип документа", "P", key="doc_type")
country     = st.text_input("Код страны выдачи (3 буквы)", "USA", key="country")
nationality = st.text_input("Гражданство (3 буквы)", "USA", key="nationality")
lastname    = st.text_input("Фамилия", "HULTON", key="lastname")
firstname   = st.text_input("Имя", "DAVID NAKAMURA", key="firstname")
number      = st.text_input("Номер документа", "A09913982", key="number")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383", key="birth")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133", key="expiry")
sex         = st.selectbox("Пол", ["M","F","<"], index=0, key="sex")
extra       = st.text_input("Дополнительные данные (до 14 символов)", "534397504<2872", key="extra")

col1, col2 = st.columns(2)
with col1:
    gen = st.button("📄 Сгенерировать MRZ")
with col2:
    clr = st.button("🧹 Очистить все поля", on_click=clear_fields)

if gen:
    try:
        if format_type.upper().startswith("TD3"):
            lines = generate_td3(doc_type, country, nationality,
                                 lastname, firstname, number,
                                 birth, expiry, sex, extra)
        else:
            lines = generate_td1(doc_type, country, nationality,
                                 lastname, firstname, number,
                                 birth, expiry, sex, extra)

        st.success("✅ ФСЁ!")
        st.code("\n".join(lines), language="text")
        st.markdown(
            f"""
            <div style='border:1px solid #888;background:#e7e7e7;padding:15px;width:730px;border-radius:6px;'>
              <div style='background:#fff;padding:10px;font-family:Courier New, monospace;'>
                <pre style='margin:0;font-weight:bold;line-height:1.2em;'>
{'\n'.join(lines)}
                </pre>
              </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Ошибка: {e}")
