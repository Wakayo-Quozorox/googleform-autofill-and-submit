# Name: Wakayo Quozorox
# Date: 22-jan-2024
# Version: 0.1.0

import form
import random

# This script is used to fill a form with pseudo-random data (oriented filling)
# It uses random.choices() to choose a random value from a list of values with a list of probabilities (weights)
#
# The script import URL from local folder "Local/URL.txt" that is not included in the repo
# It imports the list of questions and options with the function get_form_submit_request() from form.py

# Get URL from file
try:
    url = open("Local/URL.txt", "r").readline()
except IOError:
    print("Error: File not found or unable to read file.")
except Exception as e:
    print("An unexpected error occurred:", e)

# Get form data from URL
form_data = form.parse_form_entries(url)

# Select random value for each question
filled_form = {}

for question in form_data:
    if question["type"] == 2:   # Multiple choice
        # Choose a random value from the list of options
        filled_form[f"entry.{question['id']}"] = random.choice(question["options"])
    elif question["type"] == 4: # Checkbox
        # Choose a random number of options from the list of options
        num_options = random.randint(1, len(question["options"]))
        filled_form[f"entry.{question['id']}"] = random.sample(question["options"], num_options)
    else:
        print(f"Error: Question type {question['type']} not supported")
        exit()
    # Print result
    print(f"{question['container_name']}: {filled_form["entry."+str(question["id"])]}")

# Send result to form
form.submit(url, filled_form)
