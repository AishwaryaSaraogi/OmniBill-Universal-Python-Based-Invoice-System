import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

Students = pd.read_csv("Students.csv", on_bad_lines = 'skip')
Courses = pd.read_csv("Courses.csv")

def Bill_Generator(Student_id, Course_id, Quantities):
    Student = Students[Students['Student_id'] == Student_id].iloc[0]
    selected_Course = Courses[Courses['Course_id'].isin(Course_id)]

    if len(selected_Course) != len(Quantities):
        st.sidebar.error("Select The Course.")
        return None
    
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Times", 'B', size = 30)
    pdf.cell(200, 10, txt = "BILL GENERATOR", ln = 10, align = 'C')
    pdf.cell(200, 10, txt = " ", ln = True)

    pdf.image("Logo.png", x = 150, y = 30, w = 35)

    pdf.set_font("Times", size = 12)
    pdf.cell(200, 10, txt = "Aishwarya Pvt Ltd", ln = True)
    pdf.cell(200, 10, txt = "Jabalpur, Madhya Pradesh, India", ln = True)
    pdf.cell(200, 10, txt = "Pincode : 482002", ln = True)
    pdf.cell(200, 10, txt = "Email : aishwaryasaraogi@gmail.com", ln = True)
    pdf.cell(200, 10, txt = " ", ln = True)

    pdf.set_font("Times", 'B', size = 20)
    pdf.cell(200, 10, txt = "Student Details:", ln = True)
    pdf.cell(200, 10, txt = " ", ln = True)

    pdf.set_font("Times", size = 12)
    pdf.cell(200, 10, txt = f"Student: {Student['Student_name']} ", ln = True)
    pdf.cell(200, 10, txt = f"Address: {Student['Address']} ", ln = True)
    pdf.cell(200, 10, txt = f"Mobile Number: {Student['Mobile_Number']}", ln = True)
    pdf.cell(200, 10, txt = f"Email: {Student['Email']} ", ln = True)
    pdf.cell(200, 10, txt = " ", ln = True)

    pdf.set_font("Times", size = 12)
    pdf.cell(50, 10, txt = "Course", border =1)
    pdf.cell(60, 10, txt = "Description", border =1)
    pdf.cell(20, 10, txt = "Quantity", border =1)
    pdf.cell(30, 10, txt = "Unit Price", border =1)
    pdf.cell(30, 10, txt = "total", border =1)
    pdf.ln()

    total = 0
    pdf.set_font("Times", size=12)
    for i, row in selected_Course.iterrows():
        Quantity = Quantities[Course_id.index(row['Course_id'])]
        line_total = row['Fees'] * Quantity
        total += line_total

        pdf.set_font("Times", size = 12)
        pdf.cell(50, 10, txt = str(row['Course_name']), border = 1)
        pdf.cell(60, 10, txt = str(row['Description']), border = 1)
        pdf.cell(20, 10, txt = str(Quantity), border = 1)
        pdf.cell(30, 10, txt = f"Rs. {row['Fees']}", border = 1)
        pdf.cell(30, 10, txt = f"Rs. {line_total}", border = 1)
        pdf.ln()

    pdf.cell(200, 10, txt = " ", ln = True)

    pdf.set_font("Times", 'B', size = 12)
    pdf.cell(160, 10, txt = "Total", border = 1)
    pdf.cell(30, 10, txt = f"Rs. {total}", border = 1, ln = True)

    Filename = f"Bill_Generator_{Student_id}.pdf"
    pdf.output(Filename)
    return Filename

st.set_page_config(page_title= "Bill Generator")

st.title("Bill Generator")
st.sidebar.header("Select Student and Course Details")

students = Students["Student_name"].tolist()
dropdown_options = ["Select Student", "➕ Add New Student"] + students

if "selected_student" not in st.session_state:
    st.session_state.selected_student = "--- Select Student ---"

if st.session_state.selected_student == "➕ Add New Student":
    st.sidebar.subheader("Register New Student")

    try:
        if not Students.empty:
            id_str = str(Students["Student_id"].iloc[-1])
            id_num = int(id_str.split('-')[-1])
            id = id_num + 1
            new_id = f"STU-2026-{id}"
        else: 
            new_id = "STU-2026-101"
    except Exception as e:
        new_id = f"STU-2026-{len(Students) + 101}"

    st.sidebar.info(f"Generated Student ID: *{new_id}*")

    Name = st.sidebar.text_input("Enter Student Name", key="reg_name")
    Address = st.sidebar.text_input("Enter Address", key="reg_address")
    Mobile_Number = st.sidebar.text_input("Enter Mobile Number", key="reg_mobile")
    Email = st.sidebar.text_input("Enter Email ID", key="reg_email")

    submit_reg = st.sidebar.button("Save Student")

    if submit_reg:
        if Name.strip() and Address.strip() and Mobile_Number.strip() and Email.strip():
            with open("Students.csv", "r", encoding = "utf-8") as f:
                content = f.read()

            if content and not content.endswith('\n'):
                with open("Students.csv", "a", encoding = "utf-8") as f:
                    f.write('\n')

            row = {'Student_id': id, 'Student_name': Name.strip(), 'Address': Address.strip(), 'Mobile Number': Mobile_Number.strip(), 'Email': Email.strip()}
            new = pd.DataFrame([row])
            new.to_csv("Students.csv", mode = 'a', header = False, index = False, lineterminator = '\n')

            Students = pd.read_csv("Students.csv", on_bad_lines='skip')

            st.session_state.selected_student = Name.strip()
            st.rerun()

        else:
            st.sidebar.error("Please Fill Form.")

    st.sidebar.markdown("-----")

students = Students["Student_name"].tolist()
dropdown_options = ["--- Select Student ---", "➕ Add New Student"] + students

if st.session_state.selected_student in dropdown_options:
    default_index = dropdown_options.index(st.session_state.selected_student)
else: 
    default_index = 0

selected_student = st.sidebar.selectbox(
    "Choose Student", 
    dropdown_options, 
    index = default_index,
    key="student_selector"
)

if st.session_state.selected_student != selected_student:
    st.session_state.selected_student = selected_student
    st.rerun()

if selected_student != "--- Select Student ---" and selected_student != "➕ Add New Student":
    Student_id = Students[Students['Student_name'] == selected_student]['Student_id'].values[0]

    courses = Courses['Course_name'].tolist()
    selected_Course = st.sidebar.multiselect("Courses", courses)
    Course_id = Courses[Courses['Course_name'].isin(selected_Course)]['Course_id'].tolist()

    Quantities = []
    for i, item in enumerate(selected_Course):
        Quantity = st.sidebar.number_input(f"Quantity of {item}", min_value=1, max_value=100, value=1, key=f"Quantity_{i}")
        Quantities.append(Quantity)

    submit = st.sidebar.button("Bill Generator")

    if 'submit' in locals() and submit:
        if len(Course_id) != len(Quantities):
            st.sidebar.error("Select The Course.")
        else:
            Filename = Bill_Generator(Student_id, Course_id, Quantities)
            if Filename:
                with open(Filename, 'rb') as f:
                    st.download_button(label = "Download Bill", data=f, file_name=Filename, mime= "application/pdf")

                with open(Filename, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')

                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

st.write(f"*Selected Student: * {selected_student}")
st.write("*Selected Courses: *")

if 'selected_Course' in locals() and selected_Course:
        for i, courses in enumerate(selected_Course):
            if i < len(Quantities):
                st.write(f"- {courses} ({Quantities[i]} units)")