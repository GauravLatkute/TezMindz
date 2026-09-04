"""
Indian Numbering System Utility for Tezz-Mindz Game Engine.
Supports formatting, words conversion, expanded forms, and place-value calculations.
"""

ONES_WORDS = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen"
]

TENS_WORDS = [
    "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"
]


def format_indian_number(number: int) -> str:
    """
    Format an integer into the standard Indian numbering format with commas.
    Example: 375420 -> "3,75,420"
             1000000 -> "10,00,000"
             100001 -> "1,00,001"
             500 -> "500"
    """
    if number is None:
        return ""
    try:
        num_str = str(int(number))
    except (ValueError, TypeError):
        return str(number)

    if len(num_str) <= 3:
        return num_str

    # Last 3 digits (Hundreds, Tens, Ones)
    last_three = num_str[-3:]
    remaining = num_str[:-3]

    # Every 2 digits from the right for Thousands, Lakhs, Crores
    parts = []
    while len(remaining) > 2:
        parts.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        parts.insert(0, remaining)

    return ",".join(parts) + "," + last_three


def _two_digits_to_words(n: int) -> str:
    if n < 20:
        return ONES_WORDS[n]
    tens, ones = divmod(n, 10)
    return (TENS_WORDS[tens] + ("-" + ONES_WORDS[ones] if ones else "")).strip()


def _three_digits_to_words(n: int) -> str:
    words = []
    hundreds, rest = divmod(n, 100)
    if hundreds:
        words.append(f"{ONES_WORDS[hundreds]} Hundred")
    if rest:
        words.append(_two_digits_to_words(rest))
    return " ".join(words).strip()


def number_to_indian_words(num: int) -> str:
    """
    Converts an integer to full Indian English words.
    Supports up to Crores (up to 99,99,99,999).
    Examples:
        250000  -> "Two Lakh Fifty Thousand"
        375420  -> "Three Lakh Seventy-Five Thousand Four Hundred Twenty"
        835000  -> "Eight Lakh Thirty-Five Thousand"
        1000000 -> "Ten Lakh"
        1005010 -> "Ten Lakh Five Thousand Ten"
        101001  -> "One Lakh One Thousand One"
    """
    if num == 0:
        return "Zero"

    num = abs(int(num))
    crores, remainder = divmod(num, 10000000)
    lakhs, remainder = divmod(remainder, 100000)
    thousands, remainder = divmod(remainder, 1000)
    hundreds_part = remainder

    parts = []
    if crores:
        parts.append(f"{_two_digits_to_words(crores)} Crore")
    if lakhs:
        parts.append(f"{_two_digits_to_words(lakhs)} Lakh")
    if thousands:
        parts.append(f"{_two_digits_to_words(thousands)} Thousand")
    if hundreds_part:
        parts.append(_three_digits_to_words(hundreds_part))

    return " ".join(parts).strip()


def get_place_value(number: int, digit_pos_from_right: int) -> dict:
    """
    Returns the place name, place value, and face value of a digit position (0-indexed from right).
    0 = Ones, 1 = Tens, 2 = Hundreds, 3 = Thousands, 4 = Ten Thousands, 5 = Lakhs, 6 = Ten Lakhs
    """
    place_names = [
        ("Ones", 1),
        ("Tens", 10),
        ("Hundreds", 100),
        ("Thousands", 1000),
        ("Ten Thousands", 10000),
        ("Lakhs", 100000),
        ("Ten Lakhs", 1000000),
        ("Crores", 10000000),
        ("Ten Crores", 100000000),
    ]
    num_str = str(number)[::-1]
    if digit_pos_from_right >= len(num_str):
        return {}

    digit = int(num_str[digit_pos_from_right])
    name, multiplier = place_names[digit_pos_from_right]
    value = digit * multiplier

    return {
        "digit": digit,
        "place_name": name,
        "multiplier": multiplier,
        "place_value": value,
        "formatted_place_value": format_indian_number(value)
    }


def expanded_form_indian(number: int) -> list:
    """
    Returns the expanded form list of formatted strings.
    Example: 325000 -> ["3,00,000", "20,000", "5,000"]
    """
    num_str = str(number)[::-1]
    place_values = []
    for i, d in enumerate(num_str):
        digit = int(d)
        if digit > 0:
            val = digit * (10 ** i)
            place_values.insert(0, format_indian_number(val))
    return place_values
