import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMainWindow
from PyQt5.QtWidgets import (QWidget, QDialog, QLabel, QPushButton,
QLineEdit, QMessageBox, QFormLayout, QVBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
import hashlib
from PyQt5.QtGui import QPixmap

import subprocess


class LoginGUI(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.initializeUI()
    def initializeUI(self):
        """Initialize the Login GUI window."""
        self.setFixedSize(400, 240)
        self.setWindowTitle("Nhận dạng khuôn mặt")
        icon = QIcon("icon\icon.png")
        self.setWindowIcon(icon)
        self.setupWindow()
    def connectToDatabase(self):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="phanloc2702",
            database="project1"
            )

# Truy vấn tên người dùng và mật khẩu từ bảng users
        mycursor = mydb.cursor()
        mycursor.execute("SELECT username, password FROM users")
        results = mycursor.fetchall()
        
        username = self.user_entry.text()
        password = self.password_entry.text()
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Kiểm tra tên người dùng và mật khẩu với dữ liệu từ MySQL
        for result in results:
            if result[0] == username and result[1] == password_hash:
                self.hide()
                subprocess.run(["python", r"C:\Users\Lenovo\PYTHON\Nhandienkhuonmat\main2.py"])

            
                return
        QMessageBox.warning(self, "Information Incorrect",
"The user name or password is incorrect.", QMessageBox.Close)    
    def setupWindow(self):
        """Set up the widgets for the login GUI."""
        header_label = QLabel("ĐĂNG NHẬP")
        header_label.setFont(QFont('Arial', 20))
        header_label.setAlignment(Qt.AlignCenter)
        
        self.user_entry = QLineEdit()
        self.user_entry.setMinimumWidth(250)
        self.password_entry = QLineEdit()
        self.password_entry.setMinimumWidth(250)
        self.password_entry.setEchoMode(QLineEdit.Password)
        # Arrange the QLineEdit widgets into a QFormLayout
        login_form = QFormLayout()
        login_form.setLabelAlignment(Qt.AlignLeft)
        
        login_form.addRow("User Login:", self.user_entry)
        login_form.addRow("Password:", self.password_entry)


        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.connectToDatabase)
        new_user_button = QPushButton("No Account?")
        new_user_button.clicked.connect(self.createNewUser)
        main_v_box = QVBoxLayout()
        main_v_box.setAlignment(Qt.AlignTop)
        main_v_box.addWidget(header_label)
        main_v_box.addSpacing(10)
        main_v_box.addLayout(login_form)
        main_v_box.addWidget(connect_button)
        main_v_box.addWidget(new_user_button)
        self.setLayout(main_v_box)
        self.show()
        
    
       
    def createNewUser(self):
        """Set up the dialog box for the user to create a new user account."""
        self.hide() # Hide the login window
        self.new_user_dialog = QDialog(self)
        self.new_user_dialog.setWindowTitle("Create New User")
        header_label = QLabel("Create New User Account")
        self.new_user_entry = QLineEdit()
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        # Arrange QLineEdit widgets in a QFormLayout
        dialog_form = QFormLayout()
        dialog_form.addRow("New User Login:", self.new_user_entry)
        dialog_form.addRow("New Password", self.new_password)
        dialog_form.addRow("Confirm Password", self.confirm_password)
        # Create sign up button
        create_acct_button = QPushButton("Create New Account")
        create_acct_button.clicked.connect(self.acceptUserInfo)
        dialog_v_box = QVBoxLayout()
        dialog_v_box.setAlignment(Qt.AlignTop)
        dialog_v_box.addWidget(header_label)
        dialog_v_box.addSpacing(10)
        dialog_v_box.addLayout(dialog_form, 1)
        dialog_v_box.addWidget(create_acct_button)
        self.new_user_dialog.setLayout(dialog_v_box)
        self.new_user_dialog.show()

    def acceptUserInfo(self):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="phanloc2702",
            database="project1"
            )

        user_name_text = self.new_user_entry.text()
        pswd_text = self.new_password.text()
        confirm_text = self.confirm_password.text()
        mycursor = mydb.cursor()
        mycursor.execute("Select * from users where username = '"+user_name_text+"'")
        results = mycursor.fetchall()
        if len(results)>0 :
            QMessageBox.warning(self, "ERROR", "User name đã tồn tại. Hãy thử lại",QMessageBox.Close)
        else:
              
        
            if pswd_text != confirm_text:
                QMessageBox.warning(self, "Error Message",
"The passwords you entered do not match. Please try again.",
QMessageBox.Close)
                self.show()
            else:
                pswd_text_hash = hashlib.sha256(pswd_text.encode('utf-8')).hexdigest() 
                sql = "INSERT INTO users (username , password) VALUES (%s, %s)"
                values = (user_name_text, pswd_text_hash)
                mycursor.execute(sql, values)
                mydb.commit()
                QMessageBox.warning(self, "Ok", "Tạo thành công user mới",QMessageBox.Close)
                self.new_user_dialog.close()
                self.show()
                
                
            return
          
                
                
        self.show()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LoginGUI()
    
    sys.exit(app.exec_())

