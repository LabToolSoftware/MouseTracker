import numpy as np
import cv2 
from scipy import ndimage
from skimage.feature import peak_local_max
from skimage.morphology import watershed


class Tracker:
    def __init__(self,settings):
        self.SETTINGS = settings
        self.__obj_coords = []

    def StartTracking(self,frame, object_box):
        self.__tracker = cv2.TrackerCSRT_create()
        self.__tracker.init(frame,object_box)

    def getTracking(self):
        return self.__obj_coords

    def Track(self,frame):
        return frame

class CSRTTracker(Tracker):

    def Track(self,frame):
        ret, obj_box = self.__tracker.update(frame)
        if ret:
            obj_pos = (int(obj_box[0]) + int(obj_box[2]/2),
                        int(obj_box[1]) + int(obj_box[3]/2))
        self.__obj_coords.append(obj_pos)





    
