from asyncio.windows_events import NULL
from re import T
import sys
import threading 
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
from OAK_camera import OAK_camera

#Dashboard screen
class Dashboard(QMainWindow):
    cameraAction = None
    threadLock = threading.Lock()
    devices = []
    threads = []

    def __init__(self):
        super(Dashboard, self).__init__()
        loadUi("gui.ui", self)
        self.setStatus("Initiating, please wait")
        time.sleep(3)
        self.initUI()
        self.cam1_btn.clicked.connect(self.cam1Action)
        self.cam2_btn.clicked.connect(self.cam2Action)
        self.stop_btn.clicked.connect(self.stopAction)
        self.detect_btn.clicked.connect(self.detectAction)

    def initUI(self):
        self.devices = []
        self.threads = []
        for device in dai.Device.getAllAvailableDevices():
            device_info = dai.DeviceInfo()
            device_info.state = dai.XLinkDeviceState.X_LINK_BOOTLOADER
            device_info.desc.protocol = dai.XLinkProtocol.X_LINK_TCP_IP
            device_info.desc.name = device.getMxId()
            self.devices.append(device_info)
            self.threads.append(None)
        if(len(self.devices) == 0):
            self.setStatus("No devices found")
        elif(len(self.devices) == 1):
            self.setStatus("Found "+str(len(self.devices))+" devices")
            self.ip1_text.setText(self.devices[0].getMxId())
            self.threads[0] = OAK_camera(self.devices[0],self.frame1)
        elif(len(self.devices) >= 2):
            self.setStatus("Found "+str(len(self.devices))+" devices")
            self.ip1_text.setText(self.devices[0].getMxId())
            self.ip2_text.setText(self.devices[1].getMxId())
            self.threads[0] = OAK_camera(self.devices[0],self.frame1)
            self.threads[1] = OAK_camera(self.devices[1],self.frame2)
        
    def cam1Action(self):
        if (len(self.threads) > 0):
            self.threads[0] = OAK_camera(self.devices[0],self.frame2)
            thread = self.threads[0]
            while thread.stopped() is False:
                    time.sleep(0.1)
                    thread.stop()
            thread.start()
            self.setStatus("Started "+thread.getFilename())
        else:
            self.setStatus("No devices found")   
        
    def cam2Action(self):
        if (len(self.threads) > 1):
            self.threads[1] = OAK_camera(self.devices[1],self.frame2)
            thread = self.threads[1]
            #stop current thread and start new
            while thread.stopped() is False:
                    time.sleep(0.1)
                    thread.stop()
            thread.start()
            self.setStatus("Started "+thread.getFilename())
        else:
            self.setStatus("No devices found")  
        
    def stopAction(self):
        for thread in self.threads:
            while thread.stopped() is False:
                time.sleep(0.1)
                thread.stop()
            self.setStatus("Stopped "+thread.getFilename())
        
    def cam3Action(self):
        action = self.cam2_btn.text()
        if (len(self.threads) > 1):
            thread = self.threads[1]
            if action == "Start":
                if thread.stopped():
                    thread.start()
                    while thread.stopped() is True:
                        time.sleep(0.1)
                        thread.start()
                    self.cam2_btn.setText("Stop")
                    self.setStatus("Started "+thread.getFilename())
            if action == "Stop":
                while thread.stopped() is False:
                    time.sleep(0.1)
                    thread.stop()
                    self.cam2_btn.setText("Start")
                    self.setStatus("Stopped "+thread.getFilename())
        else:
            self.setStatus("No devices found")        

    def detectAction(self):
        text = self.filename_text.text()
        if (len(text) >= 19 and text.endswith(".mp4")):
            self.setStatus("Detecting "+text)
        else:
            self.setStatus("Please enter valid filename..")

    #getters and setters
    def setStatus(self,status):
        self.status_label.setText(str(status)) 
    def setIp1Text(self,ip):
        self.ip1_text.setText(str(ip))
    def setIp2Text(self,ip):
        self.ip1_text.setText(str(ip))
    def getIp1Text(self):
        return self.ip1_text.text()
    def getIp2Text(self):
        return self.ip2_text.text()
    
    # End click through buttons functions

#delete all files in "video" folder
def delete_files(dir = "video"):
    for the_file in os.listdir(dir):
        file_path = os.path.join(dir, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
delete_files()

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
