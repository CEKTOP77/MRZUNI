# coding: utf-8

def mrz_check_digit(data: str) -> str:
    """Вычисление контрольной цифры (вес 7‑3‑1)"""
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            '<': 0}
    weights = [7, 3, 1]
    return str(sum(vals.get(ch, 0) * weights[i % 3]
                   for i, ch in enumerate(data)) % 10)


def convert_date(d: str) -> str:
    """Преобразовать ДДММГГ → ГГММДД"""
    return d[4:6] + d[2:4] + d[0:2] if len(d) == 6 else d


def generate_mrz_td3(doc_type, country, nationality,
                     lastname, firstname, number,
                     birth, expiry, sex, extra):
    """Формирование MRZ кода TD3 (2×44)"""

    # нормализация
    lastname  = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    number    = number.upper()
    country   = country.upper()
    nationality = nationality.upper()
    sex = sex.upper()
    extra = extra.upper().replace(" ", "<")
    birth, expiry = convert_date(birth), convert_date(expiry)

    # контрольные цифры отдельных полей
    num_cd   = mrz_check_digit(number)
    birth_cd = mrz_check_digit(birth)
    exp_cd   = mrz_check_digit(expiry)

    # первая строка (44 символа)
    line1 = f"{doc_type}<{country}{lastname}<<{firstname}"
    line1 = line1[:44].ljust(44, "<")

    # части второй строки
    part_number = f"{number}{num_cd}"
    part_nat    = nationality
    part_birth  = f"{birth}{birth_cd}"
    part_sex    = sex
    part_expiry = f"{expiry}{exp_cd}"
    part_opt    = extra.ljust(14, "<")[:14]

    # тело второй строки без заключительных CD
    body = part_number + part_nat + part_birth + part_sex + part_expiry + part_opt

    # 43‑я контрольная цифра (по стандарту ICAO DOC 9303)
    field43 = number + num_cd + birth + birth_cd + expiry + exp_cd + part_opt
    cd43 = mrz_check_digit(field43)

    # 44‑я контрольная цифра для всей строки
    cd44 = mrz_check_digit(body + cd43)

    # финальная строка
    line2 = (body + cd43 + cd44)[:44]
    return [line1, line2]


# === Проверка ===
if __name__ == "__main__":
    mrz = generate_mrz_td3(
        "P", "USA", "USA",
        "HULTON", "DAVID NAKAMURA",
        "A09913982",
        "190383",     # Дата рождения (ДДММГГ)
        "180133",     # Дата окончания (ДДММГГ)
        "M",
        "534397504<2872"   # Extra Info
    )

    print("\n".join(mrz))
    print("Длина второй строки:", len(mrz[1]))
    print("43‑й:", mrz[1][42], "44‑й:", mrz[1][43])
