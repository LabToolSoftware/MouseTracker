import cv2
import numpy as np

class Settings:
    def __init__(self):
        self.__SETTINGS ={ 'height' : 480,
                    'width': 640,
                    'sensitivity': 15,
                    'hsv_min': np.array([50,50,50]),
                    'hsv_max': np.array([150,255,255]),
                    'history' : 100,
                    'threshold': 16, 
                    'shadows': False,
                    'learn_rate': -1,
                    'kshape' : cv2.MORPH_ELLIPSE,
                    'ksize' : (10,10),
                    'kmorph' : cv2.MORPH_CLOSE
                    }

    def set(self, changes):
        pass

    def getSettings(self):
        return self.__SETTINGS


