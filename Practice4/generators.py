#iterators

mytuple = ("apple", "banana", "cherry")
myit = iter(mytuple)

print(next(myit))
print(next(myit))
print(next(myit))
#iter() creates iterator
#next() switches on next element in array

#string is also iteratable
mystr = "banana"
myit = iter(mystr)

print(next(myit))
print(next(myit))
print(next(myit))
print(next(myit))
print(next(myit))
print(next(myit))

#iterators can be used in loops
spring_semestr = ["Calc2", "Discrete Strutures", "History", "PP2", "English", "Physics"]

for discipline in spring_semestr:
    print(discipline, end=" ")

mystr = "banana"

for x in mystr:
    print(x)

# iterators in classes
class MyNumbers:
  def __iter__(self):
    self.a = 1
    return self

  def __next__(self):
    if self.a <= 20:
      x = self.a
      self.a += 1
      return x
    else:
      raise StopIteration

myclass = MyNumbers()
myiter = iter(myclass)

for x in myiter:
  print(x)
