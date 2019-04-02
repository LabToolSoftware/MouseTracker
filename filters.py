class Filter:
    def __init__(self, settings):
        self.SETTINGS = settings

    def filter_frame(self, frame):
        pass

class GaussianBlur(Filter):
    def __init__(self, settings):
        Filter.__init__(self, settings)
        
    def filter_frame(self,frame):
        pass
