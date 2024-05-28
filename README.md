Automated Car Parking System
This project implements an Automated Car Parking System with a graphical user interface (GUI) for managing parking slots, booking slots, and checking out. The system uses image processing to extract vehicle numbers from uploaded images and sends SMS notifications for parking confirmations.

Features
Login System:

Secure login for authorized users to access the system.
Image Upload and Processing:

Upload images of vehicle license plates.
Use OpenCV and Tesseract OCR to extract vehicle numbers from the images.
Slot Management:

Display 14 parking slots with real-time status updates.
Book available slots and check out occupied slots.
SMS Notifications:

Send SMS notifications for parking confirmations using the Fast2SMS API.
Database Integration:

Use MySQL to store user credentials, slot statuses, entry and exit times, parking durations, and costs.
Requirements
Python 3.x
OpenCV
Tesseract OCR
PyQt5
mysql-connector-python
pandas
requests
imutils

Installation
pip install opencv-python pytesseract PyQt5 mysql-connector-python pandas requests imutils

Set up the MySQL database:
CREATE DATABASE database_name;
USE database_name;
CREATE TABLE IF NOT EXISTS users (username VARCHAR(50), password VARCHAR(50));
CREATE TABLE IF NOT EXISTS slot(carNumber VARCHAR(15), slot int);
CREATE TABLE IF NOT EXISTS entry(carNumber VARCHAR(15), entry VARCHAR(40));
CREATE TABLE IF NOT EXISTS exits(carNumber VARCHAR(15), exit1 VARCHAR(40));
CREATE TABLE IF NOT EXISTS duration(carNumber VARCHAR(15), durationInSec int);
CREATE TABLE IF NOT EXISTS cost(carNumber VARCHAR(15), cost int);

Run the application:
python new.py

OUTPUT
![image](https://github.com/sajeed5/internship_project/assets/155974187/828c1d07-715c-402a-a91b-82a5b994fd58)

![image](https://github.com/sajeed5/internship_project/assets/155974187/04ddc6cb-078f-4ce7-9f00-0038a8cb87ab)

USERNAME:admin
PASSWORD:admin



