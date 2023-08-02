import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime


path ="pic"
images = []
classNames= []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f"{path}/{cl}")
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
    
def maHoa(images):
    encodeList=[]
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnow = maHoa(images) 
print("ma hoa thanh cong")
print(len(encodeListKnow))


            
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    framS= cv2.resize(frame ,(0,0),None, fx =0.5,fy=0.5 )
    framS = cv2.cvtColor(framS, cv2.COLOR_BGR2RGB)
    facecurFrame=face_recognition.face_locations(framS)
    encodecurFrame= face_recognition.face_encodings(framS)

    for encodeFace, faceLoc in zip(encodecurFrame, facecurFrame):
        matches = face_recognition.compare_faces(encodeListKnow, encodeFace)
        faceDis= face_recognition.face_distance(encodeListKnow, encodeFace)
        matchIndex=np.argmin(faceDis)
        
        
        if faceDis[matchIndex] <0.50:
            name = classNames[matchIndex].upper()
           
        else:
            name = "Unknown"
            
        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 =  y1*2, x2*2, y2*2, x1*2
        cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,0),2)
        cv2.putText(frame,name,(x2,y2),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
    
    cv2.imshow('Loc', frame)
    if cv2.waitKey(1)== ord("q"):
        break
    
cap.release()
cv2.destroyAllWindows()
           