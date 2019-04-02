import cv2
import xml.etree.ElementTree as ET

class VideoCap(cv2.VideoCapture):
    
    def __init__(self, video_source,settings):
        cv2.VideoCapture.__init__(self,video_source)
        self.video_source = video_source
        self.SETTINGS = settings.SETTINGS
        if not self.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self._width = self.get(cv2.CAP_PROP_FRAME_WIDTH) 
        self._height = self.get(cv2.CAP_PROP_FRAME_HEIGHT) 
        self._num_frames = self.get(cv2.CAP_PROP_FRAME_COUNT)
        if not isinstance(self.video_source,int):
            self._fps = self.get(cv2.CAP_PROP_FPS)
            self._length = self._num_frames/self._fps
        print(str(self), 'created...')

    def get_frame(self):
        ret, frame = self.read()
        resized_frame = cv2.resize(frame.copy() , (self.SETTINGS['width'],self.SETTINGS['height']))
        resized_frame = cv2.cvtColor(resized_frame,cv2.COLOR_BGR2RGB)
        return ret, resized_frame

    def set_frame(self, framenum):
        self.set(2,framenum)

class DataCap:
    def __init__(self, source):
        self.data_source = source
        self.boxes,self.track_coords = self.Parse(source)
        print("Opened: " + str(self))

    def __str__(self):
        return str(self.data_source)

    def Parse(self, source):
        boxes = {}
        track = []
        tree = ET.parse(source)
        root = tree.getroot()
        for box in tree.iter(tag='box'):
            coords = box.text.split(',')
            boxes[str(box.get('type'))] = (int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]))
        for coords in tree.iter(tag='coords'):
            x,y = coords.text.split(',')
            track.append((int(x),int(y)))
        return box,track
