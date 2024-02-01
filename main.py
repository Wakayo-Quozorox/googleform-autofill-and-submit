# Name: Wakayo Quozorox
# Date: 23-jan-2024
# Version: 0.1.0

from os.path import exists
import form
import random
import json

# Test if "Local/form.json" exists
if not exists("Local/form.json"):
    # Generate form extract
    form.generate_form_extract()

    # Tell user to edit the file to add the oriented values, 
    # or to restart the script to generate random values
    print("Please edit Local/form_data.txt to add the oriented values, \
or restart the script to generate random values")
    exit()

else:
    # Get form data from file    
    filled_form = {}
    data = json.load(open("Local/form.json", "r"))
    # Test if weights are valid
    if not form.check_options_weights(data):
        print("Error: Invalid weights")
        exit()
    # Build response
    for question in data:
        if question['type'] == 2:   # Multiple choice
            if "XX" in question['options'][0]['weight']:
                # Choose a random value from the list of options
                filled_form[f"entry.{question['id']}"] = random.choice(question['options'])['option']
            else:
                # Choose each option along with its weight
                filled_form[f"entry.{question['id']}"] = random.choices(question["options"], weights=[int(option['weight'])/100 for option in question['options']])[0]['option']
        elif question['type'] == 4: # Checkbox
            filled_form[f"entry.{question['id']}"] = []
            if "XX" in question['options'][0]['weight']:
                # Choose a random value from the list of options
                filled_form[f"entry.{question['id']}"].append(random.choice(question['options'])['option'])
            else:
                # Choose each option along with its weight
                for option in question['options']:
                    if random.randint(0, 1) < int(option['weight'])/100:
                        filled_form[f"entry.{question['id']}"].append(option['option'])
        else:
            print(f"Error: Question type {question['type']} not supported")
            exit()
    for answers in filled_form:
        print(f"{answers}: {filled_form[answers]}")