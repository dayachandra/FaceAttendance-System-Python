from _datetime import datetime
import os
import pickle

import cvzone
import face_recognition
import numpy as np

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL' : "https://unifaceattendance-default-rtdb.firebaseio.com/",
    'storageBucket' : "unifaceattendance.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/Background.jpg')

folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))

#print(modePathList)

print("Loading Encode File...")
file= open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentsIds = encodeListKnownWithIds
#print(studentsIds)
print("Encoded File Loaded...")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0,0), None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[233:233 + 480, 20:20 + 640] = img
    imgBackground[90:90 + 633, 835:835 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches",matches)
            # print("faceDis",faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Match index", matchIndex)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 20 + x1, 233 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentsIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
        if counter != 0:

            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                datetimeObject = datetime.strptime(studentInfo['Last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondElapsed)
                if secondElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['Total_attendance'] += 1
                    ref.child('Total_attendance').set(studentInfo['Total_attendance'])
                    ref.child('Last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[90:90 + 633, 835:835 + 414] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                    imgBackground[90:90 + 633, 835:835 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['Total_attendance']), (900, 175),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['Name']), (1080, 175),
                                cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 0), 1)
                    cv2.putText(imgBackground, str(id), (1060, 548),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['Major']), (1060, 624),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['Starting_year']), (950, 700),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1)
                    cv2.putText(imgBackground, str(studentInfo['Year']), (1180, 700),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1)

                    imgBackground[255:255 + 216, 938:938 + 216] = imgStudent

            counter += 1

            if counter >= 20:
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[90:90 + 633, 835:835 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0

# cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
