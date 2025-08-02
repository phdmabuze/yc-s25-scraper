import re


def normalize_name(name) -> str:
    return re.sub(r"[^\w]", "", str(name).lower().strip())


def google_search_linkedin_followers_to_number(text: str) -> int | None:
    match = re.search(r"(\d+\.?\d*)\s*([KkMm]?)\+?\s*(followers)?", text, re.IGNORECASE)
    if not match:
        return None

    num, suffix, _ = match.groups()
    try:
        num = float(num)
    except ValueError:
        return None

    # Определяем множитель
    suffix = suffix.upper()
    multiplier = 1
    if suffix == "K":
        multiplier = 1000
    elif suffix == "M":
        multiplier = 1_000_000

    return int(num * multiplier)
