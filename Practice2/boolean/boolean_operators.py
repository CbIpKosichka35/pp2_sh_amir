x = 10
y = 5

#theres comparison operators that returns true or false(boolean data type)
print(x == y)
print(x != y)
print(x > y)
print(x < y)
print(x >= y)
print(x <= y)

#chain operators
print(1 < x < 100)
#or
print(1 < x and x < 100)

#identity operator is/ is not, checks if variables points on the same object
x = ["apple", "banana"]
y = ["apple", "banana"]
z = x

print(x is z) #true
print(x is y) #false
print(x == y) #true
print(x is not z) #false
print(x is not y) #true

#membership operator in/not in, checks if value contains in other variable
fruits = ["banana", "cucumber", "kartoshka"]
print("banana" in fruits) #true
print("pomidori" not in fruits) #true
text = "Hello world!"
print("hell" in text) #false
print("World!!" in text) #false