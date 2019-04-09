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