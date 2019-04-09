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