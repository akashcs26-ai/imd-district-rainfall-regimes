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
        with open(file_path, "r", newline="", encoding="utf-8") as file:

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

def cleaned_data(records, audit_entries,output_folder):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    cleaned_file_path = output_folder / "cleaned_data.csv"
    audit_file_path = output_folder / "audit_log.txt"

    with open(cleaned_file_path, "w", newline="", encoding="utf-8") as cleaned_file:
        if records:
            fieldnames = records[0].keys()
            writer = csv.DictWriter(cleaned_file, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(records)

    with open(audit_file_path,"w",encoding="utf-8") as audit_file:
        for entry in audit_entries:
            audit_file.write(entry + "\n")
            audit_file.write("\nSUMMARY\n")
            audit_file.write("-" * 40 + "\n")
            audit_file.write(f"Total records processed: {len(records)}\n")
            audit_file.write(f"Total validation errors: {len(audit_entries)}\n")
    
    return cleaned_file_path, audit_file_path

"""if __name__ == "__main__":

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
            print(error)"""

if __name__ == "__main__":

    
    
    project_folder = Path(__file__).resolve().parent.parent

    input_file = project_folder / "data" / "raw" / "Indian Rainfall Dataset District-wise Daily Measurements.csv"

    output_folder = project_folder / "data" / "processed"

    records, errors = read_and_validate(input_file)

    clean_file, audit_file = cleaned_data(
        records, errors, output_folder
    )

    print("Data cleaning completed!")
    print("Total records:", len(records))
    print("Total validation errors:", len(errors))

    print("\nFiles generated:")
    print(clean_file)
    print(audit_file)
    invalid_days = sum("not a valid day" in error for error in errors)
    
    invalid_rainfall = sum("invalid rainfall" in error for error in errors)
    
    non_numeric = sum("non-numeric" in error for error in errors)
    
    corrupted = sum("Corrupted CSV" in error for error in errors)
    
    invalid_month = sum("Invalid month" in error for error in errors)
    
    print("\nVALIDATION SUMMARY")
    print("--------------------------")
    print("Invalid calendar days:", invalid_days)
    print("Invalid rainfall values:", invalid_rainfall)
    print("Non-numeric values:", non_numeric)
    print("Corrupted records:", corrupted)
    print("Invalid month values:", invalid_month)

    with open(clean_file, "r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file,delimiter=";")
        exported_records = list(reader)

print("\nEXPORT VERIFICATION")
print("--------------------------")
print("Records exported:", len(exported_records))
print("Columns exported:", len(exported_records[0]))

if len(exported_records) == len(records):
    print("Record count verification: Passed")
else:
    print("Record count verification: Failed")
    february_records = [
    row for row in exported_records
    if row["month"] == "2"
]

    if february_records:
        print("\nFEBRUARY VALIDATION")
        print("--------------------------")

        print("29th day:", repr(february_records[0]["29th"]))
        print("30th day:", repr(february_records[0]["30th"]))
        print("31st day:", repr(february_records[0]["31st"]))