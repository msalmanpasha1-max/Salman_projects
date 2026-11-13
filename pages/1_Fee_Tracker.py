import streamlit as st
import pandas as pd
from datetime import date

st.title("Tuition Fee Tracker")
students = pd.read_csv("students.csv", dtype={"phone_no": str})
choice = st.sidebar.radio("Menu", ["Show Students","ADD Students","ADD Payments","Defaulters","Monthly Summary","Student History"])

if choice == "Show Students":
    st.dataframe(students)
elif choice == "ADD Students":
        name = st.text_input("Name")
        cla_ss = st.text_input("Class")
        phone = st.text_input("Phone Number")
        monthly_fees = st.number_input("Monthly Fees", step=500)
        join_date = st.text_input("Join Date (YYYY-MM-DD)")

        if st.button("Save Student"):
            new_id = students["student_id"].max() + 1
            new_row = pd.DataFrame({
            "student_id" : [new_id],
            "name" : [name],
            "class" : [cla_ss],
            "phone_no" : [phone],
            "monthly_fees" : [monthly_fees],
            "join_date" : [join_date]
            })
            students = pd.concat([students, new_row], ignore_index=True)
            students.to_csv("students.csv", index=False)
            st.success("Student Added Successfully")

elif choice == "ADD Payments":
    payments = pd.read_csv("payments.csv")
    student_id = st.number_input("Student ID", step=1)
    month = st.text_input("Month (YYYY-MM)")
    amount = st.number_input("Amount", step=500)
    if st.button("Save Payment"):
         if student_id not in students["student_id"].values:
              st.error("Student Not Found")
         else:
              payment_id = payments["payment_id"].max()+1
              pay_date = str(date.today())
              new_row = pd.DataFrame({
                   "payment_id": [payment_id],
                   "student_id": [student_id],
                   "month": [month],
                   "amount": [amount],
                   "pay_date": [pay_date]
              })
              payments = pd.concat([payments,new_row],ignore_index = True)
              payments.to_csv("payments.csv", index=False)
              st.success("Payment Added Successfully")

elif choice == "Defaulters":
     payments = pd.read_csv("payments.csv")
     month = st.text_input("month(YYYY-MM)")
     if month != "":
          paid = payments[payments["month"]==month]
          merged = students.merge(paid,on="student_id", how= "left")
          merged["amount"] = merged["amount"].fillna(0)
          defaulters = merged[merged["amount"] < merged["monthly_fees"]]

          if defaulters.empty:
               st.success("No Defaulters For This Month")
          else:
               st.dataframe(defaulters[["student_id", "name", "monthly_fees", "amount"]])
               defaulters.to_excel(f"report_{month}.xlsx", index=False)
               with open(f"report_{month}.xlsx", "rb") as f:
                    st.download_button("Download Excel", f, file_name=f"report_{month}.xlsx")

elif choice == "Monthly Summary":
     payments = pd.read_csv("payments.csv")
     month = st.text_input("Month (YYYY-MM)", key="summary_month")

     if month != "":
         paid = payments[payments["month"] == month]
         expected = students["monthly_fees"].sum()
         collected = paid["amount"].sum()
         pending = expected - collected
 
         st.metric("Expected", expected)
         st.metric("Collected", collected)
         st.metric("Pending", pending)

elif choice == "Student History":
    payments = pd.read_csv("payments.csv")
    student_id = st.number_input("Student ID", step=1, key="history_id")

    if st.button("Show History"):
        if student_id not in students["student_id"].values:
            st.error("Student Not Found")
        else:
            student = students[students["student_id"] == student_id]
            history = payments[payments["student_id"] == student_id]

            st.write("Name:", student["name"].values[0])
            st.write("Class:", student["class"].values[0])

            if history.empty:
                st.write("No payments yet")
            else:
                st.dataframe(history)
                st.write("Total Paid:", history["amount"].sum())