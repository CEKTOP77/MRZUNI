# coding: utf-8
import streamlit as st

st.set_page_config(page_title="MRZ генератор (игнор символов после <)", layout="centered")

# ---------- Контрольная цифра ----------
def mrz_check_digit(data: str) -> str:
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            '<': 0}
    weights = [7, 3, 1]

    # игнорируем всё, что идёт после первого символа "<"
    if "<" in data:
        data = data.split("<", 1)[0]

    total = sum(vals.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data))
    return str(total % 10)

# ---------- Преобразование даты ----------
def convert_date(d: str) -> str:
    return d[4:6] + d[2:4] + d[0:2] if len(d) == 6 else d

# ---------- Генерация MRZ TD3 ----------
def generate_td3(doc_type, country, nationality,
                 lastname, firstname, number,
                 birth, expiry, sex, extra):
    lastname  = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    number    = number.upper()
    country   = country.upper()
    nationality = nationality.upper()
    sex = sex.upper()
    extra = extra.upper().replace(" ", "<")
    birth, expiry = convert_date(birth), convert_date(expiry)

    # контрольные цифры с новым правилом (игнор после <)
    num_cd   = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd   = mrz_check_digit(expiry)

    line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]

    part1 = f"{number}{num_cd}"
    part2 = nationality
    part3 = f"{birth}{birth_cd}"
    part4 = sex
    part5 = f"{expiry}{exp_cd}"
    part6 = extra.ljust(14, "<")[:14]

    body = part1 + part2 + part3 + part4 + part5 + part6

    # контрольная 43 и 44, но после символа '<' игнорируем
    data_for_cd = body.split("<", 1)[0]
    cd43 = mrz_check_digit(data_for_cd)
    cd44 = mrz_check_digit(data_for_cd + cd43)

    line2 = (body + cd43 + cd44)[:44]
    return [line1, line2]

# ---------- Очистка ----------
def clear_fields():
    for key in ["doc_type","country","nationality","lastname","firstname",
                "number","birth","expiry","sex","extra"]:
        st.session_state[key] = ""

# ---------- Интерфейс ----------
st.title("🌍 MRZ генератор (игнор символов после <)")

doc_type    = st.text_input("Тип документа", "P", key="doc_type")
country     = st.text_input("Код страны (3 буквы)", "USA", key="country")
nationality = st.text_input("Гражданство (3 буквы)", "USA", key="nationality")
lastname    = st.text_input("Фамилия", "HULTON", key="lastname")
firstname   = st.text_input("Имя", "DAVID NAKAMURA", key="firstname")
number      = st.text_input("Номер документа", "A09913982", key="number")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383", key="birth")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133", key="expiry")
sex         = st.selectbox("Пол", ["M","F","<"], index=0, key="sex")
extra       = st.text_input("Доп. данные (до 14 символов)", "534397504<2872", key="extra")

col1, col2 = st.columns(2)
with col1:
    gen = st.button("📄 Сгенерировать MRZ")
with col2:
    clr = st.button("🧹 Очистить", on_click=clear_fields)

# ---------- Вывод ----------
if gen:
    try:
        lines = generate_td3(doc_type, country, nationality,
                             lastname, firstname, number,
                             birth, expiry, sex, extra)
        st.success("✅ MRZ сге!!!рован")
        st.code("\n".join(lines), language="text")
        st.markdown(
            f"""
            <div style='border:1px solid #999;background:#eee;padding:15px;width:740px;border-radius:6px;'>
              <div style='background:#fff;padding:10px;font-family:Courier New, monospace;'>
                <pre style='margin:0;font-weight:bold;line-height:1.2em;'>\n{'\n'.join(lines)}\n</pre>
              </div>
            </div>
            """,
            unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Ошибка: {e}")
