# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Performs continuous object detection with the camera.

"""

import argparse
import platform
import numpy as np
import cv2
import time
from PIL import Image
import os.path
# from edgetpu.detection.engine import DetectionEngine

from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.edgetpu import run_inference


from threading import Thread, Timer
from pubsub import pub
import time

# Function to read labels from text files.
def ReadLabelFile(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    label = {}
    for line in lines:
        pair = line.strip().split(maxsplit=1)
        label[int(pair[0])] = pair[1].strip()
    return label
        
class Vision:
    # seconds before changing to each mode (to stop constant switching)
    mode_change_thresholds = {
        'object': 5,
        'face': 2
    }
        
    def __init__(self, **kwargs):
        self.preview = kwargs.get('preview', False)
        
        self.label_file = os.path.dirname(os.path.realpath(__file__)) + '/../../resources/model/coco_labels.txt'
        self.model_file = os.path.dirname(os.path.realpath(__file__)) + '/../../resources/model/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
        self.last_mode_change_time = None
        
        self.set_mode(kwargs.get('mode', 'object')) # intial mode, will switch dynamically during use
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, 20)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        self.interpreter = make_interpreter(self.model_file)
        self.interpreter.allocate_tensors()
        # labels = read_label_file(args.labels)
        self.inference_size = input_size(self.interpreter)

        self.labels = ReadLabelFile(self.label_file) if self.label_file else None

        if self.preview:
            cv2.namedWindow('preview', cv2.WINDOW_AUTOSIZE)

        self.new_thread = Thread(target=self.vision_thread)        
        self.new_thread.start()
        self.mode_change_delay = None
        
        pub.subscribe(self.exit, 'exit')
        pub.subscribe(self.vision_mode, 'vision_mode')

    def append_objs_to_img(self, cv2_im, inference_size, objs, labels):
        height, width, channels = cv2_im.shape
        scale_x, scale_y = width / inference_size[0], height / inference_size[1]
        for obj in objs:
            bbox = obj.bbox.scale(scale_x, scale_y)
            x0, y0 = int(bbox.xmin), int(bbox.ymin)
            x1, y1 = int(bbox.xmax), int(bbox.ymax)

            percent = int(100 * obj.score)
            label = '{}% {}'.format(percent, labels.get(obj.id, obj.id))

            cv2_im = cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
            cv2_im = cv2.putText(cv2_im, label, (x0, y0+30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
        return cv2_im

    def set_mode(self, mode):
        # pub.sendMessage('log', msg="[Vision] Attempting mode change {}".format(mode))

        # if last change is greater than threshold, then change mode
        if self.last_mode_change_time is not None and time.time() - self.last_mode_change_time < self.mode_change_thresholds[mode]:
            return
        
        pub.sendMessage('log', msg="[Vision] Changing mode to {}".format(mode))
        self.mode = mode
        self.last_mode_change_time = time.time()

    def vision_mode(self, arg1):
        print("mode changed: " + arg1)
        # if(arg1 == 'start'):
        #     self.new_thread.
        pass


    def exit(self):
        self.new_thread.join()
        
    def debounce(self, mode, delay=10):
        if self.mode_change_delay is not None and self.mode_change_delay.is_alive():
            return
        self.mode_change_delay = Timer(delay, self.set_mode, [mode])
        self.mode_change_delay.start()

    def vision_thread(self):
        framecount = 0
        time1 = 0
        time2 = 0
        detectframecount = 0        

        while 1:
            t1 = time.perf_counter()
            ret, color_image = self.cap.read()
            prepimg = color_image[:, :, ::-1].copy()
            prepimg = cv2.resize(prepimg, self.inference_size)
            

            tinf = time.perf_counter()
            run_inference(self.interpreter, prepimg.tobytes())
            detectResults = get_objects(self.interpreter, 0.5)[:10]
            # print(time.perf_counter() - tinf, "sec")
            # if len(detectResults) > 0:
            #     if self.mode == 'object':
            #         pub.sendMessage('vision:detect:object', name='unknown') #, name=self.labels[objects[0].id])
            #     else:
            #         if self.mode_change_delay is not None:
            #             self.mode_change_delay.cancel()
            #             self.mode_change_delay = None
            #         pub.sendMessage('vision:detect:face', name="unknown") # @todo face recognition (from opencv module)
            #     pub.sendMessage('vision:matches', matches=objects, labels=self.labels)
            #     # if any detected objects contains 'person' then set_mode to 'face'
            #     if self.mode == 'object':
            #         for object in objects:
            #             if self.labels is not None and object.id in self.labels and self.labels[object.id] == 'person':
            #                 self.set_mode('face')
            #                 break
            # else:
            #     pub.sendMessage('vision:nomatch')
            #     # if no faces detected, go back to object detection
            #     if self.mode == 'face':
            #         self.debounce('object')
            

            if self.preview:
                frameBuffer = self.append_objs_to_img(color_image, self.inference_size, detectResults, self.labels)            
                cv2.namedWindow('preview', cv2.WINDOW_AUTOSIZE)
                cv2.imshow('preview', color_image)
                cv2.waitKey(1)

            for obj in detectResults:
                if obj.id == 0:#person
                    height, width, channels = color_image.shape
                    scale_x, scale_y = width / self.inference_size[0], height / self.inference_size[1]

                    bbox = obj.bbox.scale(scale_x, scale_y)
                    x0, y0 = int(bbox.xmin), int(bbox.ymin)
                    x1, y1 = int(bbox.xmax), int(bbox.ymax)                    
                    pub.sendMessage('detectHuman', bb=(x0,y0,x1,y1), ratio=((x0+x1)/2/width, (y0+y1)/2/height))
                    # print("pub results:\t {}\t{}\t{}\t{}".format(str(x0),str(y0),str(y0),str(x1)))
                    # print("pub results:\t {}\t{}".format(str((x0+x1)/2/width),str((y0+y1)/2/height)))
                    break                

            # FPS calculation
            framecount += 1
            if detectResults:
                detectframecount += 1
            if framecount >= 15:
                fps       = "(Playback) {:.1f} FPS".format(time1/15)
                detectfps = "(Detection) {:.1f} FPS".format(detectframecount/time2)
                framecount = 0
                detectframecount = 0
                time1 = 0
                time2 = 0
                print(detectfps)
            t2 = time.perf_counter()
            elapsedTime = t2-t1
            time1 += 1/elapsedTime
            time2 += elapsedTime
            


if __name__ == '__main__':

    
    vision = Vision(preview=True)

    from pubsub import pub
    pub.sendMessage('vision_mode', arg1='start')
    
    print("runing")

    