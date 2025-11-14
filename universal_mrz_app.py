# coding: utf-8
import streamlit as st

st.set_page_config(page_title="Универсальный MRZ генератор", layout="centered")

# === Контрольная цифра (7‑3‑1) ===
def mrz_check_digit(data: str) -> str:
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            "<": 0}
    weights = [7, 3, 1]
    return str(sum(vals.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data)) % 10)

# === Преобразование даты ===
def convert_date(d: str) -> str:
    return d[4:6] + d[2:4] + d[0:2] if len(d) == 6 else d

# === Генерация TD3 (паспорт) ===
def mrz_check_digit(data: str) -> str:
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            '<': 0}
    weights = [7, 3, 1]
    return str(sum(vals.get(ch, 0) * weights[i % 3]
                   for i, ch in enumerate(data)) % 10)


def convert_date(d: str) -> str:
    return d[4:6] + d[2:4] + d[0:2]


def generate_mrz_td3(doc_type, country, nationality,
                     lastname, firstname, number,
                     birth, expiry, sex, optional):

    lastname  = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    number    = number.upper()
    country   = country.upper()
    nationality = nationality.upper()
    sex = sex.upper()
    optional = optional.upper().replace(" ", "<")
    birth, expiry = convert_date(birth), convert_date(expiry)

    # индивидуальные контрольные
    num_cd   = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd   = mrz_check_digit(expiry)

    # первая строка
    line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]

    # части второй строки
    part1 = f"{number}{num_cd}"       # номер + cd1
    part2 = nationality               # гражданство
    part3 = f"{birth}{birth_cd}"      # дата рожд + cd2
    part4 = sex
    part5 = f"{expiry}{exp_cd}"       # срок + cd3
    part6 = optional.ljust(14, "<")[:14]

    # тело строки без заключительных контрольных цифр
    body = part1 + part2 + part3 + part4 + part5 + part6

    # правильная формула для 43-й позиции
    field43 = number + num_cd + birth + birth_cd + expiry + exp_cd + part6
    cd43 = mrz_check_digit(field43)

    # контроль всей строки (44-я позиция)
    cd44 = mrz_check_digit(body + cd43)

    line2 = (body + cd43 + cd44)[:44]
    return [line1, line2]


# Проверка
if __name__ == "__main__":
    mrz = generate_mrz_td3(
        "P", "USA", "USA",
        "HULTON", "DAVID NAKAMURA",
        "A09913982",
        "190383", "180133", "M", "534397504<2872"
    )
    for l in mrz:
        print(l)
    print("длина:", len(mrz[1]), "| 43:", mrz[1][42], "| 44:", mrz[1][43])

# === TD1 для ID‑карт ===
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

# Очистка полей
def clear_fields():
    for k in ["doc_type","country","nationality","lastname","firstname",
              "number","birth","expiry","sex","extra"]:
        st.session_state[k] = ""

# Интерфейс
st.title("🌍 Универсальный MRZ‑генератор (ICAO DOC 9303)")

format_type = st.selectbox("Формат документа", ["TD3 (Паспорт 2×44)", "TD1 (ID‑карта 3×30)"])
doc_type    = st.text_input("Тип", "P", key="doc_type")
country     = st.text_input("Страна (3 буквы)", "USA", key="country")
nationality = st.text_input("Гражданство (3 буквы)", "USA", key="nationality")
lastname    = st.text_input("Фамилия", "HULTON", key="lastname")
firstname   = st.text_input("Имя", "DAVID NAKAMURA", key="firstname")
number      = st.text_input("Номер", "A09913982", key="number")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383", key="birth")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133", key="expiry")
sex         = st.selectbox("Пол", ["M","F","<"], index=0, key="sex")
extra       = st.text_input("Extra Info (до 14 символов)", "534397504<2872", key="extra")

col1, col2 = st.columns(2)
with col1:
    gen = st.button("📄 Сгенерировать MRZ")
with col2:
    clr = st.button("🧹 Очистить", on_click=clear_fields)

# Логика
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

        st.success("✅ !!!!!!")
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
