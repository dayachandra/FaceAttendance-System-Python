import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL' : "https://unifaceattendance-default-rtdb.firebaseio.com/"
})

ref = db.reference("Students")

data = {
    "001":
        {
            "Name" : "Elon Musk",
            "Major" : "ICT",
            "Starting_year":2020,
            "Total_attendance" : 6,
            "Standing" : "G",
            "Year" : 3,
            "Last_attendance_time": "2023-08-09 00:54:34"
        },
    "002":
        {
            "Name": "Zukerburk",
            "Major": "ET",
            "Starting_year": 2019,
            "Total_attendance": 10,
            "Standing": "Automobile",
            "Year": 4,
            "Last_attendance_time": "2023-08-09 00:54:34"
        },
    "003":
        {
            "Name": "Bill Gates",
            "Major": "BST",
            "Starting_year": 2021,
            "Total_attendance": 6,
            "Standing": "G",
            "Year": 2,
            "Last_attendance_time": "2023-08-09 00:54:34"
        },
    "004":
        {
            "Name": "Danushka",
            "Major": "ICT",
            "Starting_year": 2020,
            "Total_attendance": 0,
            "Standing": "G",
            "Year": 3,
            "Last_attendance_time": "2023-08-09 00:54:34"
        }
}

for key,value in data.items():
    ref.child(key).set(value)