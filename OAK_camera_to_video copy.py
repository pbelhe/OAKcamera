#!/usr/bin/env python3

import os
import depthai as dai
import cv2
import time

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and output
#camRgb = pipeline.createColorCamera()
camRgb = pipeline.create(dai.node.ColorCamera)
image_manip = pipeline.create(dai.node.ImageManip)
videoEnc = pipeline.createVideoEncoder()
xout = pipeline.createXLinkOut()

xout.setStreamName('h265')

'''
# Properties
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
videoEnc.setDefaultProfilePreset(3840, 2160, 30, dai.VideoEncoderProperties.Profile.H265_MAIN)
'''
# Properties camera
camRgb.setPreviewSize(960, 512)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
camRgb.setFps(40)

# Properties image manipulator
image_manip.setMaxOutputFrameSize(1474560)
rgbRr = dai.RotatedRect()
rgbRr.center.x, rgbRr.center.y = camRgb.getPreviewWidth() // 2, camRgb.getPreviewHeight() // 2
rgbRr.size.width, rgbRr.size.height = camRgb.getPreviewHeight(), camRgb.getPreviewWidth()
rgbRr.angle = 90
image_manip.initialConfig.setCropRotatedRect(rgbRr, False)

# Linking
camRgb.video.link(videoEnc.input)
videoEnc.bitstream.link(xout.input)

#generate filename
dirname = "video"
if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname)):
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname))
dt_now = time.strftime("%Y%m%d-%H%M%S")
filepath =  os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname,dt_now+".h265")
frame_count = 0

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    # Output queue will be used to get the encoded data from the output defined above
    q = device.getOutputQueue(name="h265", maxSize=40, blocking=True)

    batpath = open( os.path.join(os.path.dirname(os.path.abspath(__file__)), "video",dt_now+".bat"), 'w')
    batpath.write("ffmpeg -framerate 40 -i "+dt_now+".h265 -c copy "+dt_now+".mp4")
    batpath.close()

    # The .h265 file is a raw stream file (not playable yet)
    with open(filepath, 'wb') as videoFile:
        print("Press Ctrl+C to stop encoding...")
        try:
            while True:
                h265Packet = q.get()  # Blocking call, will wait until a new data has arrived
                h265Packet.getData().tofile(videoFile)  # Appends the packet data to the opened file
                print(" (Ctrl+C to stop) Frames saved: "+str(frame_count))
                frame_count +=1
        except KeyboardInterrupt:
            # Keyboard interrupt (Ctrl + C) detected
            pass

    print("To view the encoded data, convert the stream file (.h265) into a video file (.mp4) using a command below:")
    print("ffmpeg -framerate 40 -i "+dt_now+".h265 -c copy "+dt_now+".mp4")
