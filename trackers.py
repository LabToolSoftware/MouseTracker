import numpy as np
import cv2 
from scipy import ndimage
from skimage.feature import peak_local_max
from skimage.morphology import watershed


class Tracker:
    def __init__(self,settings):
        self.SETTINGS = settings

    def Initialise(self,start_frame,obj_box):
        pass

    def Update(self,frame):
        return frame

class CSRTTracker(Tracker):
    def __init__(self, settings):
        Tracker.__init__(self, settings)
        self.tracker = None

    def Initialise(self,start_frame=None,obj_box=None):
        self.tracker = cv2.TrackerCSRT_create()
        self.tracker.init(start_frame,obj_box)

    def Update(self,frame):
        ret, obj_box = self.tracker.update(frame)
        if ret:
            obj_pos = (int(obj_box[0]) + int(obj_box[2]/2),
                        int(obj_box[1]) + int(obj_box[3]/2))
        return obj_pos



    
