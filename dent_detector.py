import os
from posixpath import dirname
import cv2
import depthai as dai
import numpy as np
import time
import logging as log

from pathlib import Path
from threading import Thread

# Initialise log instance
#log.basicConfig(filename='log.log', level=log.INFO, format='%(asctime)s %(levelname)s: %(message)s')

class DentsDetector:
    video_writer = None

    def __init__(self, preview=True):
        # Initiate variables
        self.preview = preview
        self.frame = None
        self.detection_list = []

        self.online = False

        # Create pipeline
        self.pipeline = dai.Pipeline()

        # Define sources and outputs
        camera_rgb = self.pipeline.create(dai.node.ColorCamera)
        image_manip = self.pipeline.create(dai.node.ImageManip)
        preview_out = self.pipeline.create(dai.node.XLinkOut)
        
        preview_out.setStreamName('preview')

        # Properties camera
        camera_rgb.setPreviewSize(960, 512)
        camera_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        camera_rgb.setInterleaved(False)
        camera_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        camera_rgb.setFps(40)

        # Properties image manipulator
        image_manip.setMaxOutputFrameSize(1474560)
        rgbRr = dai.RotatedRect()
        rgbRr.center.x, rgbRr.center.y = camera_rgb.getPreviewWidth() // 2, camera_rgb.getPreviewHeight() // 2
        rgbRr.size.width, rgbRr.size.height = camera_rgb.getPreviewHeight(), camera_rgb.getPreviewWidth()
        rgbRr.angle = 90
        image_manip.initialConfig.setCropRotatedRect(rgbRr, False)
        
        # Linking
        camera_rgb.preview.link(image_manip.inputImage)
        image_manip.out.link(preview_out.input)

        # Create a video writer
        dirname = "video2"
        dt_now = time.strftime("%Y%m%d-%H%M%S")
        filepath =  os.path.join(os.path.dirname(os.path.abspath(__file__)), dirname,dt_now+".mp4")
        if Path(filepath).exists():
            os.remove(filepath)
        self.video_writer = cv2.VideoWriter(filepath, cv2.VideoWriter_fourcc('m','p','4','v'), camera_rgb.getFps(), (camera_rgb.getPreviewHeight(),camera_rgb.getPreviewWidth()))
    
    def start(self):
        # Initialize the thread
        thread = Thread(target=self._run, args=())
        thread.daemon = False
        
        print('[Info] Loading camera...')
        thread.start()
        time.sleep(30)
        print('[Info] Camera loading completed')
        
        return self
    
    def _run(self):

        while True:
            # Initiate main loop
            print('[Info] Attempting camera connection...')

            try:
                # Connect to device and start pipeline
                with dai.Device(self.pipeline) as device:
                    time.sleep(5)
                    log.info('Camera correctly conected and online')
                    print('[Info] Camera correctly conected')

                    self.online = True

                    # Output queues
                    preview_queue = device.getOutputQueue('preview', maxSize=1, blocking=False)

                    startTime = time.monotonic()
                    counter = 0

                    if self.preview:
                        def frameNorm(frame, bbox):
                            normVals = np.full(len(bbox), frame.shape[0])
                            normVals[::2] = frame.shape[1]
                            return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

                        def displayFrame(name, frame, fps_text):
                            cv2.putText(frame, fps_text, (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, (255, 255, 255))
                            
                            colors = [(0, 255, 0), (0, 255, 255), (0, 0, 255)]
                            # Store and Show the frame
                            self.video_writer.write(frame)
                            cv2.imshow(name, frame)

                    while True:
                        try:
                            preview_frame = preview_queue.get()
                        except:
                            print('[Info] Frame missed')
                            #log.warning('Camera frame missed')
                            detections = None
                            preview_frame = None
                            break
                        
                        if preview_frame is not None:
                                self.frame = preview_frame.getCvFrame()
                                counter += 1
                        
                        fps_text = 'NN fps: {:.2f}'.format(counter / (time.monotonic() - startTime))
                        print(fps_text)                       
                        
                        if self.preview:    
                            if self.frame is not None:
                                frame_detections = self.frame.copy()
                                displayFrame('Preview', frame_detections, fps_text)
                                cv2.waitKey(1)
                    
                    self.video_writer.release()
                    print("released")

            except:
                print('[Info] Camera connection error')
                #log.warning('Camera connection error, attempting reconnection')

                self.online = False

                time.sleep(15)

    def is_online(self):
        return self.online

    def take_detection(self):
        return self.frame, self.detection_list

DentsDetector().start()