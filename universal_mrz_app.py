# coding: utf-8
import streamlit as st

st.set_page_config(page_title="Универсальный MRZ генератор", layout="centered")


# === 1. Контрольная цифра ===
def mrz_check_digit(data: str) -> str:
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            "<": 0}
    weights = [7, 3, 1]
    return str(sum(vals.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data)) % 10)


# === 2. Формат даты (ДДММГГ → ГГММДД) ===
def convert_date(date_str: str) -> str:
    return date_str[4:6] + date_str[2:4] + date_str[0:2] if len(date_str) == 6 else date_str


# === 3. Генерация MRZ TD3 (паспорт) ===
def generate_td3(doc_type, country, nationality,
                 lastname, firstname, number,
                 birth, expiry, sex, extra):
    """Формирует две строки MRZ TD3 (2×44)."""

    # ----- нормализация -----
    lastname  = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    number    = number.upper()
    country   = country.upper()
    nationality = nationality.upper()
    sex = sex.upper()
    extra = extra.upper().replace(" ", "<")

    # исправляем: разделитель между несколькими именами всегда "<"
    firstname = firstname.replace("<<", "<")  # если было двойное
    if " " in firstname:
        firstname = firstname.replace(" ", "<")

    birth, expiry = convert_date(birth), convert_date(expiry)

    # ----- индивидуальные контрольные цифры -----
    num_cd   = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd   = mrz_check_digit(expiry)

    # ----- первая строка (44 символа) -----
    line1 = f"{doc_type}<{country}{lastname}<<{firstname}"
    line1 = line1[:44].ljust(44, "<")

    # ----- части второй строки -----
    part_num   = f"{number}{num_cd}"
    part_nat   = nationality
    part_birth = f"{birth}{birth_cd}"
    part_sex   = sex
    part_exp   = f"{expiry}{exp_cd}"
    part_opt   = extra.ljust(14, "<")[:14]

    # тело второй строки без итоговых контрольных цифр
    body = part_num + part_nat + part_birth + part_sex + part_exp + part_opt

    # ----- 43‑я контрольная цифра (номер + даты + optional) -----
    field43 = number + num_cd + birth + birth_cd + expiry + exp_cd + part_opt
    cd43 = mrz_check_digit(field43)

    # ----- 44‑я контрольная цифра (вся строка) -----
    cd44 = mrz_check_digit(body + cd43)

    # итоговая вторая строка (строго 44 символа)
    line2 = (body + cd43 + cd44)[:44]

    return [line1, line2]


# === 4. Генерация TD1 (ID‑карта) ===
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


# === 5. Очистка полей ===
def clear_fields():
    for k in ["doc_type","country","nationality","lastname","firstname",
              "number","birth","expiry","sex","extra"]:
        st.session_state[k] = ""


# === 6. Интерфейс Streamlit ===
st.title("🌍 Универсальный MRZ‑генератор (ICAO DOC 9303)")

format_type = st.selectbox("Формат документа", ["TD3 (Паспорт 2×44)", "TD1 (ID‑карта 3×30)"])
doc_type    = st.text_input("Тип документа", "P", key="doc_type")
country     = st.text_input("Страна (3 буквы)", "USA", key="country")
nationality = st.text_input("Гражданство (3 буквы)", "USA", key="nationality")
lastname    = st.text_input("Фамилия", "HULTON", key="lastname")
firstname   = st.text_input("Имя", "DAVID NAKAMURA", key="firstname")  # оставляем пробел — заменим на "<" выше
number      = st.text_input("Номер документа", "A09913982", key="number")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383", key="birth")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133", key="expiry")
sex         = st.selectbox("Пол", ["M","F","<"], index=0, key="sex")
extra       = st.text_input("Доп. информация (до 14 символов)", "534397504<2872", key="extra")

col1, col2 = st.columns(2)
with col1:
    gen = st.button("📄 Сгенерировать MRZ")
with col2:
    clr = st.button("🧹 Очистить поля", on_click=clear_fields)


# === 7. ЛОГИКА ===
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

        st.success("✅ MRZ 2222!")
        st.code("\n".join(lines), language="text")
        st.markdown(
            f"""
            <div style='border:1px solid #999;background:#ececec;padding:15px;width:740px;border-radius:6px;'>
              <div style='background:#fff;padding:10px;font-family:Courier New, monospace;'>
                <pre style='margin:0;font-weight:bold;line-height:1.2em;'>
{'\n'.join(lines)}
                </pre>
              </div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ошибка: {e}")
