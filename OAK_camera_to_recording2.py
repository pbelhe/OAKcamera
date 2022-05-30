import cv2
#from cv2 import VideoCapture
import depthai as dai
import time
import os

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
if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname)):
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname))
dt_now = time.strftime("%Y%m%d-%H%M%S")
filepath =  os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname,dt_now+".mp4")

# delete outpy.mp4 if exist
if os.path.exists(filepath):
    os.remove(filepath)
out = cv2.VideoWriter(filepath, cv2.VideoWriter_fourcc('m','p','4','v'), 40, (512,960))

print("Video will be Saved in "+filepath)

device_info = dai.DeviceInfo()
device_info.state = dai.XLinkDeviceState.X_LINK_BOOTLOADER
device_info.desc.protocol = dai.XLinkProtocol.X_LINK_TCP_IP
device_info.desc.name = "192.168.1.100"

with dai.Device(pipeline) as device:
    print("Recodring started, press q on frame to stop recording")
    qRgb = device.getOutputQueue('preview', maxSize=1, blocking=False)
    while True:
        frame = qRgb.get().getCvFrame()
        out.write(frame)
        cv2.imshow("rgb", frame )
        #cv2.imshow("rgb", qRgb.get().getCvFrame() )
        if cv2.waitKey(1) == ord('q'):
            break
out.release()
print("File Saved successfully: "+dt_now+".mp4")