# Name: Wakayo Quozorox
# Date: 23-jan-2024
# Version: 0.1.0

from os.path import exists
import form
import random
import json

# Test if "Local/form_data.txt" exists
if not exists("Local/form_data.txt"):
    # Generate form extract
    form.generate_form_extract()

    # Tell user to edit the file to add the oriented values, 
    # or to restart the script to generate random values
    print("Please edit Local/form_data.txt to add the oriented values, or restart the script to generate random values")
# else:
#     # Read form extract
#     possible_data = form.check_form_extract()
#     # Compute random values
#     filled_form = form.fill_form_random(possible_data)
#     # Send result to form
    
    filled_form = {}
    data = json.load(open("Local/form.json", "r"))
    # Test if weights are valid
    if not form.check_options_weights(data):
        print("Error: Invalid weights")
        return
    # Build response
    for question in data:
        if question['type'] == 2:   # Multiple choice
            # Choose a random value from the list of options
            filled_form[f"entry.{question['id']}"] = random.choices(question["options"], weights=[option['weight'] for option in question['options']])[0]['option']
