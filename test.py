class Person:
    def __init__(self, name):
        self.__name = name
        self.getName()
    
    def getName(self):
        print(self.__name)

    
class Employee(Person):

    def isEmployee(self):
        return True

class Executive(Employee):

    def isExecutive(self):
        return True


steve = Employee('Steve')
george = Person('George')
CEO = Executive('Bob')