""" Get entries from form 
    Version 1: 
        - support submit almost all types of google form fields
        - only support single page form
        - not support upload file (because it's required to login)
    Date: 2023-12-17
"""

import argparse
import json
import re
import random

import requests


# constants
ALL_DATA_FIELDS = "FB_PUBLIC_LOAD_DATA_"

""" --------- Helper functions ---------  """

def get_form_response_url(url: str):
    """
    Converts a Google Form URL to the corresponding form response URL.

    Args:
        url (str): The Google Form URL.

    Returns:
        str: The form response URL.
    """
    url = url.replace('/viewform', '/formResponse')
    if not url.endswith('/formResponse'):
        if not url.endswith('/'):
            url += '/'
        url += 'formResponse'
    return url

def get_form_url(path= "Local/URL.txt"):
    """
    Retrieves the URL of the form from a specified file.

    Args:
        path (str): The path to the file containing the URL. Defaults to "Local/URL.txt".

    Returns:
        str: The URL of the form.

    Raises:
        IOError: If the file is not found or unable to be read.
        Exception: If an unexpected error occurs.
    """
    try:
        url = open(path, "r").readline()
    except IOError:
        print("Error: File not found or unable to read file.")
        exit()
    except Exception as e:
        print("An unexpected error occurred:", e)
        exit()
    return url

def extract_script_variables(name :str, html: str):
    """
    Extracts the value of a script variable from an HTML string.

    Parameters:
    name (str): The name of the script variable.
    html (str): The HTML string to search for the script variable.

    Returns:
    dict or None: The value of the script variable as a dictionary, or None if the variable is not found.
    """
    pattern = re.compile(r'var\s' + name + r'\s=\s(.*?);')
    match = pattern.search(html)
    if not match:
        return None
    value_str = match.group(1)
    return json.loads(value_str)

def get_fb_public_load_data(url: str):
    """
    Retrieves form data from a given URL.

    Args:
        url (str): The URL of the form.

    Returns:
        dict: A dictionary containing the extracted form data.
            Returns None if there was an error retrieving the data.
    """
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        print("Error! Can't get form data", response.status_code)
        return None
    return extract_script_variables(ALL_DATA_FIELDS, response.text)

def submit(url, data):
    """
    Submits form data to the specified URL.

    Args:
        url (str): The URL of the form response endpoint.
        data (dict): The form data to be submitted.

    Returns:
        bool: True if the form submission is successful, False otherwise.
    """
    response_url = get_form_response_url(url)

    try:
        res = requests.post(response_url, data=data)
        if res.status_code != 200:
            # TODO: show error message
            raise Exception("Error! Can't submit form", res.status_code)
        return True
    except Exception as e:
        print("Error!", e)
        return False

""" ------ MAIN LOGIC ------ """
def parse_form_entries(url: str, only_required = False):
    """
    In window.FB_PUBLIC_LOAD_DATA_ (as v) 
    - v[1][1] is the form entries array
    - for x in v[1][1]:
        x[0] is the entry id of the entry container
        x[1] is the entry name (*)
        x[3] is the entry type 
        x[4] is the array of entry (usually length of 1, but can be more if Grid Choice, Linear Scale)
            x[4][0] is the entry id (we only need this to make request) (*)
            x[4][1] is the array of entry value (if null then text)
                x[4][1][i][0] is the i-th entry value option (*)
            x[4][2] field required (1 if required, 0 if not) (*)
            x[4][3] name of Grid Choice, Linear Scale (in array)

    """
    url = get_form_response_url(url)
        
    v = get_fb_public_load_data(url)
    if not v or not v[1] or not v[1][1]:
        print("Error! Can't get form entries")
        return None
    
    def parse_entry(entry):
        entry_name = entry[1]
        entry_type_id = entry[3]
        result = []
        for sub_entry in entry[4]:
            info = {
                "id": sub_entry[0],
                "container_name": entry_name,
                "type": entry_type_id,
                "required": sub_entry[2] == 1,
                "name": ' - '.join(sub_entry[3]) if (len(sub_entry) > 3 and sub_entry[3]) else None,
                "options": [(x[0] if x[0] != "" else "!ANY TEXT")for x in sub_entry[1]] if sub_entry[1] else None,
            }
            if only_required and not info['required']:
                continue
            result.append(info)
        return result

    parsed_entries = []
    for entry in v[1][1]:
        parsed_entries += parse_entry(entry)
        
    return parsed_entries

""" ------ OUTPUT ------ """
def get_form_submit_request(url: str, output = "console", only_required = False, with_comment = True):
    entries = parse_form_entries(url, only_required = only_required)
    result = generate_form_request_dict(entries, with_comment)
    if output == "console":
        print(result)
    elif output == "return":
        return result
    else:
        # save as file
        with open(output, "w") as f:
            f.write(result)
            print(f"Saved to {output}", flush = True)
    pass

def generate_json(entries):
    with open("Local/form.json", "w") as file:
        json.dump(entries, file, indent=4)
        print(f"Saved to Local/form.json", flush=True)

def generate_form_request_dict(entries, with_comment: bool = True):
    """ Generate a dict of form request data from entries"""
    result = "{\n"
    for entry in entries:
        if with_comment:
            # gen name of entry
            result += f"    # {entry['container_name']}{': ' + entry['name'] if entry['name'] else ''} {'(required)' * entry['required']}\n"
            # gen all options (if any)
            if entry['options']:
                result += f"    #   Options: {entry['options']}\n"
            else:
                result += f"    #   Option: any text\n"
        # gen entry id
        result += f'    "entry.{entry["id"]}": "",\n'

    result += "}"
    return result

def generate_form_extract():
    # Get data from URL and save it to a file
    url = get_form_url()

    form_data = parse_form_entries(url)
    result = ""
    #result += f"# Replace \"XX\" with wanted final percentage for oriented answers\n Example:\n# Option 1:10\n# Option 2:40\n# Option 3:50\n\n"
    for question in form_data:
        if 'options' in question:
            new_option = []
            for option in question['options']:
                new_option.append({
                    "option": option,
                    "weight": "XX"
                })
            question['options'] = new_option       
        else:
            question['options'] = "!ANY_TEXT"
    result += json.dumps(form_data, indent=4)

    with open("Local/form.json", "w") as file:
        file.write(result)
        print(f"Saved to Local/form_data.txt", flush=True)

def check_options_weights(data):
    weight_not_set_flag = False
    exit_flag = False
    for question in data:
        total_weight = 0
        if question['type'] == 2:
            if 'options' in question:
                for option in question['options']:
                    if 'weight' not in option:
                        print(f"Error: Weight not found for {option['option']}")
                        exit_flag = True
                    elif option['weight'] == 'XX':
                        print(f"Warning: Weight for {option['option']} is not set. Random value will be generated")
                        weight_not_set_flag = True
                    elif int(option['weight']) > 100:
                        print(f"Error: Weight for {option['option']} is greater than 100")
                        exit_flag = True
                    elif int(option['weight']) < 0:
                        print(f"Error: Weight for {option['option']} is less than 0")
                        exit_flag = True
                    else:
                        total_weight += int(option['weight'])
                        print("Total weight:", total_weight)
                if weight_not_set_flag and total_weight > 100:
                    print(f"Error: Total weight is greater than 100")
                    exit_flag = True
                elif not weight_not_set_flag and total_weight != 100:
                    print(f"Error: Total weight is not 100")
                    exit_flag = True
            if exit_flag:
                print(f"Error in question : {question['container_name']}")
                return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Form Autofill and Submit")
    parser.add_argument("url", help="Google Form URL", )
    parser.add_argument("-o", "--output", default="console", help="Output file path (default: console)")
    parser.add_argument("-r", "--required", action="store_true", help="Only include required fields")
    parser.add_argument("-c", "--no-comment", action="store_true", help="Don't include explain comment for each field")
    args = parser.parse_args()
    get_form_submit_request(args.url, args.output, args.required, not args.no_comment)
    pass