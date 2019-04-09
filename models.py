import cv2
import xml.etree.ElementTree as ET

class VideoCap(cv2.VideoCapture):
    
    def __init__(self, video_source,settings):

        cv2.VideoCapture.__init__(self,video_source)

        self.__video_source = video_source
        self.__SETTINGS = settings.getSettings()

        if not self.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self.__width = self.get(cv2.CAP_PROP_FRAME_WIDTH) 
        self.__height = self.get(cv2.CAP_PROP_FRAME_HEIGHT) 

        if not isinstance(self.__video_source,int):
            self.__fps = self.get(cv2.CAP_PROP_FPS)
            self.__length = self._num_frames/self._fps
        print(str(self), 'created...')

    def get_frame(self):
        ret, frame = self.read()
        resized_frame = cv2.resize(frame.copy() , (self.SETTINGS['width'],self.SETTINGS['height']))
        resized_frame = cv2.cvtColor(resized_frame,cv2.COLOR_BGR2RGB)
        return ret, resized_frame

    def set_frame(self, framenum):
        self.set(2,framenum)

    def get_fps(self):
        return (self._VideoCap__fps,self._VideoCap__length)

    def get_length(self):
        return self._VideoCap__length

    def get_size(self):
        return (self._VideoCap__width,self._VideoCap__height)

class DataCap:
    def __init__(self, source):
        self.__data_source = source
        self.__boxes,self.__track_coords = self.getData(source)
        print("Opened: " + str(self))

    def __str__(self):
        return str(self.data_source)

    def getData(self):
        boxes = {}
        track = []
        tree = ET.parse(__data_source)
        root = tree.getroot()
        for box in tree.iter(tag='box'):
            coords = box.text.split(',')
            boxes[str(box.get('type'))] = (int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]))
        for coords in tree.iter(tag='coords'):
            x,y = coords.text.split(',')
            track.append((int(x),int(y)))
        return box,track
