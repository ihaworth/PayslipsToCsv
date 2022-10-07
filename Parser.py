import csv
import re
import subprocess
import sys
from collections import defaultdict

payslips = sys.argv[1:]

# Uncomment these and related lines to see all Sections and/or Elements in the input files
# all_sections = set()
# all_elements = set()


def parse_payslip(payslip):
    file_data = defaultdict(lambda: defaultdict(lambda: ''))
    current_sections = []
    payslip_text = subprocess.check_output(['pdftotext', '-layout', payslip, '-'], encoding="utf-8")
    for line in payslip_text.splitlines():
        # Lines that start immediately at the first char of the line are mostly Sections like 'Employee Details'
        # It also includes Month Ending, plus a few false positives that we parse but don't output
        if re.match(r'^[A-Z]', line):
            # Reset data about the previous section, so we don't have pollution
            current_sections = []

            # Month Ending needs special treatment
            if re.match(r'.*Month Ending.*', line):
                parts = re.split(r'Month Ending', line)
                file_data['Heading']['Month Ending'] = parts[1].strip()
            else:
                # Otherwise, we're mostly Section definitions, like 'Employee Details', 'Payments', 'Deductions', etc.
                for section in re.split(r'  +', line):
                    section = section.strip()
                    start_x = line.find(section)
                    current_sections.append((section, start_x))
                    # all_sections.add(section)

        # The real data we're after is on lines that start with a space
        if re.match(r'^ [A-Z]', line):
            # These are all in the sections captured above, so break down the line for each section
            for section_index in range(0, 3):
                start_x = current_sections[section_index][1]
                element_text = line[start_x:start_x + 45]
                parts = re.split(r'  +', element_text)
                if len(parts) >= 2:
                    element_name = parts[0].strip()
                    element_value = parts[1].strip()
                    section_name = current_sections[section_index][0]
                    file_data[section_name][element_name] = element_value
                    # all_elements.add(element_name)
    return file_data


payslips_data = [parse_payslip(payslip) for payslip in payslips]

output = csv.writer(sys.stdout)
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
        ]
    )

# print()
# for section in sorted(all_sections):
#     print(section)

# for element in sorted(all_elements):
#     print(element)
