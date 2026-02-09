#inheritance is using by implementing 1 class into other
class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)

#Use the Person class to create an object, and then execute the printname method:

x = Person("John", "Doe")
x.printname()

class Student(Person):
  pass

x = Student("Mike", "Olsen")
x.printname()


#__init__ method, it overrides parent init
class Student(Person):
  def __init__(self, fname, lname):
    Person.__init__(self, fname, lname)

#to save init
class Student(Person):
  def __init__(self, fname, lname):
    Person.__init__(self, fname, lname)