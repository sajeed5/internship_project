import sys
import cv2
import numpy as np
import imutils
import pytesseract
import requests
import mysql.connector
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QLineEdit, QMessageBox, QInputDialog, QFrame, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor, QIcon
from PyQt5.QtCore import Qt, QRect, QTimer
from datetime import datetime

# MySQL database connection
mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database="sajeed", autocommit=True)
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS users (username VARCHAR(50), password VARCHAR(50))")
mycursor.execute("CREATE TABLE IF NOT EXISTS slot(carNumber VARCHAR(15), slot int)")
mycursor.execute("CREATE TABLE IF NOT EXISTS entry(carNumber VARCHAR(15), entry VARCHAR(40))")
mycursor.execute("CREATE TABLE IF NOT EXISTS exits(carNumber VARCHAR(15), exit1 VARCHAR(40))")
mycursor.execute("CREATE TABLE IF NOT EXISTS duration(carNumber VARCHAR(15), durationInSec int)")
mycursor.execute("CREATE TABLE IF NOT EXISTS cost(carNumber VARCHAR(15), cost int)")

# Initialize slots list
slots = [False for _ in range(16)]

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 400, 250)
        self.setStyleSheet("background-color: #2c3e50; color: #ecf0f1;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.label_title = QLabel("Car Parking System Login")
        self.label_title.setFont(QFont("Arial", 20, QFont.Bold))
        self.label_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_title)

        self.label_username = QLabel("Username:")
        self.label_username.setFont(QFont("Arial", 14))
        layout.addWidget(self.label_username)

        self.input_username = QLineEdit(self)
        self.input_username.setFont(QFont("Arial", 14))
        self.input_username.setStyleSheet("padding: 10px; border: 1px solid #3498db; border-radius: 5px;")
        layout.addWidget(self.input_username)

        self.label_password = QLabel("Password:")
        self.label_password.setFont(QFont("Arial", 14))
        layout.addWidget(self.label_password)

        self.input_password = QLineEdit(self)
        self.input_password.setFont(QFont("Arial", 14))
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setStyleSheet("padding: 10px; border: 1px solid #3498db; border-radius: 5px;")
        layout.addWidget(self.input_password)

        self.button_login = QPushButton('Login', self)
        self.button_login.setFont(QFont("Arial", 16, QFont.Bold))
        self.button_login.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                padding: 15px;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.button_login.clicked.connect(self.handle_login)
        layout.addWidget(self.button_login)

        self.setLayout(layout)

    def handle_login(self):
        username = self.input_username.text()
        password = self.input_password.text()
        mycursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        result = mycursor.fetchone()
        if result:
            self.close()
            self.main_window = CarParkingGUI()
            self.main_window.showFullScreen()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid credentials')

class CarParkingGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Car Parking System")
        self.setStyleSheet("background-color: #f0f0f0;")  # Set background color

        # Title label
        self.label_title = QLabel("CAR PARKING SYSTEM", self)
        self.label_title.setGeometry(50, 10, 1000, 80)
        title_font = QFont("Times New Roman", 24, QFont.Bold)
        self.label_title.setFont(title_font)
        self.label_title.setStyleSheet("color: #333;")

        # Image label
        self.label_image = QLabel(self)
        self.label_image.setGeometry(50, 70, 0, 0)
        self.label_image.setFrameShape(QFrame.Box)  # Set frame shape to Box
        self.label_image.setLineWidth(4)  # Set the width of the frame
        self.label_image.setMidLineWidth(2)  # Set the width of the mid-line of the frame

        # Upload image button
        self.button_upload = QPushButton('UPLOAD IMAGE', self)
        self.button_upload.setGeometry(50, 580, 150, 60)
        self.button_upload.setStyleSheet("background-color: #007bff; color:  #000000;font: bold; font-family: Times New Roman; font-size: 17px;")
        self.button_upload.clicked.connect(self.upload_image)

        # SLOTS label
        self.label_slots = QLabel("SLOTS", self)
        self.label_slots.setGeometry(1049, 70, 200, 50)
        self.label_slots.setFont(QFont("Arial", 18, QFont.Bold))

        # Vehicle number label and line edit
        self.label_number = QLabel("VEHICLE NO.:", self)
        self.label_number.setGeometry(50, 480, 150, 30)
        self.label_number.setFont(QFont("Times New Roman", 17, QFont.Bold))
        self.line_edit_number = QLineEdit(self)
        self.line_edit_number.setGeometry(209, 480, 200, 30)
        self.line_edit_number.setFont(QFont("Times New Roman", 16, QFont.Bold))

        # Book parking button
        self.button_book = QPushButton('BOOK PARKING', self)
        self.button_book.setGeometry(245, 580, 150, 60)
        self.button_book.setStyleSheet("background-color: #28a745; color:  #000000;font-family: Times New Roman;font: bold; font-size: 17px;")
        self.button_book.clicked.connect(self.enter_phone_number)

        # Check out slot button
        self.button_check_out_any = QPushButton('CHECK OUT SLOT', self)
        self.button_check_out_any.setGeometry(1000, 580, 200, 60)
        self.button_check_out_any.setStyleSheet("background-color: #dc3545; color: #000000;font-family: Times New Roman; font: bold; font-size: 17px;")
        self.button_check_out_any.clicked.connect(self.check_out_any_slot)

        # Logout button
        self.button_logout = QPushButton('LOGOUT', self)
        self.button_logout.setGeometry(50, 660, 150, 60)
        self.button_logout.setStyleSheet("background-color: #ff5733; color: #000000;font-family: Times New Roman; font: bold; font-size: 17px;")
        self.button_logout.clicked.connect(self.logout)

        # Slots display area   
        self.slot_labels = []
        for i in range(16):
            label_text = f"SLOT {i+1}"
            label = QLabel(label_text, self)
            label.setFont(QFont("Times New Roman", 12, QFont.Bold))
            label.setGeometry(900 + (i % 4) * 100, 130 + (i // 4) * 100, 80, 80)
            label.setAlignment(Qt.AlignCenter)
           # label.setStyleSheet("background-color: #28a745; color: #fff; border-radius: 5px;")
            self.slot_labels.append(label)

        # Initialize slots
        self.update_slots()

        # Timer for button animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.reset_button_style)

    def update_slots(self):
        for i, slot in enumerate(slots):
            color = "#dc3545" if slot else "#28a745"
            self.slot_labels[i].setStyleSheet(f"background-color: {color}; color: #fff; border-radius: 5px;")

    def upload_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Upload Image', '.', 'Image Files (*.png *.jpg *.jpeg)')
        if filename:
            pixmap = QPixmap(filename)
            #pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio)  # Increase the
            pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio)  # Increase the width to 600 pixels and height to 400 pixels
            self.label_image.setPixmap(pixmap)
            self.image_path = filename
            self.label_image.setFrameShape(QFrame.Box)  # Set frame shape to Box
            self.label_image.setLineWidth(4)  # Set the width of the frame
            self.label_image.setMidLineWidth(2)  # Set the width of the mid-line of the frame
            self.label_image.setGeometry(50, 100, pixmap.width(), pixmap.height())  # Adjust frame geometry to image size
            self.extract_number()

    def extract_number(self):
        if hasattr(self, 'image_path'):
            # Image processing to extract vehicle number
            img = cv2.imread(self.image_path, cv2.IMREAD_UNCHANGED)
            img = imutils.resize(img, width=500)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.bilateralFilter(gray, 11, 17, 17)
            edged = cv2.Canny(gray, 170, 200)
            cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:30]
            NumberPlateCnt = None
            for c in cnts:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4:
                    NumberPlateCnt = approx
                    break
           
            mask = np.zeros(gray.shape, np.uint8)
            new_image = cv2.drawContours(mask, [NumberPlateCnt], 0, 255, -1)
            new_image = cv2.bitwise_and(img, img, mask=mask)

            config = ('-l eng --oem 1 --psm 3')
            text = pytesseract.image_to_string(new_image, config=config)
            self.line_edit_number.setText(text.strip())

            # Save extracted data to CSV
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            data = {'Vehicle Number': [text.strip()], 'Timing': [current_time]}
            df = pd.DataFrame(data)
            df.to_csv('data.csv', mode='a', header=False, index=False)  # Append data to CSV

    def enter_phone_number(self):
        number, ok = QInputDialog.getText(self, 'Phone Number', 'Enter your phone number:')
        if ok:
            self.book_parking(number)

    def book_parking(self, phone_number):
        if hasattr(self, 'image_path'):
            number = self.line_edit_number.text()
            if number:
                # Check if any slots are available
                if all(slots):
                    QMessageBox.warning(self, 'Warning', 'All slots are full!')
                else:
                    # Find the first available slot
                    slot_number = next(i + 1 for i, slot in enumerate(slots) if not slot)
                    # Mark the slot as occupied
                    slots[slot_number - 1] = True

                    # Perform booking operations here (e.g., sending confirmation message)
                    url = "https://www.fast2sms.com/dev/bulkV2"
                    message = f"Your parking is confirmed. Slot number: {slot_number}. Thank you for using our service."
                    querystring = {
                        "authorization": "YOUR API KEY",
                        "message": message,
                        "language": "english",
                        "route": "q",
                        "numbers": phone_number
                    }
                    headers = {'cache-control': "no-cache"}
                    response = requests.request("GET", url, headers=headers, params=querystring)
                    print(response.text)

                    # Notify user that parking is booked
                    QMessageBox.information(self, 'Parking Booked', f'Your parking at slot {slot_number} is booked.')
                    self.update_slots()
            else:
                QMessageBox.warning(self, 'Warning', 'Please extract vehicle number first!')
        else:
            QMessageBox.warning(self, 'Warning', 'Please upload an image first!')
    def check_out_any_slot(self):
        if any(slots):
            slot_number, ok = QInputDialog.getInt(self, 'Check Out Slot', 'Enter slot number to check out:')
            if ok:
                if 1 <= slot_number <= len(slots):
                    if slots[slot_number - 1]:
                        slots[slot_number - 1] = False
                        QMessageBox.information(self, 'Checked Out', f'Slot {slot_number} is now available.')
                        self.update_slots()
                    else:
                        QMessageBox.warning(self, 'Warning', f'Slot {slot_number} is already empty.')
                else:
                    QMessageBox.warning(self, 'Warning', 'Invalid slot number.')
        else:
            QMessageBox.warning(self, 'Warning', 'No slots are occupied.')

    def logout(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    def reset_button_style(self):
        self.button_upload.setStyleSheet("background-color: #007bff; color: #000000; font: bold; font-family: Times New Roman; font-size: 17px;")
        self.button_book.setStyleSheet("background-color: #28a745; color: #000000; font: bold; font-family: Times New Roman; font-size: 17px;")
        self.button_check_out_any.setStyleSheet("background-color: #dc3545; color: #000000; font: bold; font-family: Times New Roman; font-size: 17px;")
        self.button_logout.setStyleSheet("background-color: #ff5733; color: #000000; font: bold; font-family: Times New Roman; font-size: 17px;")
        self.animation_timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.showFullScreen()
    sys.exit(app.exec_())
 
