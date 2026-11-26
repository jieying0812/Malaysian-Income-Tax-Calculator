"""main.py - Malaysian Income Tax Calculator (YA 2026): menus and user interface."""

import math
import pandas as pd
from functions import (ensure_storage_files, register_user, login_user,
                       calculate_tax, create_record, save_record, get_records)

# (test case ID, annual income, total relief, expected final tax)
TEST_CASES = [("T01", 9000, 9000, 0), ("T02", 40000, 9000, 80),
              ("T03", 65000, 14000, 1610), ("T04", 120000, 18000, 9900),
              ("T05", 83000, 12000, 3890)]

def get_number(prompt):
    """Keep asking until the user enters a valid number that is not negative."""
    while True:                                   # repeat until the input is valid
        try:
            value = float(input(prompt).replace(",", ""))   # accept 50,000
            if value >= 0 and math.isfinite(value):
                return value
            print("Please enter a valid non-negative number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def calculate_menu(user_id):
    """Ask for income and relief, show the result in RM and save it."""
    print("--- Calculate Income Tax ---")
    income = get_number("Enter annual income (RM): ")
    relief = get_number("Enter total tax relief (RM): ")

    result = calculate_tax(income, relief)
    print("===== INCOME TAX RESULT (YA 2026) =====")
    for name, value in result.items():
        print(f"{name:<18}: RM {value:,.2f}")

    if save_record(create_record(user_id, income, relief)):
        print("Tax record saved.")
    else:
        print("Unable to save tax record.")

def view_records(user_id):
    """Retrieve and show all saved records of the user (calculations and test cases)."""
    print("--- Saved Tax Records ---")
    records = get_records(user_id)
    if records.empty:
        print("No tax records found.")
    else:
        print(records.to_string(index=False))

def run_test_cases(user_id):
    """Calculate T01-T05, show PASS/FAIL, save each test case once and show the saved records."""
    # Test cases already saved are skipped, so there are no duplicates
    saved = get_records(user_id, test_cases_only=True)["Test Case ID"].tolist()

    print("===== TEST CASES T01-T05 =====")
    for test_id, income, relief, expected in TEST_CASES:
        result = calculate_tax(income, relief)
        status = "PASS" if abs(result["Final Tax"] - expected) < 0.01 else "FAIL"
        print(f"{test_id} | Income: RM {income:,.2f} | Relief: RM {relief:,.2f} | "
              f"Chargeable: RM {result['Chargeable Income']:,.2f} | "
              f"Before Rebate: RM {result['Tax Before Rebate']:,.2f} | "
              f"Rebate: RM {result['Tax Rebate']:,.2f} | "
              f"Final: RM {result['Final Tax']:,.2f} | {status}")
        if test_id in saved:
            print("    -> already saved")
        elif save_record(create_record(user_id, income, relief, test_id)):
            print("    -> saved to tax_records.csv")
        else:
            print("    -> unable to save")

    # Read the test cases back from the CSV file using pandas
    print("===== SAVED TEST CASE RECORDS (from tax_records.csv) =====")
    print(get_records(user_id, test_cases_only=True).to_string(index=False))

def data_demo(user_id):
    """Show the data processing steps: list -> dictionary -> DataFrame (test case T05)."""
    print("--- Data Processing Demo (T05) ---")
    raw_list = ["T05", 83000, 12000]                       # 1. list
    print("1. List       :", raw_list)
    record = create_record(user_id, raw_list[1], raw_list[2], raw_list[0])
    print("2. Dictionary :", record)                       # 2. dictionary
    print("3. DataFrame  :")                               # 3. DataFrame
    print(pd.DataFrame([record]).to_string(index=False))

def user_menu(user_id):
    """Menu shown after a successful login."""
    while True:
        print(f"--- User Menu ({user_id}) ---")
        print("1. Calculate Income Tax")
        print("2. View Saved Tax Records")
        print("3. Run Test Cases (T01-T05)")
        print("4. Data Processing Demo (List -> Dictionary -> DataFrame)")
        print("5. Logout")
        choice = input("Enter choice (1-5): ").strip()
        if choice == "1":
            calculate_menu(user_id)
        elif choice == "2":
            view_records(user_id)
        elif choice == "3":
            run_test_cases(user_id)
        elif choice == "4":
            data_demo(user_id)
        elif choice == "5":
            print("Logged out successfully.")
            break
        else:
            print("Invalid choice. Enter 1 to 5.")

def main():
    """Main menu: register, login or exit."""
    ensure_storage_files()                 # create the CSV files if they are missing
    while True:
        print(" " + "=" * 50)
        print("  MALAYSIAN INCOME TAX CALCULATOR (YA 2026)")
        print("=" * 50)
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            print("--- User Registration ---")
            user_id = input("Enter User ID: ").strip()
            ic_number = input("Enter 12-digit IC number: ").strip()
            success, message = register_user(user_id, ic_number)
            print(message)
        elif choice == "2":
            print("--- User Login ---")
            user_id = input("Enter User ID: ").strip()
            password = input("Enter password: ").strip()
            # Only registered users can open the user menu
            if login_user(user_id, password):
                print(f"Login successful. Welcome, {user_id}.")
                user_menu(user_id)
            else:
                print("Invalid User ID or password.")
        elif choice == "3":
            print("Program ended.")
            break
        else:
            print("Invalid choice. Enter 1 to 3.")

if __name__ == "__main__":
    main()