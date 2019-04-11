import tkinter as tk 
from tkinter import filedialog, HORIZONTAL
import cv2
import numpy as np
import views
import models
import settings
import filters
import controllers


APP_TITLE = 'MouseTracker v0.1'


class Application(tk.Tk):

    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)

        self.__views = {'video':self.__openvideofile,
                'webcam':self.__openwebcamcapture,
                'analysis':self.__openanalysis
                }

        self.__wm_title =  args[0]
        self.__settings = settings.Settings()
        self.__homeview = views.MainView(self,self.__settings)
        self.__homeview.grid()
        self.__videocap = None
        self.__viewcontroller = controllers.ViewController()
        self.__videocontroller = None

        self.__video_open = False

        self.__data = None
        self.__datacontroller = None
        self.__analysisview = None
        self.__analysis_open = False

    def set_view(self, view):
        if view in self.__views.keys():
            return self.__views[view]()
    
    def close(self):
        self.videocontroller = None
        self.videoview = None
        self.videocap.release()
        self.video_open = False
    
if __name__ == "__main__":
    app = Application(APP_TITLE)
    app.mainloop()