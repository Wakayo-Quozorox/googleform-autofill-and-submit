# 🚀 Google Form AutoFill and Submit

Orginally created by Tien-Thanh Nguyen-Dang (GitHub depot [here](https://github.com/tienthanh214/googleform-autofill-and-submit)), I modified some of the code to populate the form with random data.

## Prerequisites

- Python 3.x
- `requests` library (`pip install requests` or `pip install -r requirements.txt`)

## Use

Create a `Local/URL.txt` file with the URL of the form to fill out.
It is not imported in GitHub for privacy reasons.

The `example.py` script will fill out the form with random data and submit it, once. It only manage multiple choice questions and checkboxes (for now).

Work is in progress to make it work with other types of questions and automatically submit the form multiple times.
Orienting the randomly generated data with a file is on the roadmap too.

## Limitations

Please note that this script currently operates only with Google Forms that do not require user authentication.
