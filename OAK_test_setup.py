import cv2
#from cv2 import VideoCapture
import depthai as dai
import time
import os

pipeline = dai.Pipeline()

camRgb = pipeline.createColorCamera()

xoutRgb = pipeline.createXLinkOut()
xoutRgb.setStreamName("rgb")
camRgb.preview.link(xoutRgb.input)

with dai.Device(pipeline) as device:
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    while True:
        frame = qRgb.get().getCvFrame()
        cv2.imshow("rgb", frame )
        #cv2.imshow("rgb", qRgb.get().getCvFrame() )
        if cv2.waitKey(1) == ord('q'):
            break