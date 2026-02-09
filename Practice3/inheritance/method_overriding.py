#__init__ method, it overrides parent init
class Student(Person):
  def __init__(self, fname, lname):
    Person.__init__(self, fname, lname)

#to save init
class Student(Person):
  def __init__(self, fname, lname):
    Person.__init__(self, fname, lname)