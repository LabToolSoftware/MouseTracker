import xml.etree.ElementTree as ET

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

class DataWriter:
    def __init__(self):
        pass

    def writeData(self, path, data):
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