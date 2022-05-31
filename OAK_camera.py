from cProfile import run
import sys
import cv2
#from cv2 import VideoCapture
import depthai as dai
import time
import os
import threading
import time
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QDialog, QMainWindow, QComboBox
from matplotlib import widgets
from matplotlib.widgets import Widget
from PyQt5.QtGui import QPixmap

class OAK_camera(threading.Thread):
    ip = "192.168.1.100"
    display = None
    killed = False
    pipeline = dai.Pipeline()

    camRgb = pipeline.createColorCamera()
    manip = pipeline.createImageManip()
    xoutRgb = pipeline.createXLinkOut()

    # Properties camRgb
    camRgb.setPreviewSize(960, 512)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.setInterleaved(False)
    camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    camRgb.setFps(40)

    # Properties manip
    manip.setMaxOutputFrameSize(1474560)
    rgbRr = dai.RotatedRect()
    rgbRr.center.x, rgbRr.center.y = camRgb.getPreviewWidth() // 2, camRgb.getPreviewHeight() // 2
    rgbRr.size.width, rgbRr.size.height = camRgb.getPreviewHeight(), camRgb.getPreviewWidth()
    rgbRr.angle = -90
    manip.initialConfig.setCropRotatedRect(rgbRr, False)

    # Properties xoutRgb
    xoutRgb.setStreamName("preview")

    # Linking
    camRgb.preview.link(manip.inputImage)
    manip.out.link(xoutRgb.input)

    #generate filename
    dirname = "video"
    dt_now = time.strftime("%Y%m%d-%H%M%S")+"_"+ip.replace(".","_")
    filepath =  os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname,dt_now+".mp4")
    out = None

    device_info = None
    # overriding constructor
    def __init__(self, device_info = None, display = None):
        # calling parent class constructor
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.device_info = device_info
        self.ip = device_info.getMxId()
        self.display = display
        self.killed = False
        self.camera_config()
        self.generate_filename()

    def camera_config(self):
        
        self.pipeline = dai.Pipeline()
        self.camRgb = self.pipeline.createColorCamera()
        self.manip = self.pipeline.createImageManip()
        self.xoutRgb = self.pipeline.createXLinkOut()

        # Properties camRgb
        self.camRgb.setPreviewSize(960, 512)
        self.camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        self.camRgb.setInterleaved(False)
        self.camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        self.camRgb.setFps(40)

        # Properties manip
        self.manip.setMaxOutputFrameSize(1474560)
        rgbRr = dai.RotatedRect()
        rgbRr.center.x, rgbRr.center.y = self.camRgb.getPreviewWidth() // 2, self.camRgb.getPreviewHeight() // 2
        rgbRr.size.width, rgbRr.size.height = self.camRgb.getPreviewHeight(), self.camRgb.getPreviewWidth()
        rgbRr.angle = -90
        self.manip.initialConfig.setCropRotatedRect(rgbRr, False)

        # Properties xoutRgb
        self.xoutRgb.setStreamName("preview")

        # Linking
        self.camRgb.preview.link(self.manip.inputImage)
        self.manip.out.link(self.xoutRgb.input)
        print("Camera Configured "+self.device_info.getMxId())

    def generate_filename(self):
        #generate filename
        if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.dirname)):
            os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.dirname))
        self.dt_now = time.strftime("%Y%m%d-%H%M%S")+"_"+self.ip.replace(".","_")
        self.filepath =  os.path.join(os.path.dirname(os.path.abspath(__file__)), self.dirname,self.dt_now+".mp4")

        # delete outpy.mp4 if exist
        print("File: "+self.dt_now)
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        self.out = cv2.VideoWriter(self.filepath, cv2.VideoWriter_fourcc('m','p','4','v'), 40, (512,960))
        print("Video will be Saved in "+self.filepath)

    # define your own run method
    def run(self):
        time.sleep(3)
        with dai.Device(self.pipeline, self.device_info) as device:
            print("Recodring started, press q on frame to stop recording")
            qRgb = device.getOutputQueue('preview', maxSize=1, blocking=False)
            while True:
                frame = qRgb.get().getCvFrame()
                self.out.write(frame)
                self.image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
                self.display.setPixmap(QtGui.QPixmap.fromImage(self.image))
                cv2.imshow(self.ip, frame )
                if cv2.waitKey(1) == ord('q'):
                    break
            self.out.release()
            print("File Saved successfully: "+self.dt_now+".mp4")
            self.display.setStyleSheet("QLabel { background-color : black; }");
            cv2.destroyWindow(self.ip)
            self.stop()

    def getFilepath(self):
        return self.filepath

    def getFilename(self):
        return self.dt_now

    def stop(self):
        self.out.release()
        print("File Saved successfully: "+self.dt_now+".mp4")
        self.display.setStyleSheet("QLabel { background-color : black; }");
        self._stop_event.set()

    def stopped(self):
        print(self.ip+" stopped ->"+str(self._stop_event.is_set()))
        return self._stop_event.is_set()