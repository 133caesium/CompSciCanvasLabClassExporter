import csv
import os
import matplotlib.pyplot as plt
import numpy as np
import jinja2
import pdfkit
import pandas as pd


#SETUP

filename = "2021-07-23T0949_Grades-COMPSCI_235.csv"

all_lab_slots = ['B01C', 'B02C', 'B03C', 'B04C', 'B05C', 'B06C']

total_rows = 55

input_folder = "input_files"
output_folder = "output"

filename = os.path.join(input_folder, filename)

# PROCESSING

labslot_to_student_dict = {}
for labslot in all_lab_slots:
    labslot_to_student_dict[labslot] = []

with open(filename, newline='') as csvfile:
    studentreader = csv.DictReader(csvfile, delimiter = ',')

    for row in studentreader:
        #print(row['Student'], row['SIS Login ID'], row['Section'])
        for labslot in all_lab_slots:
            if row['Section'].find(labslot) != -1:
                if row["Student"] != 'student, Test' and row["Student"] != '' and len(row["SIS Login ID"]) > 5 and len(row["SIS Login ID"]) < 9:
                    labslot_to_student_dict[labslot].append((row["Student"], row["SIS Login ID"]))

    for labslot in all_lab_slots:
        print(f"{labslot}: {len(labslot_to_student_dict[labslot])} {labslot_to_student_dict[labslot]}")


fieldnames = ["Student", "UPI", "Signature"]

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "pdf_attendance_sheet_template.html"
template = templateEnv.get_template(TEMPLATE_FILE)

for labslot in all_lab_slots:

    number_of_extra_rows = max(0, total_rows - len(labslot_to_student_dict[labslot]))
    outputText = template.render(which_lab=labslot, column_names=fieldnames,
                                 student_entries=labslot_to_student_dict[labslot],
                                 number_of_extra_rows=number_of_extra_rows)

    html_filename = f"{labslot}.html"
    pdf_filename = f"{labslot}.pdf"
    html_file = open(os.path.join(output_folder, html_filename), 'w')
    html_file.write(outputText)
    html_file.close()

    # convert html to pdf simply via pdfkit
    pdfkit.from_file(os.path.join(output_folder, html_filename), os.path.join(output_folder, pdf_filename))

    with open(os.path.join(output_folder, f"{labslot}.csv"), 'w', newline='') as csvoutfile:
        writer = csv.DictWriter(csvoutfile, fieldnames=fieldnames)

        writer.writeheader()
        for student in labslot_to_student_dict[labslot]:
            writer.writerow({f"{fieldnames[0]}": student[0], f"{fieldnames[1]}": student[1], f"{fieldnames[2]}": ""})

