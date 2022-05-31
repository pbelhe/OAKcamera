import threading
import time
from OAK_camera import OAK_camera 
import depthai as dai

threadLock = threading.Lock()
threads = []

for device in dai.Device.getAllAvailableDevices():
    print(f" configuring {device.getMxId()} {device.state}")
    device_info = dai.DeviceInfo()
    device_info.state = dai.XLinkDeviceState.X_LINK_BOOTLOADER
    device_info.desc.protocol = dai.XLinkProtocol.X_LINK_TCP_IP
    device_info.desc.name = device.getMxId()
    thread = OAK_camera(device_info,None)
    thread.start()
    threads.append(thread)

for t in threads:
    t.join()
print("Exiting Main Thread")
input("Press enter to exit..")