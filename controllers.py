import tkinter as tk
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import cv2
import detectors
import trackers

class VideoController():
    
    def __init__(self, videocap, settings):

        self.SETTINGS = settings.SETTINGS
        self.videocap = videocap
        self.videowriter = None

        self.detectors = {'original':detectors.Detector(self.SETTINGS),
                        'colour': detectors.ColourDetector(self.SETTINGS),
                        'colourdiff': detectors.ColourDiffDetector(self.SETTINGS),
                        'difference':detectors.DiffDetector(self.SETTINGS),
                        'background':detectors.BackgroundSubDetector(self.SETTINGS),
                        'watershed': detectors.WatershedDetector(self.SETTINGS),
                        }

        self.trackers = {'csrt': trackers.CSRTTracker(self.SETTINGS),
                        }

        self.detector = self.detectors['original']

        self.framenum = 0
        print(str(self), ' created...')
        self.video_source = videocap.__getattribute__('video_source')
        self._num_frames = videocap.__getattribute__('_num_frames')
        
        self._isrunning = True
        self._istracking = False
        self._isrecording = False
        self.bboxes = {'stage':[(0,0,self.SETTINGS['width'],self.SETTINGS['height'])],'ROI':[],'Obj':[(0,0,0,0)]}
        self.track = []
        self.current_frame = self.GetFrame(0)

    def SetBox(self,boxtype,coords):

        if boxtype == 'ROI':
            self.bboxes['ROI'].append(coords)
        else:
            self.bboxes[boxtype][0] = coords
        print(self.bboxes)

    def SetDetector(self,detector):
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

    def GetNextFrame(self):
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

    def GetFrame(self, framenum=0,bboxes=None):
        self.videocap.set_frame(framenum)
        ret, frame = self.videocap.get_frame()
        if ret:
            self.current_frame = frame.copy()
            return frame

    def Save(self,path):
        data = ET.Element('data')
        boxes = ET.SubElement(data, 'boxes')
        for type_,coords in self.bboxes.items():
            box = ET.SubElement(boxes,'box')
            box.set('type',type_)
            for coord in coords:
                box.text = str(coord[0]) +','+str(coord[1]) +','+str(coord[2]) +','+str(coord[3])
        tracker = ET.SubElement(data,'track')
        for coords in self.track:
            item = ET.SubElement(tracker, 'coords')
            item.text = str(coords[0]) +','+str(coords[1])
        f = open(path,"w+")
        mydata = ET.tostring(data).decode('utf-8')
        f.write(mydata)
        f.close()

    def StartRecording(self, path):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(path+'.avi',fourcc, 30.0, (self.SETTINGS['width'],self.SETTINGS['height']))
        self.videowriter = out
        self._isrecording = True
        
    def StopRecord(self):
        self._isrecording = False
        self.videowriter.release()
        self.videowriter = None

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