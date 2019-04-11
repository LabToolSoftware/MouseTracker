import cv2
import abc

class Stream():
    def __init__(self, video_source,settings):
        self.__video_source = self.__openSource(video_source)
        self.__settings = settings.getSettings()
        self.__width = self._Stream__video_source.get(cv2.CAP_PROP_FRAME_WIDTH) 
        self.__height = self._Stream__video_source.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.__fps = self._Stream__video_source.get(cv2.CAP_PROP_FPS)

    def getFPS(self):
        return self.__fps

    def __openSource(self, source):
        try:
            return cv2.VideoStream(source)
        except:
            raise print('Video could not be loaded')

    def __iter__(self):
        return self

    def __next__(self):
        ret, frame = self._Stream__video_source.read()
        resized_frame = cv2.resize(frame.copy() , (self._Stream__width,self._Stream__height))
        resized_frame = cv2.cvtColor(resized_frame,cv2.COLOR_BGR2RGB)
        return ret, resized_frame

class IsScannable(Stream,abc.ABCMeta):
    @abc.abstractmethod    
    def setFrame(self, framenum):
        pass

    @abc.abstractmethod
    def getLength(self):
        pass  

class VideoStream(IsScannable): 
   
    def setFrame(self, framenum):
        self.__video_source.set(2,framenum)

    def getFPS(self):
        return self._Stream__fps

    def getLength(self):
        return self._Stream__fps  * self._Stream__video_source.get(cv2.CAP_PROP_)  

class VideoRecorder:
    def __init__(self):
        pass

    def StartRecording(self, path):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(path+'.avi',fourcc, 30.0, (self.SETTINGS['width'],self.SETTINGS['height']))
        self.videowriter = out
        self._isrecording = True
    
    def StopRecord(self):
        self._isrecording = False
        self.videowriter.release()
        self.videowriter = None

