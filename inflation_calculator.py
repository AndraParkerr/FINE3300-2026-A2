import pandas as pd
import numpy as np


# Load and prepare the CPI dataset
def load_cpi_data():
    data_file = "data/CPI_Data.csv"

    cpi_data = pd.read_csv(data_file, skiprows=8)

    cpi_data["date"] = pd.to_datetime(cpi_data["date"])
    cpi_data["STATIC_INFLATIONCALC"] = pd.to_numeric(
        cpi_data["STATIC_INFLATIONCALC"], errors="coerce"
    )

    cpi_data = cpi_data.dropna()
    cpi_data = cpi_data.sort_values("date")

    return cpi_data.set_index("date")


# Ask the user for a valid positive price
def get_price():
    while True:
        try:
            price = float(input("Enter the original price (CAD): $"))

            if not np.isfinite(price) or price <= 0:
                print("Please enter a valid price greater than zero.")
            else:
                return price

        except ValueError:
            print("Invalid input. Please enter a numerical price.")


# Ask the user for a valid date within the dataset
def get_date(prompt, cpi_data):
    earliest_date = cpi_data.index.min()
    latest_date = cpi_data.index.max()

    while True:
        date_input = input(prompt)

        try:
            selected_date = pd.to_datetime(
                date_input + "-01",
                format="%Y-%m-%d"
            )

            if selected_date not in cpi_data.index:
                print(
                    f"Please enter a month between "
                    f"{earliest_date:%Y-%m} and {latest_date:%Y-%m} "
                    f"that exists in the dataset."
                )
                continue

            return selected_date

        except ValueError:
            print("Invalid date. Please use YYYY-MM format.")


# Calculate the inflation-adjusted price and rates of change
def calculate_inflation(price, first_date, second_date, cpi_data):

    first_cpi = cpi_data.loc[first_date, "STATIC_INFLATIONCALC"]
    second_cpi = cpi_data.loc[second_date, "STATIC_INFLATIONCALC"]

    adjusted_price = price * (second_cpi / first_cpi)

    percentage_change = (
        (second_cpi / first_cpi) - 1
    ) * 100

    number_of_months = (
        (second_date.year - first_date.year) * 12
        + second_date.month - first_date.month
    )

    number_of_years = number_of_months / 12

    if number_of_months > 0:
        annual_rate = (
            np.power(second_cpi / first_cpi, 12 / number_of_months) - 1
        ) * 100
    else:
        annual_rate = None

    return (
        adjusted_price,
        percentage_change,
        number_of_years,
        annual_rate,
        first_cpi,
        second_cpi
    )


# Display the calculation results
def display_results(
    price,
    adjusted_price,
    percentage_change,
    number_of_years,
    annual_rate,
    first_cpi,
    second_cpi,
    first_date,
    second_date
):

    print("\n========== INFLATION CALCULATOR RESULTS ==========")

    print(f"Original price:             ${price:,.2f} CAD")
    print(f"Adjusted price:             ${adjusted_price:,.2f} CAD")

    print(f"Percentage change:          {percentage_change:,.2f}%")
    print(f"Number of years:            {number_of_years:,.2f}")

    if annual_rate is not None:
        print(f"Annual rate of change:      {annual_rate:,.2f}%")
    else:
        print("Annual rate of change:      N/A (same dates)")

    print(f"CPI for {first_date:%Y-%m}:             {first_cpi:.2f}")
    print(f"CPI for {second_date:%Y-%m}:             {second_cpi:.2f}")

    # Interpret the overall CPI change
    if percentage_change > 0:
        print("\nInterpretation: The overall CPI price level increased over the selected period.")
    elif percentage_change < 0:
        print("\nInterpretation: The overall CPI price level decreased over the selected period.")
    else:
        print("\nInterpretation: There was no change in the CPI over the selected period.")

    print("==================================================")


# Main program
def main():

    print("CANADIAN INFLATION CALCULATOR")
    print("--------------------------------")

    cpi_data = load_cpi_data()

    price = get_price()

    first_date = get_date(
        "Enter the first date (YYYY-MM): ",
        cpi_data
    )

    while True:
        second_date = get_date(
            "Enter the second date (YYYY-MM): ",
            cpi_data
        )

        if second_date < first_date:
            print("The second date must be on or after the first date.")
        else:
            break

    results = calculate_inflation(
        price,
        first_date,
        second_date,
        cpi_data
    )

    display_results(
        price,
        *results,
        first_date,
        second_date
    )


if __name__ == "__main__":
    main()
