from asyncio.windows_events import NULL
from re import T
import sys 
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QDialog, QMainWindow, QComboBox
from matplotlib import widgets
from matplotlib.widgets import Widget
from PyQt5.QtGui import QPixmap
import cv2
#from cv2 import VideoCapture
import depthai as dai
import time
import os

# Camera Setup
pipeline = dai.Pipeline()

camRgb = pipeline.createColorCamera()

xoutRgb = pipeline.createXLinkOut()
xoutRgb.setStreamName("rgb")
camRgb.preview.link(xoutRgb.input)

#Dashboard screen
class Dashboard(QMainWindow):
    cameraAction = None
    def __init__(self):
        super(Dashboard, self).__init__()
        loadUi("gui.ui", self)
        self.setStatus("Initiating, please wait")
        time.sleep(3)
        self.setStatus("Initiated")
        self.test_btn.clicked.connect(self.testAction)
        self.record_btn.clicked.connect(self.recordAction)
        self.detect_btn.clicked.connect(self.detectAction)

    # Click through buttons functions
    def testAction(self):
        self.setStatus("Initiating Testing...")
        if self.isRunning() is not None:
            self.setStatus("Camera is " + self.isRunning())  # testing/recording/detecting
        else:
            self.isRunning("Testing")                       # lock for testing
            self.setStatus("Initiating Testing")
            time.sleep(3)
            os.system("start /wait cmd /c python OAK_test_setup.py")
            time.sleep(3)
            self.isRunning(None) 
            self.setStatus("Testing Stopped")

    def recordAction(self):
        self.setStatus("Initiating Recording...")
        if self.isRunning() is not None:
            self.setStatus("Camera is " + self.isRunning())  # testing/recording/detecting
        else:
            # lock for recording
            self.isRunning("Recording")
            self.setStatus("Initiating Recording")
            time.sleep(3)
            self.setStatus("Initiating Recording..")
            os.system("start /wait cmd /c python OAK_camera_to_video.py")
            time.sleep(3)
            self.isRunning(None) 
            self.setStatus("Recording Stopped")
        

    def detectAction(self):
        self.setStatus("Initiating Detection...")
        if self.isRunning() is not None:
            self.setStatus("Camera is " + self.isRunning())  # testing/recording/detecting
        else:
            # lock for detection
            self.isRunning("Detecting")
            self.setStatus("Initiating Detection")
            time.sleep(3)
            text = self.filename_text.text()
            if (len(text) == 19 and text.endswith(".mp4")):
                filename = text.replace(".mp4","")
                self.setStatus("Detecting "+text)
                cmd = "ffmpeg -framerate 30 -i "+filename+".h265 -c copy "+filename+".mp4"
                os.chdir("video")
                os.system("start /wait cmd /c "+cmd)
                os.chdir("..")
                self.setStatus("Processed "+text)
            else:
                self.setStatus("Please enter valid filename..")
            self.isRunning(None) 

    # Helper functions
    def isRunning(self,status = NULL):
        if status is not NULL:
            self.cameraAction = status
        if self.cameraAction is not None:
            self.label_7.setPixmap(QtGui.QPixmap("hmi-images/online.png"))
        else:
            self.label_7.setPixmap(QtGui.QPixmap("hmi-images/offline.png"))
        return self.cameraAction

    def setStatus(self,status):
        self.label_2.setText(str(status)) 
    # End click through buttons functions

# Main 
app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
dashboard = Dashboard()
widget.addWidget(dashboard)
widget.setFixedHeight(768)
widget.setFixedWidth(1366)
widget.show()

try: 
    sys.exit(app.exec_())
except:
    print("Exiting")
