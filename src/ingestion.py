import csv 
import calendar
import math
from pathlib import Path

def get_valid_days(month,year=2022):
    month = int(month)

    if month<1 or month >12:
        raise ValueError("Month not Valid")

    
    days = calendar.monthrange(year,month)[1] #gives the number of days in that month.
    return days

if __name__ == "__main__":              #Only runs when executed directly not when imported
    print("February",get_valid_days(2))
    print("September",get_valid_days(9))


def validate_row(row):
    errors = []
    clean_row = row.copy()

    try:
        month = int(row["month"])
        valid_days = get_valid_days(month)

    except (ValueError, TypeError, KeyError):
        return clean_row, ["Invalid month value"]

    for column in row:

        if not column.endswith(("st", "nd", "rd", "th")):
            continue

        day_text = column[:-2]

        if not day_text.isdigit():
            continue

        day = int(day_text)

        if day > valid_days:
            clean_row[column] = ""
            errors.append(column + " is not a valid day")
            continue

        try:
            rainfall = float(row[column])

            if not math.isfinite(rainfall) or rainfall < 0:
                clean_row[column] = ""
                errors.append(column + " has invalid rainfall")

        except (ValueError, TypeError):
            clean_row[column] = ""
            errors.append(column + " has a non-numeric value")

    return clean_row, errors




def read_and_validate(file_path):
    clean_records = []
    audit_entries = []

    try:
        with open(file_path, "r", newline="", encoding="utf-8-sig") as file:

            reader = csv.DictReader(file, delimiter=";")

            for row_number, row in enumerate(reader, start=2):

                if None in row or any(value is None for value in row.values()):
                    audit_entries.append(
                        f"Row {row_number}: Corrupted CSV record"
                    )
                    continue

                cleaned_row, errors = validate_row(row)

                clean_records.append(cleaned_row)

                for error in errors:
                    audit_entries.append(
                        f"Row {row_number}: {error}"
                    )

    except FileNotFoundError:
        raise FileNotFoundError("The input CSV file was not found.")

    except PermissionError:
        raise PermissionError("Unable to access the input CSV file.")

    return clean_records, audit_entries



if __name__ == "__main__":

    project_folder = Path(__file__).resolve().parent.parent

    input_file = project_folder / "data" / "raw" / "Indian Rainfall Dataset District-wise Daily Measurements.csv"

    records, errors = read_and_validate(input_file)

    print("Total clean records:", len(records))
    print("Total validation errors:", len(errors))

    if records:
        print("\nFirst cleaned record:")
        print(records[0])

    if errors:
        print("\nFirst few errors:")
        for error in errors[:5]:
            print(error)
