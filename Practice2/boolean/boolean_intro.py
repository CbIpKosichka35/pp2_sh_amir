#important thing is Boolean values (true or false), we can get them through operators like
print(15 > 9)
print(10 < 15)
print(10 == 10)
print(14 == 13.99)

#can be used in if else statements
a = 100
b = 33
if (a > b):
    print("a is greater than b")
else:
    print("b is greater than a")

# bool() evaluates other data types to boolean (all empty will be false)
print(bool("Hi")) #output is true
print(bool("")) #output is false
print(bool(10)) #true
print(bool(-3)) #true
print(bool(0)) #false
print(bool([1, 2, 3])) #true
print(bool([])) #false
print(bool(None)) #false

print(isinstance(a, str)) #returns true/false depends is variable data type is correct

#boolean function
def myFunction() :
  return True

print(myFunction())

