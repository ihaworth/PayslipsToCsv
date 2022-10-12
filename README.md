# Payslip Parser
Extracts pay information from multiple Bright Pay pdf payslips and presents it
in csv form, handy for processing with a spreadsheet or similar.

## Installation
### Ubuntu Linux
Install python3:

`sudo apt install python3`

The script uses `pdftotext` which should already be installed on ubuntu linux.

### Mac
Using brew:

`brew install python3`

Then to install `pdftotext` you need to install the poppler utils package:

`brew install poppler`

## Use

Get the pdf payslips you want to work with in a location where they can be easily accessed,
usually all in 1 directory. Also add the Parser.py file from this repo.

Then, in a terminal, run:

`python3 Parser.py *.pdf`

This will generate output in the terminal which can be copied 'n' pasted elsewhere.

If you prefer the csv data in a file, then use:

`python3 Parser.py *.pdf > my_payslip_data.csv`
