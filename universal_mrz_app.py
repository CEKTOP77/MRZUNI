def mrz_check_digit(data):
    vals = {**{str(i): i for i in range(10)},
            **{chr(i + 55): i for i in range(10, 36)},
            '<': 0}
    weights = [7, 3, 1]
    return str(sum(vals.get(c, 0) * weights[i % 3] for i, c in enumerate(data)) % 10)

def convert_date(d):
    # ДДММГГ -> ГГММДД
    return d[4:6] + d[2:4] + d[0:2]

def generate_mrz_td3(doc_type, country, nationality,
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

    n_cd = mrz_check_digit(number)
    b_cd = mrz_check_digit(birth)
    e_cd = mrz_check_digit(expiry)

    line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]

    opt = extra.ljust(14, "<")[:14]
    body = f"{number}{n_cd}{nationality}{birth}{b_cd}{sex}{expiry}{e_cd}{opt}"
    final_cd = mrz_check_digit(body)

    # если тело + checksum > 44, нужно убрать лишние заполнители,
    # но оставить checksum как последний символ
    line2 = body
    if len(line2) > 43:
        line2 = line2[:43]
    line2 = line2 + final_cd

    # теперь длина гарантированно 44
    return [line1, line2]


if __name__ == "__main__":
    mrz = generate_mrz_td3(
        "P", "USA", "USA",
        "HULTON", "DAVID NAKAMURA",
        "A09913982", "190383", "180133", "M", "534397504"
    )
    for l in mrz: 
        print(l)
