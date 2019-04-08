# test for encapsulation in python

class Test():
    def __init__(self,attr1,attr2):
        self.attr1 = attr1
        self.__attr2 = attr2

    def get_attr2(self):
        return self.__attr2

test = Test('public','private')

print(test.attr1)
print(test.get_attr2())
print(test.__attr2)
