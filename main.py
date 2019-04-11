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

    def __openwebcamcapture(self):
        return self.__openvideocapture(0)

    def __openvideofile(self):
        return self.__openvideocapture(filedialog.askopenfilename())

    def __openvideocapture(self, source):
        if self.__video_open:
            self.close()
        videocap = models.VideoCap(source,self.__settings)
        self.__videocap = videocap
        self.__videocontroller = controllers.VideoController(self.__videocap,self.__settings)
        self.__videoview = views.VideoView(self.__videocontroller,self.__settings)
        self.__video_open = True
        return self.__videoview

    def __openanalysis(self):
        if self.video_open:
            self.close()
        self.data = models.DataCap(source)
        self.datacontroller = controllers.AnalysisController(self.data,self.settings)
        self.analysisview = views.AnalysisView(self.datacontroller,self.settings)
        self.analysis_open = True
        return self.analysisview
    
    def close(self):
        self.videocontroller = None
        self.videoview = None
        self.videocap.release()
        self.video_open = False
    
if __name__ == "__main__":
    app = Application(APP_TITLE)
    app.mainloop()