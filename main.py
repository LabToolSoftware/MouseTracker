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
        self.wm_title =  args[0]
        self.settings = settings.Settings()
        self.homeview = views.MainView(self,self.settings)
        self.homeview.grid()
        self.videocap = None
        self.videoview = None
        self.videocontroller = None

        self.video_open = False

        self.data = None
        self.datacontroller = None
        self.analysisview = None
        self.analysis_open = False

        self.views = {'video':self.openvideocapture,
                'webcam':self.openvideocapture,
                'analysis':self.openanalysis,
                }

    def changeview(self, view):
        if view in ['video','analysis']:
            return self.views[view](filedialog.askopenfilename())
        elif view == 'webcam':
            return self.views[view](0)

    def openvideocapture(self, source):
        if self.video_open:
            self.close()
        videocap = models.VideoCap(source,self.settings)
        self.videocap = videocap
        self.videocontroller = controllers.VideoController(self.videocap,self.settings)
        self.videoview = views.VideoView(self.videocontroller,self.settings)
        self.video_open = True
        return self.videoview

    def openanalysis(self,source):
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