"""functions.py - functions for the Malaysian Income Tax Calculator (YA 2026)."""

import os
import pandas as pd

# CSV files are saved in the same folder as this program
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.csv")
TAX_FILE = os.path.join(BASE_DIR, "tax_records.csv")

USER_HEADERS = ["User ID", "IC Number"]
TAX_HEADERS = ["User ID", "Test Case ID", "Year of Assessment", "Annual Income",
               "Total Tax Relief", "Chargeable Income", "Tax Before Rebate",
               "Tax Rebate", "Final Tax Payable"]

# YA 2026 tax rates: (upper limit of the band, tax rate)
BRACKETS = [(5000, 0.00), (20000, 0.01), (35000, 0.03), (50000, 0.06),
            (70000, 0.11), (100000, 0.19), (400000, 0.25), (600000, 0.26),
            (2000000, 0.28), (float("inf"), 0.30)]

def ensure_storage_files():
    """Create users.csv and tax_records.csv with headers if they are missing."""
    try:
        if not os.path.exists(USERS_FILE):
            pd.DataFrame(columns=USER_HEADERS).to_csv(USERS_FILE, index=False)
        if not os.path.exists(TAX_FILE):
            pd.DataFrame(columns=TAX_HEADERS).to_csv(TAX_FILE, index=False)
    except OSError:
        print("Warning: unable to create the CSV files.")

def read_csv_file(filename, headers):
    """Read a CSV file as text. Return an empty table if the file is missing or unreadable."""
    try:
        return pd.read_csv(filename, dtype=str).fillna("")
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=headers)

def register_user(user_id, ic_number):
    """Register a new user. Return (True/False, message)."""
    # Validate: User ID not empty, IC must be exactly 12 digits
    if user_id == "" or not ic_number.isascii() or not ic_number.isdigit() \
            or len(ic_number) != 12:
        return False, "Invalid User ID or IC number (must be 12 digits)."

    users = read_csv_file(USERS_FILE, USER_HEADERS)
    if user_id in users["User ID"].tolist():
        return False, "User ID already exists."

    # Dictionary -> DataFrame -> add to old users -> save to CSV
    new_user = {"User ID": user_id, "IC Number": ic_number}
    users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
    try:
        users.to_csv(USERS_FILE, index=False)
    except OSError:
        return False, "Unable to save. Close the CSV file if it is open."
    return True, "Registration successful. Password is the last 4 digits of your IC."

def login_user(user_id, password):
    """Return True if the User ID exists and the password is the last 4 digits of its IC."""
    users = read_csv_file(USERS_FILE, USER_HEADERS)
    matched = users[users["User ID"] == user_id]
    if matched.empty:
        return False
    # Password = last 4 digits of the stored IC number
    return password == matched.iloc[0]["IC Number"][-4:]

def calculate_tax(annual_income, total_relief):
    """Return chargeable income, tax before rebate, rebate and final tax as a dictionary."""
    # Chargeable income cannot be negative
    chargeable = max(0.0, float(annual_income) - float(total_relief))

    # Progressive tax: each rate only applies to the income inside its band
    tax = 0.0
    lower = 0.0
    for upper, rate in BRACKETS:
        if chargeable > lower:
            tax += (min(chargeable, upper) - lower) * rate
        lower = upper

    # RM400 rebate if chargeable income is RM35,000 or below
    rebate = 400 if chargeable <= 35000 else 0
    # Final tax cannot be negative
    final_tax = max(0.0, tax - rebate)

    return {"Chargeable Income": round(chargeable, 2),
            "Tax Before Rebate": round(tax, 2),
            "Tax Rebate": float(rebate),
            "Final Tax": round(final_tax, 2)}

def create_record(user_id, annual_income, total_relief, test_id=""):
    """Put the values in a list, then turn the list into a dictionary."""
    result = calculate_tax(annual_income, total_relief)
    # Step 1: list of values (same order as TAX_HEADERS)
    values = [user_id, test_id, 2026, float(annual_income), float(total_relief),
              result["Chargeable Income"], result["Tax Before Rebate"],
              result["Tax Rebate"], result["Final Tax"]]
    # Step 2: list -> dictionary (column names are the keys)
    return dict(zip(TAX_HEADERS, values))

def save_record(record):
    """Add one record (dictionary) to tax_records.csv. Old records are kept."""
    records = read_csv_file(TAX_FILE, TAX_HEADERS)
    # Step 3: dictionary -> DataFrame -> add to old records -> save to CSV
    records = pd.concat([records, pd.DataFrame([record])], ignore_index=True)
    try:
        records.to_csv(TAX_FILE, index=False)
    except OSError:
        return False
    return True

def get_records(user_id, test_cases_only=False):
    """Return the saved records of a user as a DataFrame (money shown as RM).
    A blank Test Case ID means a normal calculation. T01-T05 are the test cases.
    """
    records = read_csv_file(TAX_FILE, TAX_HEADERS)
    records = records[records["User ID"] == user_id].copy()
    if test_cases_only:
        records = records[records["Test Case ID"] != ""].copy()
    for column in TAX_HEADERS[3:]:
        records[column] = records[column].apply(lambda v: f"RM {float(v):,.2f}")
    return records