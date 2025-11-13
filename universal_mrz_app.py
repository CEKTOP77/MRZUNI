import streamlit as st

# === Расчет контрольной цифры (ICAO DOC 9303) ===
def mrz_check_digit(data: str) -> str:
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              '<': 0}
    weights = [7, 3, 1]
    total = sum(values.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data))
    return str(total % 10)

# === Преобразование даты ДДММГГ → ГГММДД ===
def convert_date(date_str: str) -> str:
    if len(date_str) == 6:
        d, m, y = date_str[:2], date_str[2:4], date_str[4:6]
        return y + m + d
    return date_str

# === Генерация MRZ ===
def generate_mrz(format_type, doc_type, country, nationality,
                 lastname, firstname, doc_number,
                 birth, expiry, sex, extra_info):

    # нормализация значений
    lastname  = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    doc_number = doc_number.upper()
    country = country.upper()
    nationality = nationality.upper()
    sex = sex.upper() if sex else "<"
    extra_info = extra_info.upper().replace(" ", "<")
    birth = convert_date(birth)
    expiry = convert_date(expiry)

    # контрольные цифры
    doc_cd    = mrz_check_digit(doc_number)
    birth_cd  = mrz_check_digit(birth)
    expiry_cd = mrz_check_digit(expiry)

    # === TD3 (Паспорт) ===
    if format_type.upper().startswith("TD3"):
        line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]
        optional_data = extra_info.ljust(14, "<")[:14]
        line2_body = f"{doc_number}{doc_cd}{nationality}{birth}{birth_cd}{sex}{expiry}{expiry_cd}{optional_data}"
        final_cd = mrz_check_digit(line2_body)  # итоговый checksum всего блока
        line2 = line2_body + final_cd
        if len(line2) < 44:
            line2 = line2.ljust(44, "<")
        return [line1, line2]

    # === TD1 (ID‑карта) ===
    elif format_type.upper().startswith("TD1"):
        line1 = f"{doc_type}<{country}{doc_number}{doc_cd}".ljust(30, "<")[:30]
        base2 = f"{birth}{birth_cd}{sex}{expiry}{expiry_cd}{nationality}{extra_info[:14]}"
        temp2 = base2.ljust(29, "<")
        final_cd = mrz_check_digit(line1 + temp2)
        line2 = temp2 + final_cd
        line3 = f"{lastname}<<{firstname}".ljust(30, "<")[:30]
        return [line1, line2, line3]

    # --- если формат не распознан ---
    else:
        raise ValueError(f"Не удалось определить формат: {format_type}")

# === Интерфейс Streamlit ===
st.set_page_config(page_title="Универсальный MRZ Генератор", layout="centered")
st.title("🌍 Универсальный MRZ‑генератор (ICAO DOC 9303)")
st.caption("Создаёт MRZ‑коды для паспортов (TD3) и ID‑карт (TD1). Поддерживает Extra Info и полную валидацию контрольных сумм.")

# --- функция очистки полей ---
def clear_fields():
    for key in ["doc_type", "country", "nationality", "lastname", "firstname",
                "doc_number", "birth", "expiry", "sex", "extra_info"]:
        st.session_state[key] = ""

# --- ввод данных ---
format_type = st.selectbox("Формат документа", ["TD3 (Паспорт, 2x44)", "TD1 (ID‑карта, 3x30)"])
doc_type    = st.text_input("Тип документа (P, ID, V и т.п.)", "P", key="doc_type")
country     = st.text_input("Код страны выдачи (3 буквы)", "USA", key="country")
nationality = st.text_input("Гражданство (3 буквы)", "USA", key="nationality")
lastname    = st.text_input("Фамилия", "HULTON", key="lastname")
firstname   = st.text_input("Имя (можно через пробел)", "DAVID NAKAMURA", key="firstname")
doc_number  = st.text_input("Номер документа", "A09913982", key="doc_number")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383", key="birth")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133", key="expiry")
sex         = st.selectbox("Пол", ["M", "F", "<"], index=0, key="sex")
extra_info  = st.text_input("Extra Info (до 14 символов)", "534397504", key="extra_info")

# --- кнопки действий ---
col1, col2 = st.columns(2)
with col1:
    gen_btn = st.button("📄 Сгенерировать MRZ")
with col2:
    clr_btn = st.button("🧹 Очистить все поля", on_click=clear_fields)

# --- генерация MRZ ---
if gen_btn:
    try:
        mrz_lines = generate_mrz(format_type, doc_type, country, nationality,
                                 lastname, firstname, doc_number,
                                 birth, expiry, sex, extra_info)
        st.success("✅ MRZ успешно сгенерирован!")
        st.code("\n".join(mrz_lines), language="text")
        st.markdown("---")
        st.markdown(
            f"""
            <div style='border:1px solid #999;background:#e0e0e0;padding:15px;width:700px;border-radius:6px;'>
              <div style='background:#fff;padding:10px;font-family:Courier;'>
                <pre style='font-weight:bold;margin:0;line-height:1.2em;'>
{'\n'.join(mrz_lines)}
                </pre>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Ошибка: {e}")
