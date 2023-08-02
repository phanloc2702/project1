import typing
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
import os
import sys
import time
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
import hashlib
import face_recognition
import cv2
import sys
import mysql.connector
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from datetime import datetime

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    change_label_signal=pyqtSignal(str,str,str,str)
    change_timelabel_signal=pyqtSignal(str)
    handle_attendance_success= pyqtSignal()
    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # capture from web cam
        def maHoa(images):
            encodeList=[]
            for img in images:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encode= face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            return encodeList
        path = "Nhandienkhuonmat\pic"
        images = []
        classNames=[]
        myList= os.listdir(path)
        print(myList)
        for cl in myList:
            curImg = cv2.imread(f"{path}/{cl}")
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])
        encodeListKnow = maHoa(images)
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, cv_img = cap.read()
            
            if ret:
                framS= cv2.resize(cv_img ,(0,0),None, fx =0.5,fy=0.5 )
                framS = cv2.cvtColor(framS, cv2.COLOR_BGR2RGB)
                facecurFrame=face_recognition.face_locations(framS)
                encodecurFrame= face_recognition.face_encodings(framS)
                for encodeFace, faceLoc in zip(encodecurFrame, facecurFrame):
                        matches = face_recognition.compare_faces(encodeListKnow, encodeFace)
                        faceDis= face_recognition.face_distance(encodeListKnow, encodeFace)
                        matchIndex=np.argmin(faceDis)
                        print(faceDis)
                        print(matchIndex)
                        

                        if faceDis[matchIndex] <0.50:
                            name = classNames[matchIndex].upper()
                            mydb = mysql.connector.connect(
                                host="localhost",
                                user="root",
                                password="phanloc2702",
                                database="project1"
                                )
                            mycursor2 = mydb.cursor()
                            mycursor2.execute("Select * from diem_danh where MSSV = '"+name+"'")
                            MSSV = mycursor2.fetchall()
                            if len(MSSV) == 0:
                                current_time = datetime.now()
                                addMSSV = "INSERT INTO diem_danh (MSSV,TIME) VALUES (%s, %s)"
                                values = (name,current_time)
                                mycursor2.execute(addMSSV, values)
                                mydb.commit()
                                self.handle_attendance_success.emit()
                            else:
                                print("Đã tồn tại")
                                
                                mycursor3=mydb.cursor()
                                mycursor3.execute("Select NAME, MSSV, SUBJECT, CLASS from sinh_vien where MSSV = '"+name+"'")
                                
                                results = mycursor3.fetchall()
                                
                                mycursor4=mydb.cursor()
                                mycursor4.execute("Select TIME from diem_danh where MSSV = '"+name+"' ")
                                ketqua=mycursor4.fetchone()
                                for result in results:
                                    ten=result[0]
                                    mssv = result[1]
                                    mon = result[2]
                                    lop = result[3]
                                    self.change_label_signal.emit(ten,mssv,mon,lop)   
                                if len(ketqua) >0:
                                    
                                    ketqua2=ketqua[0].strftime("%Y-%m-%d %H:%M:%S")
                                    self.change_timelabel_signal.emit(ketqua2)
                                else:
                                    print("Điểm danh thành công")
                        else:
                            name = "Unknown"

                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 =  y1*2, x2*2, y2*2, x1*2
                        cv2.rectangle(cv_img, (x1,y1),(x2,y2),(0,255,0),2)
                        cv2.putText(cv_img,name,(x2,y2),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                
                self.change_pixmap_signal.emit(cv_img)
               
                
        # shut down capture system
        cap.release()
        
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # kích thước, màu background, tên window
        self.setGeometry(100,100,800,600)       
        self.setStyleSheet("background: lightgrey;")
        self.setWindowTitle("ĐIỂM DANH SINH VIÊN")
        self.disply_width = 640
        self.display_height = 480
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('Webcam')
        
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout=QHBoxLayout(main_widget)
        
        camera_group_box = QGroupBox("Camera Viewfinder")
        camera_layout= QVBoxLayout()
        camera_layout.addWidget(self.image_label)
        camera_layout.addWidget(self.textLabel)
        self.viewfinder= QCameraViewfinder()
        camera_layout.addWidget(self.viewfinder)
        
        camera_group_box.setLayout(camera_layout)
       
        layout.addWidget(camera_group_box)
        
        user_group_box = QGroupBox("THÔNG TIN SINH VIÊN")
        user_layout = QGridLayout()
        self.thread = VideoThread()
        self.namelb= QLabel()
        self.mssvlb=QLabel()
        self.loplb=QLabel()
        self.monlb=QLabel()
        self.timelb=QLabel()
        user_layout.addWidget(QLabel("HỌ VÀ TÊN:"), 0, 0)
        user_layout.addWidget(self.namelb, 0, 1)
        user_layout.addWidget(QLabel("MSSV: "), 1, 0)
        user_layout.addWidget(self.mssvlb, 1, 1)
        user_layout.addWidget(QLabel("LỚP:"), 2, 0)
        user_layout.addWidget(self.loplb, 2, 1)
        user_layout.addWidget(QLabel("MÔN HỌC:"), 3, 0)
        user_layout.addWidget(self.monlb, 3, 1)
        user_layout.addWidget(QLabel("THỜI GIAN:"), 4, 0)
        user_layout.addWidget(self.timelb, 4, 1)
        user_group_box.setLayout(user_layout)
        layout.addWidget(user_group_box)
        
        # create the video capture thread
        
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.change_label_signal.connect(self.update_label)
        self.thread.change_timelabel_signal.connect(self.update_label2)
        self.thread.handle_attendance_success.connect(self.handle_attendance_success)
        # start the thread
        self.thread.start()
        self.show()
    
    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def update_label(self,ten,mssv,mon,lop):
        
            self.namelb.setText(ten)
            self.mssvlb.setText(mssv)
            self.monlb.setText(mon)
            self.loplb.setText(lop)
    def update_label2(self, time):
            
            self.timelb.setText(time)   
    
    def handle_attendance_success(self):
        
        QMessageBox.information(self, "Thông báo", "Điểm danh thành công!")
if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(App.exec())