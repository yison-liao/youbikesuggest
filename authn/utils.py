import re


def password_check(password):
    pattern = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")  # 至少包含一個字母和一個數字
    if bool(pattern.match(password)):
        if len(password) >= 8:
            return True
    return False
