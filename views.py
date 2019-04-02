import tkinter as tk 
from tkinter import filedialog, HORIZONTAL

import PIL.Image, PIL.ImageTk

LARGE_FONT = ("Verdana", 12)

class View(tk.Frame):
    def __init__(self, controller,settings):
        tk.Frame.__init__(self)
        self.controller = controller
        self.SETTINGS = settings
        self.InitialiseGrid()

    def InitialiseGrid(self):
        pass

class MainView(tk.Frame):
    def __init__(self, controller,settings):
        tk.Frame.__init__(self,controller)
        self.controller = controller
        self.SETTINGS = settings

        #Menubar initialisation
        self.InitialiseGrid()

    def InitialiseGrid(self):
        self.container = tk.Frame(self)

        menubar = tk.Menu(self)

        filemenu = tk.Menu(menubar,tearoff=0)
        filemenu.add_command(label="Open Webcam", command=lambda : self.OpenView('webcam'))
        filemenu.add_command(label="Open File", command=lambda : self.OpenView('video'))
        filemenu.add_command(label="Save project", command=lambda : print("Save Project Clicked"))
        filemenu.add_command(label="Close", command=lambda : self.Close())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
    
        settingsmenu = tk.Menu(menubar, tearoff =1)
        settingsmenu.add_command(label='General', command=None)
        settingsmenu.add_command(label='Background Subtraction', command=None)

        analysismenu = tk.Menu(menubar, tearoff =0)
        analysismenu.add_command(label='Open data', command=lambda:self.OpenView('analysis'))
        analysismenu.add_command(label='Close data', command=None)


        menubar.add_cascade(label="Video", menu=filemenu)
        menubar.add_cascade(label="Analysis", menu=analysismenu)
        menubar.add_cascade(label='Settings',menu=settingsmenu)
        self.controller.config(menu=menubar)

    def OpenView(self, view):
        self.container = self.controller.changeview(view)
        self.container.grid(row=0,column=0,sticky='NSEW')

    def Close(self):
        self.container.grid_forget()
        self.controller.close()

class VideoView(tk.Frame):
    def __init__(self,controller,settings):
        tk.Frame.__init__(self)
        self.controller = controller
        self.SETTINGS = settings.SETTINGS

        #Parameters
        self._isrunning = False 
        self.frame_pos = 0
        self.paused = True
        self.rect=None
        self.start_x = self.start_y = 0
        self.end_x = self.end_y = 0
        
        self.detectors = {'None': 'original',
                            'Colour': 'colour',
                            'Colour + Difference': 'colourdiff',
                            'Difference': 'difference',
                            'MOG2': 'background',
                            'Watershed': 'watershed',}
        self.detector = tk.StringVar()
        self.detector.set('None')

        self.trackers = {'CSRT': 'csrt'}
        self.tracker = tk.StringVar()
        self.tracker.set('CSRT')

        self.filters = {'None': 'original',
                        'Kalman': 'kalman'}
        self.filter = tk.StringVar()
        self.filter.set('None')

        self.InitialiseGrid()
        print(str(self), ' created...')
        self.UpdateFrame(10)
 
    def InitialiseGrid(self):

        self.mainwindow = tk.Frame(self)
        self.videoframe = tk.Frame(self.mainwindow)
        self.controlpanel = tk.Frame(self.mainwindow,width = self.SETTINGS['width'], relief=tk.RIDGE, borderwidth=1)
        self.sidebar = tk.Frame(self,width = 240, relief=tk.RIDGE, borderwidth=1)
        self.canvas_orig = tk.Canvas(self.videoframe, width = self.SETTINGS['width'], height = self.SETTINGS['height'], relief=tk.SUNKEN,borderwidth=1,cursor="cross")
        self.canvas_mask = tk.Canvas(self.videoframe, width = self.SETTINGS['width'], height = self.SETTINGS['height'], relief=tk.SUNKEN,borderwidth=1,cursor="cross")

        self.mainwindow.grid(row=0,column=0)
        self.videoframe.grid(row=0,column=0,stick="EW")
        self.controlpanel.grid(row=1,column=0,sticky="EW")
        self.sidebar.grid(row=0,column=1)
        self.canvas_orig.grid(row=0,column=0)
        self.canvas_mask.grid(row=0,column=1)

        self.btn_setStage = tk.Button(self.sidebar, text="Set Stage", command=lambda : self.SetBox('stage'))
        self.btn_setROI = tk.Button(self.sidebar, text="Set ROI", command=lambda : self.SetBox('ROI'))
        self.btn_setObj = tk.Button(self.sidebar,text="Select Object", command=lambda : self.SetBox('Obj'))
        self.btn_start = tk.Button(self.sidebar,text='Start Tracking',command=lambda : self.StartTracking())
        self.btn_save = tk.Button(self.sidebar,text="Save",command=lambda : self.Save())
        self.btn_record = tk.Button(self.controlpanel, text="Start Recording",command=lambda: self.StartRecording())
        self.btn_srecord = tk.Button(self.controlpanel, text="Stop Recording",command=lambda: self.StopRecording())
        self.btn_setStage.grid(row=3,column=0,columnspan=2,sticky="EW")
        self.btn_setROI.grid(row=4,column=0,columnspan=2,sticky="EW")
        self.btn_setObj.grid(row=5,column=0,columnspan=2,sticky="EW")
        self.btn_start.grid(row=6,column=0,columnspan=2,sticky="EW")
        self.btn_save.grid(row=7,column=0,columnspan=2,sticky="EW")
        self.btn_record.grid(row=1,column=3,sticky="EW")

        self.lbl_background = tk.Label(self.sidebar, text="Background Subtraction: ")
        self.lbl_tracker = tk.Label(self.sidebar, text="Tracker: ")
        self.lbl_filter = tk.Label(self.sidebar, text="Filter: ")
        self.lbl_background.grid(row=0,column=0)
        self.lbl_tracker.grid(row=1,column=0)
        self.lbl_filter.grid(row=2,column=0)
        self.combo_detector = tk.OptionMenu(self.sidebar,self.detector,*self.detectors,command=lambda event: self.SetDetector(event=event))
        self.combo_tracker = tk.OptionMenu(self.sidebar,self.tracker,*self.trackers)
        self.combo_filter = tk.OptionMenu(self.sidebar,self.filter,*self.filters)
        self.combo_detector.grid(row=0,column=1)
        self.combo_tracker.grid(row=1,column=1)
        self.combo_filter.grid(row=2,column=1)


        
        if not isinstance(self.controller.video_source,int):
            self.stop_btn = tk.Button(self.controlpanel,text="Stop", command=lambda : self.Stop())
            self.pause_btn = tk.Button(self.controlpanel,text="Pause", command=lambda : self.Pause())
            self.resume_btn = tk.Button(self.controlpanel,text="Play", command=lambda : self.Resume())
            
            self.slider = tk.Scale(self.controlpanel, from_=0, to=self.controller._num_frames, orient=HORIZONTAL,length=self.SETTINGS['width'])
            self.slider.bind("<ButtonPress-1>",lambda x : self.Pause(event=x))
            self.slider.bind("<B1-Motion>",lambda x : self.UpdateFrame(event=x,framenum=self.slider.get()))
            

            self.slider.grid(row=0,column=0,columnspan=4,sticky="EW")
            self.stop_btn.grid(row=1,column=0,sticky="EW")
            self.pause_btn.grid(row=1,column=1,sticky="EW")
            self.resume_btn.grid(row=1,column=2,sticky="EW")

            
        else:
            self.pause_btn = tk.Button(self.controlpanel,text="Pause", command=lambda : self.Pause())
            self.resume_btn = tk.Button(self.controlpanel,text="Play", command=lambda : self.Resume())
            self.pause_btn.grid(row=1,column=1,sticky="EW")
            self.resume_btn.grid(row=1,column=2,sticky="EW")
            self._isrunning = True       

    def BoxStart(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if not self.rect:
            self.rect = self.canvas_orig.create_rectangle(0,0,1,1,outline="black")

    def BoxExpand(self, event):
        self.end_x = event.x
        self.end_y  = event.y
        self.canvas_orig.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)

    def BoxStop(self, event, boxtype):
        self.canvas_orig.unbind("<ButtonPress-1>")
        self.canvas_orig.unbind("<B1-Motion>")
        self.canvas_orig.unbind("<ButtonRelease-1>")
        self.canvas_orig.delete(self.rect)
        self.rect = None
        self.controller.SetBox(boxtype,(self.start_x,self.start_y,self.end_x,self.end_y))

    def MakeBox(self,boxtype):
        self.canvas_orig.bind("<ButtonPress-1>",lambda x : self.BoxStart(x))
        self.canvas_orig.bind("<B1-Motion>",lambda x : self.BoxExpand(x))
        self.canvas_orig.bind("<ButtonRelease-1>",lambda x : self.BoxStop(x,boxtype))

    def SetBox(self,boxtype):
        self.Pause()
        self.MakeBox(boxtype)

    def Resume(self):
        self.paused=False
        self.Update()

    def Pause(self,event=None):
        self.paused =True

    def Save(self):
        path = filedialog.asksaveasfilename()
        self.controller.Save(path)

    def Stop(self):
        self.paused = True
        self.frame_pos = 0
        self.UpdateFrame(0)

    def SetDetector(self,event):
        self.Pause()
        detector = self.detectors[self.detector.get()]
        self.controller.SetDetector(detector)

    def StartTracking(self):
        tracker = self.trackers[self.tracker.get()]
        self.controller.StartTracking(tracker)

    def StartRecording(self):
        self.Pause()
        path = filedialog.asksaveasfilename()
        self.controller.StartRecording(path)
        self.btn_record.grid_remove()
        self.btn_srecord.grid(row=1,column=3,sticky="EW")
  
    def StopRecording(self):
        self.Pause()
        self.controller.StopRecord()
        self.btn_srecord.grid_remove()
        self.btn_record.grid(row=1,column=3,sticky="EW")

    def Update(self):
        delay = 10
        if not self.paused:
            frame,mask= self.controller.GetNextFrame()
            self.frame_pos += 1
            normal_photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas_orig.image = normal_photo
            self.canvas_orig.create_image(0, 0, image = normal_photo, anchor = tk.NW)
            mask_photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(mask))
            self.canvas_mask.image = mask_photo
            self.canvas_mask.create_image(0, 0, image = mask_photo, anchor = tk.NW)
            if not isinstance(self.controller.video_source,int):
                self.slider.set(self.frame_pos)
            self.after(delay, self.Update)

    def UpdateFrame(self,framenum,event=None):
        frame = self.controller.GetFrame()
        normal_photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
        self.canvas_orig.create_image(0, 0, image = normal_photo, anchor = tk.NW)
        self.canvas_orig.image = normal_photo
        if not isinstance(self.controller.video_source,int):
                self.slider.set(self.frame_pos)

class AnalysisView(tk.Frame):
    def __init__(self,controller,settings):
        tk.Frame.__init__(self)
        self.controller = controller
        self.InitialiseGrid()

    def InitialiseGrid(self):
        self.maincontainer = tk.Frame(self)
        self.main = tk.Canvas(self.maincontainer)
        self.sidebar = tk.Frame(self)
        self.btn_basic = tk.Button(self.sidebar,text='Heatmap...',command=lambda:self.GetHeatMap())

        self.maincontainer.grid(row=0,column=0)
        self.main.grid(row=0,column=0)
        self.sidebar.grid(row=0,column=1)
        self.btn_basic.grid(row=0,column=0)
        self.GetPlot()

    def GetPlot(self, format_='original'):
        self.main = self.controller.GetPlot(type_=format_,master=self.maincontainer)        
        self.main.grid(row=0,column=0)

    def GetHeatMap(self):
        heatmap = self.controller.GenerateHeatMap()
        heatmap_photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(heatmap))
        self.main.image = heatmap_photo
        self.main.create_image(0, 0, image = heatmap_photo, anchor = tk.NW)