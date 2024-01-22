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
datas = form.parse_form_entries(url)

# Select random value for each question
result = {}

for data in datas:
    if data["type"] == 2:   # Multiple choice
        # Choose a random value from the list of options
        result["entry."+str(data["id"])] = random.choice(data["options"])
    elif data["type"] == 4: # Checkbox
        # Choose a random number of options from the list of options
        result["entry."+str(data["id"])] = list(set(random.choices(data["options"], k=random.randint(1, len(data["options"])))))

# Print result
for i in range(len(result)):
    print(f"{datas[i]['container_name']}: {result["entry."+str(datas[i]["id"])]}")

# Send result to form
form.submit(url, result)
