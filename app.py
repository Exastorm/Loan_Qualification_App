# -*- coding: utf-8 -*-

"""Loan Qualifier Application. This is a command line application to match applicants with qualifying loans.
Example: $ python app.py
"""

# import sys # Not using it. See comment on line 31
# import fire # Not using it. See comment on line 179
import os
import csv
import questionary
from colorama import Fore, Back, Style
from pathlib import Path
from qualifier.utils.fileio import load_csv
from qualifier.utils.calculators import calculate_monthly_debt_ratio
from qualifier.utils.calculators import calculate_loan_to_value_ratio
from qualifier.filters.max_loan_size import filter_max_loan_size
from qualifier.filters.credit_score import filter_credit_score
from qualifier.filters.debt_to_income import filter_debt_to_income
from qualifier.filters.loan_to_value import filter_loan_to_value

"""Ask for the file path to the latest banking data and load the CSV file.
Returns the bank data from the data rate sheet CSV file.
"""

def load_bank_data():

    print()
    input_path = questionary.text("Please enter the file path to a .csv rate-sheet:\n").ask()
    input_path = Path(input_path)
    while not input_path.exists(): # I replaced 'sys.exit' with a 'while' loop that runs until a valid path is entered 

        print(f"Sorry, you have entered an incorrect path or filename: '{input_path}' cannot be found...")
        print()
        input_path = questionary.text("Please enter the fifle path to a .csv rate-sheet:\n").ask()
        input_path = Path(input_path)
    
    return load_csv(input_path)

"""Prompt dialog to get the applicant's financial information.
Returns the applicant's financial information.
"""

def get_applicant_info():

    print()
    credit_score = questionary.text("What's your credit score?").ask()
    debt = questionary.text("What's your current amount of monthly debt? $").ask()
    income = questionary.text("What's your total monthly income? $").ask()
    loan_amount = questionary.text("What's your desired loan amount? $").ask()
    home_value = questionary.text("What's your home value? $").ask()

    credit_score = int(credit_score)
    debt = float(debt)
    income = float(income)
    loan_amount = float(loan_amount)
    home_value = float(home_value)

    return credit_score, debt, income, loan_amount, home_value

"""Determine which loans the user qualifies for.

Loan qualification criteria:
    - Credit Score
    - Loan Size
    - Debt to Income ratio (calculated)
    - Loan to Value ratio (calculated)

Args:
    bank_data_ (list): A list of bank data.
    credit_score_ (int): The applicant's current credit score.
    debt_ (float): The applicant's total monthly debt payments.
    income_ (float): The applicant's total monthly income.
    loan_ (float): The total loan amount applied for.
    home_value_ (float): The estimated home value.

Returns:
    A list of the banks willing to underwrite the loan.

"""

def find_qualifying_loans(bank_data_, credit_score_, debt_, income_, loan_, home_value_):
    
    # Calculate the monthly debt ratio
    monthly_debt_ratio = calculate_monthly_debt_ratio(debt_, income_)
    print(Fore.CYAN + f"\n       Your monthly debt to income ratio is {int(monthly_debt_ratio * 100)}%")

    # Calculate loan to value ratio
    loan_to_value_ratio = calculate_loan_to_value_ratio(loan_, home_value_)
    print(Fore.CYAN + f"\n       Your loan to value ratio is {int(loan_to_value_ratio * 100)}%")

    # Run qualification filters
    bank_data_filtered = filter_max_loan_size(loan_, bank_data_)
    bank_data_filtered = filter_credit_score(credit_score_, bank_data_filtered)
    bank_data_filtered = filter_debt_to_income(monthly_debt_ratio, bank_data_filtered)
    bank_data_filtered = filter_loan_to_value(loan_to_value_ratio, bank_data_filtered)

    if len(bank_data_filtered) == 0: # I diversified the replies based on qualification results
        print(Back.RED)
        print(Back.RED + Fore.LIGHTWHITE_EX + "\n       Sorry, no qualifying loans are available at this time.")

    elif len(bank_data_filtered) == 1:
        print(Back.CYAN)
        print(Back.CYAN + Fore.YELLOW + Style.BRIGHT + "\n       There is 1 qualifying loan available.")
    
    else:
        print(Back.CYAN)
        print(Back.CYAN + Fore.YELLOW + Style.BRIGHT + f"\n       There are {len(bank_data_filtered)} qualifying loans available.")

    return bank_data_filtered

"""Save the qualifying loans to a CSV file.
Args: qualifying_loans_ (list of lists): The qualifying bank loans.
"""
# @TODO: Complete the usability dialog for saving the CSV Files
# First I'm adding an additional function to optionally display results

def view_qualifying_loans(qualifying_loans_): 
    print()
    view = questionary.text("Would you like to view your qualifying loan information?").ask()
    print()
    x = 1
    while x == 1: # A loop to force a response with 'y', 'n', 'yes' or 'no'
        if str.lower(view) in ["yes", "y"]:
            for each_loan in qualifying_loans_:
                print(*each_loan, end="\n") # Unpacking and printing the list of lists and adding a line break
            x = 0
        elif str.lower(view) in ["no", "n"]:
            x = 0
        else:
            view = questionary.text("Please respond 'yes' or 'no'...").ask()
            print()
    
def save_qualifying_loans(qualifying_loans_):
    print()
    save = questionary.text("Would you like to download your qualifying loan information?").ask()
    print()
    x = 1
    while x == 1: # A loop to force a response with 'y', 'n', 'yes' or 'no'
        if str.lower(save) in ["yes", "y"]:
            output_path = Path("qualifying_loans.csv")
            with output_path.open("w", newline = "") as csv_file:
                csvwriter = csv.writer(csv_file, delimiter = ",")
                csvwriter.writerows(qualifying_loans_)
            print(f'The qualifying loans shown above have been recorded on the "qualifying_loans.csv" file, which has been downloaded to {os.path.abspath("qualifying_loans.csv")}')    
            x = 0
        elif str.lower(save) in ["no", "n"]:
            x = 0
        else:
            save = questionary.text("Please respond 'yes' or 'no'...").ask()
            print()
       
"""The main function for running the script."""

def run():
    
    # Load the latest Bank data
    bank_data = load_bank_data()

    # Get the applicant's information
    credit_score, debt, income, loan_amount, home_value = get_applicant_info()

    # Find qualifying loans
    qualifying_loans = find_qualifying_loans(
        bank_data, credit_score, debt, income, loan_amount, home_value
    )

    if len(qualifying_loans) > 0: # Skipping these two functions if there are no qualifying loans

        # Optional: View qualifying loans
        view_qualifying_loans(qualifying_loans)
        
        # Optional: Save qualifying loans
        save_qualifying_loans(qualifying_loans)

    print(Fore.MAGENTA + "\n   Thank you for using the Loan Qualification App by Exastorm.\n")

if __name__ == "__main__":
    # fire.Fire(run) # I did not find any purpose for the 'fire' module
    run()