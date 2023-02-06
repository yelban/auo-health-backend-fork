def mask_credential_name(s: str):
    wildcard = "*"
    if len(s) == 1:
        return s
    elif len(s) == 2:
        return f"{s[0]}{wildcard}"
    elif len(s) == 3:
        return f"{s[0]}{wildcard*(len(s)-2)}{s[-1]}"
    else:
        return f"{s[0]}{wildcard*(len(s)-3)}{s[-2:]}"


def mask_crediential_sid(s: str):
    wildcard = "*"
    return f"{s[0:4]}{wildcard * (len(s) - 6)}{s[-2:]}"


def safe_divide(a, b):
    if b == 0:
        return 0
    return a / b


def get_filters(f):
    return dict([(k, v) for k, v in f.items() if v is not None and v != []])
