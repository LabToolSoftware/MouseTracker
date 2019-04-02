import cv2
import numpy as np
from scipy import ndimage
from skimage.feature import peak_local_max
from skimage.morphology import watershed

class Detector():

    """ This is a base class for a video feed that gets frames from a cv2.VideoCapture Object,
     processes them in a defined manner then returns the frame to the VideoController to display"""

    def __init__(self, settings):
        self.sync=True
        self.kernel = None
        self.SETTINGS = settings

    def reinitialize(self):
        pass

    def detect_frame(self, frame):
        return frame

class ColourDetector(Detector):
    def __init__(self, settings):
        Detector.__init__(self, settings)
        self.kernel = cv2.getStructuringElement(self.SETTINGS['kshape'],
                                                self.SETTINGS['ksize'])

    def AbsDiff(self,frame1,frame2):  
        differnce_image = cv2.absdiff(frame1,frame2)
        return differnce_image   
    
    def Threshold(self, frame):
        threshold_frame = cv2.inRange(frame,
                                    self.SETTINGS['hsv_min'],
                                    self.SETTINGS['hsv_max'])
        return threshold_frame

    def Blur(self, frame):
        blur_size = 4
        blur_frame = cv2.blur(frame,(blur_size,blur_size))
        return blur_frame

    def detect_frame(self,frame):
        hsv_frame = cv2.cvtColor(frame,cv2.COLOR_RGB2HSV)
        blur_frame = self.Blur(hsv_frame)
        #threshold_frame = self.Threshold(hsv_frame)
        #fgmask = cv2.morphologyEx(threshold_frame, self.SETTINGS['kmorph'], self.kernel) 
        return blur_frame

class ColourDiffDetector(Detector):
    def __init__(self, settings):
        Detector.__init__(self, settings)
        self.sensitivity = self.SETTINGS['sensitivity']
        self.stored_frame = None
        self.kernel = cv2.getStructuringElement(self.SETTINGS['kshape'],
                                                self.SETTINGS['ksize'])

    def AbsDiff(self,frame1,frame2):  
        differnce_image = cv2.absdiff(frame1,frame2)
        return differnce_image   
    
    def Threshold(self, frame):
        threshold_frame = cv2.inRange(frame,
                                    self.SETTINGS['hsv_min'],
                                    self.SETTINGS['hsv_max'])
        return threshold_frame

    def Blur(self, frame):
        blur_size = 10
        blur_frame = cv2.blur(frame,(blur_size,blur_size))
        return blur_frame

    def detect_frame(self,frame):
        hsv_frame = cv2.cvtColor(frame,cv2.COLOR_RGB2HSV)
        if self.stored_frame is None:
            self.stored_frame = hsv_frame.copy()
        difference_frame = self.AbsDiff(self.stored_frame,hsv_frame)
        #threshold_frame = self.Threshold(difference_frame)
        fgmask = cv2.morphologyEx(difference_frame, self.SETTINGS['kmorph'], self.kernel) 
        self.stored_frame = hsv_frame.copy()
        return difference_frame

class DiffDetector(Detector):
    def __init__(self, settings):
        Detector.__init__(self, settings)
        self.sensitivity = self.SETTINGS['sensitivity']
        self.stored_frame = None
        self.kernel = cv2.getStructuringElement(self.SETTINGS['kshape'],
                                                self.SETTINGS['ksize'])

    def AbsDiff(self,frame1,frame2):  
        differnce_image = cv2.absdiff(frame1,frame2)
        return differnce_image   
    
    def Threshold(self, frame):
        ret, threshold_frame = cv2.threshold(frame,self.sensitivity,255,cv2.THRESH_BINARY)
        if ret:
            return (threshold_frame)

    def Blur(self, frame):
        blur_size = 10
        blur_frame = cv2.blur(frame,(blur_size,blur_size))
        return blur_frame

    def detect_frame(self,frame):
        if self.stored_frame is None:
            self.stored_frame = frame.copy()
        difference_frame = self.AbsDiff(self.stored_frame,frame)
        threshold_frame = self.Threshold(difference_frame)
        fgmask = cv2.morphologyEx(threshold_frame, self.SETTINGS['kmorph'], self.kernel) 
        self.stored_frame = frame.copy()
        return fgmask

class BackgroundSubDetector(Detector):    

    def __init__(self, settings):
        Detector.__init__(self, settings)
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=self.SETTINGS['history'], 
                                                    varThreshold=self.SETTINGS['threshold'], 
                                                    detectShadows=self.SETTINGS['shadows'])


        self.kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                                (5,5))
        self.kernel_close = cv2.getStructuringElement(self.SETTINGS['kshape'],
                                                self.SETTINGS['ksize'])

    def detect_frame(self, frame):
        #resized_frame = cv2.GaussianBlur(resized_frame, (10,10), 0)
        fgmask  = self.fgbg.apply(frame, self.SETTINGS['learn_rate'])
        fgmask = cv2.morphologyEx(fgmask, self.SETTINGS['kmorph'], self.kernel_close) 
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel_open)  
         
        mask_frame = frame.copy()  
        mask_frame[fgmask==0] = (0,0,0)
        mask_frame[fgmask!=0] = (0,0,255)
        merge_frame = cv2.addWeighted(mask_frame,1.0,frame,1.0,0)
        return mask_frame

class WatershedDetector(Detector):
    def __init__(self, settings):
        Detector.__init__(self, settings)

    def PyrMeanShiftFilter(self, frame):
        blur = cv2.bilateralFilter(frame,9,75,75)
        shifted = cv2.pyrMeanShiftFiltering(frame, 21, 51)
        return shifted

    def Threshold(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255,
	    cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        return thresh, gray
    
    def Watershed(self, thresh, frame):
        D = ndimage.distance_transform_edt(thresh)
        localMax = peak_local_max(D, indices=False, min_distance=20,
            labels=frame)
        
        # perform a connected component analysis on the local peaks,
        # using 8-connectivity, then appy the Watershed algorithm
        markers = ndimage.label(localMax, structure=np.ones((3, 3)))[0]
        labels = watershed(-1*D, markers, mask=thresh)
        print("[INFO] {} unique segments found".format(len(np.unique(labels)) - 1))
        for label in np.unique(labels):
    	# if the label is zero, we are examining the 'background'
        # so simply ignore it
            if label == 0:
                continue
        
            # otherwise, allocate memory for the label region and draw
            # it on the mask
            mask = np.zeros(frame.shape, dtype="uint8")
            mask[labels == label] = 255
        
            # detect contours in the mask and grab the largest one
            _, contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            c = max(contours, key=cv2.contourArea)
        
            # draw a circle enclosing the object
            ((x, y), r) = cv2.minEnclosingCircle(c)
            print(x,y,r)
        return c

    def detect_frame(self,frame):
        shifted = self.PyrMeanShiftFilter(frame)
        thresh,gray = self.Threshold(shifted)
        mask_frame = self.Watershed(thresh,gray)
        return mask_frame