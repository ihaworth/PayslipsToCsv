import csv
import re
import subprocess
import sys
from collections import defaultdict

# Uncomment these and related lines to see all Sections and/or Elements in the input files
# all_sections = set()
# all_elements = set()


def pdf_to_text(payslip):
    return subprocess.check_output(['pdftotext', '-layout', payslip, '-'], encoding="utf-8")


def parse_payslip(payslip_text):
    # the data is stored under section and element: payslip_data[<section_name>][<element_name>]
    payslip_data = defaultdict(lambda: defaultdict(lambda: ''))
    current_sections = []
    for line in payslip_text.splitlines():
        # Lines that start immediately at the first char of the line are mostly Sections like 'Employee Details'
        # It also includes Month Ending, plus a few false positives that we parse but don't output
        if re.match(r'^[A-Z]', line):
            # Reset data about any previous sections, so we don't include these
            current_sections = []
            # Month Ending needs special treatment
            if re.match(r'.*Month Ending.*', line):
                heading_parts = re.split(r'Month Ending', line)
                payslip_data['Heading']['Month Ending'] = heading_parts[1].strip()
            else:
                # Otherwise, we're mostly Section definitions, like 'Employee Details', 'Payments', 'Deductions', etc.
                for section in re.split(r'  +', line):
                    section_name = section.strip()
                    start_char = line.find(section_name)
                    current_sections.append((section_name, start_char))
                    # all_sections.add(section)

        # The data Elements we're after are on lines that start with a space
        if re.match(r'^ [A-Z]', line):
            # These are all in the sections captured above, so break down the line for each section
            for section_index in range(0, 3):
                start_char = current_sections[section_index][1]
                element_text = line[start_char:start_char + 45]
                element_parts = re.split(r'  +', element_text)
                if len(element_parts) >= 2:
                    element_name, element_value = [part.strip() for part in element_parts[0:2]]
                    section_name = current_sections[section_index][0]
                    payslip_data[section_name][element_name] = element_value
                    # all_elements.add(section_name + ":" + element_name)
    return payslip_data


def write_csv(payslips_data, output_stream=sys.stdout):
    output = csv.writer(output_stream)
    output.writerow(['Tax code',
                     'Month Ending',
                     'Monthly pay', 'Bonus', 'Additional pay',
                     'Tax', 'NI', 'Salary Sacrifice',
                     'Taxable gross pay', 'Employer NI', 'Net pay'])
    for payslip_data in payslips_data:
        output.writerow([
            payslip_data['Employee Details']['Tax code'],
            payslip_data['Heading']['Month Ending'],
            # data['Employee Details']['Works number'],
            payslip_data['Payments']['Monthly pay'],
            payslip_data['Payments']['Bonus'],
            payslip_data['Payments']['Additional pay'],
            payslip_data['Deductions']['Tax'],
            payslip_data['Deductions']['National Insurance'],
            payslip_data['Deductions']['Salary Sacrifice'],
            payslip_data['This Month']['Taxable gross pay'],
            payslip_data['This Month']['Employer National Insurance'],
            payslip_data['This Month']['Net pay']
        ])


payslips = sys.argv[1:]
payslips_text = [pdf_to_text(payslip) for payslip in payslips]
payslips_data = [parse_payslip(payslip_text) for payslip_text in payslips_text]
write_csv(payslips_data)

# print()
# for section in sorted(all_sections):
#     print(section)

# for element in sorted(all_elements):
#     print(element)
