# coding: utf-8
import streamlit as st

# Настройка страницы
st.set_page_config(page_title="MRZ генератор (корректный)", layout="centered")

# ---------- функции генерации ----------
def mrz_check_digit(data: str) -> str:
    """Контрольная цифра по стандарту ICAO DOC 9303 (веса 7‑3‑1)."""
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              "<": 0}
    weights = [7, 3, 1]
    return str(sum(values.get(c, 0) * weights[i % 3] for i, c in enumerate(data)) % 10)


def convert_date(d: str) -> str:
    """ДДММГГ → ГГММДД"""
    return d[4:6] + d[2:4] + d[0:2]


def generate_td3(doc_type, country, nationality,
                 lastname, firstname, number,
                 birth, expiry, sex, optional):
    """Генерация MRZ (паспорт TD3) полностью по образцу."""

    lastname  = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    number    = number.upper()
    country   = country.upper()
    nationality = nationality.upper()
    sex = sex.upper()
    optional = optional.upper().replace(" ", "<")

    birth, expiry = convert_date(birth), convert_date(expiry)

    # контрольные цифры отдельных полей
    num_cd   = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd   = mrz_check_digit(expiry)

    # первая строка (44 символа)
    line1 = f"{doc_type}<{country}{lastname}<<{firstname}"
    line1 = line1[:44].ljust(44, "<")

    # составляющие второй строки
    part_num   = f"{number}{num_cd}"
    part_nat   = nationality
    part_birth = f"{birth}{birth_cd}"
    part_sex   = sex
    part_exp   = f"{expiry}{exp_cd}"
    part_opt   = optional.ljust(14, "<")[:14]

    # тело второй строки (без итоговых контрольных)
    body = part_num + part_nat + part_birth + part_sex + part_exp + part_opt

    # 43‑й контрольный (номер + cd + даты + их cd + optional)
    field43 = number + num_cd + birth + birth_cd + expiry + exp_cd + part_opt
    cd43 = mrz_check_digit(field43)

    # 44‑й контрольный на всю линию
    cd44 = mrz_check_digit(body + cd43)

    line2 = (body + cd43 + cd44)[:44]

    return [line1, line2]


# ---------- интерфейс ----------
st.title("🌍 Генератор MRZ (паспорт TD3)")

doc_type    = st.text_input("Тип документа", "P")
country     = st.text_input("Страна (3 буквы)", "USA")
nationality = st.text_input("Гражданство (3 буквы)", "USA")
lastname    = st.text_input("Фамилия", "HULTON")
firstname   = st.text_input("Имя", "DAVID NAKAMURA")
number      = st.text_input("Номер документа", "A09913982")
birth       = st.text_input("Дата рождения (ДДММГГ)", "190383")
expiry      = st.text_input("Дата окончания (ДДММГГ)", "180133")
sex         = st.selectbox("Пол", ["M","F","<"], index=0)
extra       = st.text_input("Доп. данные (до 14 символов)", "534397504<2872")

if st.button("📄 Сгенерировать MRZ"):
    try:
        lines = generate_td3(doc_type, country, nationality,
                             lastname, firstname, number,
                             birth, expiry, sex, extra)

        st.success("✅  ")
        st.code("\n".join(lines), language="text")

        # форматированный вывод, как на паспорте
        st.markdown(
            f"""
            <div style='border:1px solid #888;background:#eee;
                        padding:15px;width:730px;border-radius:6px;'>
              <div style='background:#fff;padding:10px;
                          font-family:Courier New, monospace;'>
                <pre style='margin:0;font-weight:bold;
                            line-height:1.2em'>{lines[0]}\n{lines[1]}</pre>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error(f"Ошибка: {e}")
