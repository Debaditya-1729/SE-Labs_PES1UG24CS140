"""Input-validated library fine processor for Lab 7.

Invalid inputs raise ValueError; see README.md for the input contract.
"""
import string
import sys

MAX_INPUT_LENGTH = 4096
MAX_DIGITS = 9
ASCII_LETTERS = frozenset(string.ascii_letters)
ASCII_DIGITS = frozenset(string.digits)


def _validated_text(value, field):
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    if len(value) > MAX_INPUT_LENGTH:
        raise ValueError(f"{field} is too long")
    return value.strip()


def _parse_nonnegative_integer(token, field):
    if (not token or len(token) > MAX_DIGITS
            or any(char not in ASCII_DIGITS for char in token)):
        raise ValueError(f"{field} must be 1 to 9 ASCII digits")
    return int(token)


def parse_member_id(member_id):
    text = _validated_text(member_id, "member ID")
    parts = text.split("-")
    if len(parts) != 2:
        raise ValueError("member ID must have the form TYPE-NUMBER")
    member_type, number = parts
    if not member_type or any(char not in ASCII_LETTERS for char in member_type):
        raise ValueError("member type must contain ASCII letters only")
    return member_type.upper(), _parse_nonnegative_integer(number, "member number")


def total_fine(days_csv):
    text = _validated_text(days_csv, "days CSV")
    tokens = text.split(",")
    days = [_parse_nonnegative_integer(token.strip(), "days kept")
            for token in tokens]
    return sum(max(0, day - 14) * 2 for day in days)


def shelf_code(title):
    text = _validated_text(title, "title")
    words = text.split()
    if len(words) < 2:
        raise ValueError("title must contain at least two words")
    return (words[0][0] + words[1][0]).upper()


def main():
    try:
        print("==== Running parse_member_id ====")
        user_input = input("Enter a member ID (e.g. STU-1023): ")
        print("Member Type and Number:", parse_member_id(user_input))

        print("\n==== Running total_fine ====")
        user_input = input("Enter days kept for each book as CSV (e.g. 10,20,30): ")
        print("Total Fine:", total_fine(user_input))

        print("\n==== Running shelf_code ====")
        user_input = input("Enter a book title with at least two words: ")
        print("Shelf Code:", shelf_code(user_input))
    except ValueError as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 1
    except EOFError:
        print("Input ended before all fields were provided.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
