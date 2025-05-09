# Table Plan Project

*A simple table plan generator for multiple meals*

## Description

This Python script helps to automatically create seating arrangements for different meals. You provide a list of attendees and their details in a CSV file, and the script tries to make sensible seating plans. It considers who people are related to, who they'd prefer to sit with, and aims for a mix of genders at the table. It also tries to make sure people don't sit next to the exact same person over multiple meals.

## Features

* Reads guest list and details from a CSV file.
* Generates circular seating plans for one or more meals (e.g., Breakfast, Lunch, Dinner).
* Tries to sit people next to their preferred companions (`P*`).
* Tries to avoid seating relations next to each other (`R!`) – this is penalised.
* Allows a maximum of one same-sex pairing per table (`S!`).
* Avoids repeating neighbour pairs from previous meals (`N!`).
* Shows the plan as a simple list and a basic visual diagram in the terminal.

## Getting Started

1.  **Python:** Make sure you have Python 3 installed. This script uses only standard Python libraries (`csv`, `math`), so no special installations are needed.
2.  **Input File:** You will need a CSV file containing your attendee information.
    * A **blank template** with just the necessary headers is provided as `Blank_Plan.csv` to help you get started.
    * An **example of a filled CSV file** is also included as `Example_Plan.csv` for you to see how it works.
    * You can copy either `Blank_Plan.csv` or `Example_Plan.csv`, rename it (e.g., `my_event_attendees.csv`), and then edit it with your actual attendee data. See the "Input CSV File Format" section below for details on each column.
3.  **Run the Script:** Open your terminal or command prompt, navigate to the directory where you saved the script and your CSV file, and run:
    ```bash
    python Table_Plans.py
    ```
    The script will then ask you to enter the name of your CSV file (e.g., `my_event_attendees.csv`).

## Input CSV File Format

The script needs a CSV file with the following columns, in this order. Please refer to `Example_Plan.csv` for a practical example and use `Blank_Plan.csv` to create your own file.

1.  `name`: The full name of the person.
    * Example: `John Smith`
2.  `sex`: The person's sex. This must be `male` or `female`.
    * Example: `male`
3.  `relations`: A list of names (separated by commas) of people this person is related to. If they have no relations in the list, leave this blank.
    * Example: `Sarah Jones,David Wilson`
    * Example (no relations): ``
4.  `preferred people`: A list of names (separated by commas) of people this person would like to sit next to. Leave blank if no preferences.
    * Example: `Tom Brown`
    * Example (no preferences): ``
5.  **Meal Columns (e.g., `Breakfast`, `Lunch`, `Evening Dinner`):**
    * After the `preferred people` column, add one column for each meal you are planning.
    * The **full header of the column** (e.g., `Breakfast Club Meeting`, `Annual Charity Dinner`, `Lunch`) will be used as the meal name/ID. Any leading or trailing spaces in the header will be removed.
    * In each person's row, put `yes` (case-insensitive) in a meal column if they are attending that meal. If they are not attending, you can leave it blank or put any other text.

For a complete example of how the data should look, please open and review the `Example_Plan.csv` file included in this project.

## Output

The script will print the seating arrangements to your terminal. For each meal, you'll see:

* A summary of whether a plan was found.
* **List View:** Details of who is sitting next to whom, with indicators:
    * `(P*)`: Preferred people sitting together.
    * `(R!)`: Related people sitting together (this is penalised).
    * `(S!)`: A same-sex pair (the script allows only one such pair per table). It also shows the count.
    * `(N!)`: This pair of people already sat together at a previous meal shown in the list.
* **Visual Layout:** A simple text drawing of the circular table with names and seat numbers.

## Customisation

The way the script decides on the "best" arrangement is based on scores. These scores (penalties and bonuses) are set as constants at the top of the Python script (`Table_Plans.py` - e.g., `BONUS_PREFERRED`, `PENALTY_RELATION`). You can change these numbers in the script if you want to make certain rules more or less important.

## Possible Future Ideas

* The script currently finds one arrangement per meal if possible. It could be changed to find several different options.

---
This README was generated based on the script's functionality and then amended by the author
*Author: TFortescue*
