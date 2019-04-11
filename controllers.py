import tkinter as tk
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import cv2
import detectors
import trackers

class ViewController():

    def __init__(self, views):
        self.__views = views
        self.__current_view 

    def setView(self, view):
        if view in self.__views:
            self.__current_view = view
        else:
            print(view + 'not found')

    def getView(self):
        return self.__current_view

class VideoController():
    
    self.__detectors = {'original':detectors.Detector(self.SETTINGS),
                        'colour': detectors.ColourDetector(self.SETTINGS),
                        'colourdiff': detectors.ColourDiffDetector(self.SETTINGS),
                        'difference':detectors.DiffDetector(self.SETTINGS),
                        'background':detectors.BackgroundSubDetector(self.SETTINGS),
                        'watershed': detectors.WatershedDetector(self.SETTINGS),
                        }

    self.__trackers = {'csrt': trackers.CSRTTracker(self.SETTINGS),
                        }

    def __init__(self, stream, settings):

        self.__SETTINGS = settings.getSettings()
        self.__videocap = stream
        self.__videowriter = None

        
        self.__detector = self.detectors['original']

        self.__framenum = stream.getFrame()
        print(str(self), ' created...')
        self.video_source = videocap.__getattribute__('video_source')
        self._num_frames = videocap.__getattribute__('_num_frames')
        
        self.__isrunning = True
        self.__istracking = False
        self.__isrecording = False
        self.__bboxes = {'stage':[(0,0,self.__SETTINGS['width'],self.__SETTINGS['height'])],'ROI':[],'Obj':[(0,0,0,0)]}
        self.__track = []
        self.__current_frame = self.GetFrame(0)

    def setBox(self,boxtype,coords):

        if boxtype == 'ROI':
            self.bboxes['ROI'].append(coords)
        else:
            self.bboxes[boxtype][0] = coords
        print(self.bboxes)

    def setDetector(self,detector):
        self.detector = self.detectors[detector]

    def StartTracking(self,tracker):
        
        self.tracker = self.trackers[tracker]
        obj = self.bboxes['Obj'][0]
        box = (obj[0],
                obj[1],
                obj[2]-obj[0],
                obj[3]-obj[1])
        self.tracker.Initialise(start_frame=self.current_frame,obj_box=box)
        self._istracking = True
        print('Started Tracking...')
                                              
    def DrawBoxes(self,frame):
        colour=None
        for bbox,rects in self.bboxes.items():
            if bbox == 'stage':
                if rects:
                    colour = (0,0,255)
                    cv2.rectangle(frame, (rects[0][0],rects[0][1]),(rects[0][2],rects[0][3]),colour, thickness=2)
            elif bbox == 'Obj':
                if rects:
                    colour = (0,255,0)
                    cv2.rectangle(frame, (rects[0][0],rects[0][1]),(rects[0][2],rects[0][3]),colour, thickness=2)
        for point in self.track[-10:-1]:
            cv2.circle(img=frame, 
            center = (point[0],point[1]), 
            radius=1,
            color=(255,0,0),
            thickness=2)
        return frame

    def getNextFrame(self):
        ret, frame = self.videocap.get_frame()
        fg_frame = None
        if ret:
            
            self.current_frame = frame.copy()
            fg_frame = self.detector.detect_frame(frame)

            if self._istracking:
                coords = self.tracker.Update(fg_frame)
                self.track.append(coords)
                print('Object coordinates: ' + str(self.track[-1]))    
                box_frame = self.DrawBoxes(frame)
            else:
                box_frame = frame

            if self._isrecording:
                self.videowriter.write(cv2.cvtColor(box_frame,cv2.COLOR_BGR2RGB))

            return box_frame,fg_frame

    def getFrame(self, framenum=0,bboxes=None):
        self.videocap.set_frame(framenum)
        ret, frame = self.videocap.get_frame()
        if ret:
            self.current_frame = frame.copy()
            return frame    

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.backends.backend_tkagg as tkagg
import seaborn as sns

class AnalysisController:
    def __init__(self, source,settings):
        self.bboxes = {}
        self.SETTINGS = settings.SETTINGS
        self.data_source = source  
        self.trace = pd.DataFrame(np.asarray(tuple(self.data_source.track_coords)),columns=["x", "y"]) 

    def GetPlot(self, type_='original',master=None):
        Fig = matplotlib.figure.Figure(figsize=(5,4),dpi=100)
        ax = Fig.add_subplot(111)
        ax.plot(self.trace['x'],self.trace['y'])
        ax.set_ylim(0,self.SETTINGS['height'])
        ax.set_xlim(0,self.SETTINGS['width'])
        ax.invert_yaxis()
        canvas_plot = tkagg.FigureCanvasTkAgg(Fig,master=master)
        canvas_plot.draw()
        return canvas_plot.get_tk_widget()

    def GenerateHeatMap(self):
        number_of_bins = 100
        min_x = 0
        max_x = self.SETTINGS['width']
        min_y = 0
        max_y = self.SETTINGS['height']
        heatmap, xedges, yedges = np.histogram2d(self.trace['y'], self.trace['x'], bins=number_of_bins,range=[[min_x, max_x], [min_y, max_y]],density=True)
        plt.imshow(heatmap)
        plt.show()
        return heatmap