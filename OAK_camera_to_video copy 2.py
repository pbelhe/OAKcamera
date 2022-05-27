#!/usr/bin/env python3

import os
from tkinter import X
import depthai as dai
import cv2
import time

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and output
camRgb = pipeline.createColorCamera()
manip = pipeline.createImageManip()
videoEnc = pipeline.createVideoEncoder()
xout = pipeline.createXLinkOut()
xout.setStreamName('h265')

# Properties camera
#camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setPreviewSize(960, 512)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
camRgb.setFps(40)

# Properties image manipulator
manip.setMaxOutputFrameSize(1474560)
rgbRr = dai.RotatedRect()
rgbRr.center.x, rgbRr.center.y = camRgb.getPreviewWidth() // 2, camRgb.getPreviewHeight() // 2
rgbRr.size.width, rgbRr.size.height = camRgb.getPreviewHeight(), camRgb.getPreviewWidth()
rgbRr.angle = 90
manip.initialConfig.setCropRotatedRect(rgbRr, False)
'''
# Linking
camRgb.video.link(videoEnc.input)
videoEnc.bitstream.link(xout.input)

# Linking cam -> manip -> videoenc -> xout
camRgb.video.link(manip.inputImage)
manip.out.link(videoEnc.input)
videoEnc.bitstream.link(xout.input)

# Linking cam -> videoenc -> manip -> xout
camRgb.video.link(videoEnc.input)
videoEnc.bitstream.link(xout.input)
depth.disparity.link(disparityOut.input)
depth.rectifiedRight.link(manip.inputImage)
manip.out.link(nn.input)
manip.out.link(manipOut.input)
nn.out.link(nnOut.input)

# Linking
camRgb.video.link(videoEnc.input)
videoEnc.bitstream.link(manip.inputImage)
manip.out.link(xout.input)
'''
# Linking
camRgb.video.link(manip.inputImage)
manip.out.link(videoEnc.input)
videoEnc.bitstream.link(xout.input)

#generate filename
dirname = "video"
if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname)):
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname))
dt_now = time.strftime("%Y%m%d-%H%M%S")
filepath =  os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname,dt_now+".h265")
frame_count = 0



device_info = dai.DeviceInfo()
device_info.state = dai.XLinkDeviceState.X_LINK_BOOTLOADER
device_info.desc.protocol = dai.XLinkProtocol.X_LINK_TCP_IP
device_info.desc.name = "192.168.1.100"

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    # Output queue will be used to get the encoded data from the output defined above
    q = device.getOutputQueue(name="h265", maxSize=30, blocking=True)
    
    batpath = open( os.path.join(os.path.dirname(os.path.abspath(__file__)), "video",dt_now+".bat"), 'w')
    batpath.write("ffmpeg -framerate 30 -i "+dt_now+".h265 -c copy "+dt_now+".mp4")
    batpath.close()

    videoFile = open(filepath, 'wb')

    # The .h265 file is a raw stream file (not playable yet)
    print("Press Ctrl+C to stop encoding...")
    try:
        while True:
            h265Packet = q.get()  # Blocking call, will wait until a new data has arrived
            h265Packet.getData().tofile(videoFile)  # Appends the packet data to the opened file
            print(" (Ctrl+C to stop) Frames saved: "+str(frame_count))
            frame_count +=1
    except KeyboardInterrupt:
        # Keyboard interrupt (Ctrl + C) detected
        videoFile.close()
        pass

    print("To view the encoded data, convert the stream file (.h265) into a video file (.mp4) using a command below:")
    print("ffmpeg -framerate 30 -i "+dt_now+".h265 -c copy "+dt_now+".mp4")
