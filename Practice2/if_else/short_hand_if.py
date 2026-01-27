#we can write if else in one line
a = 2
b = 330
print("A") if a > b else print("B")

#assign if else to variable
a = 10
b = 20
bigger = a if a > b else b
print("Bigger is", bigger)

#syntax variable = value_if_true if condition else value_if_false

#chain if else statements
a = 330
b = 330
print("A") if a > b else print("=") if a == b else print("B")
#shorthand if makes code readable, it helps when condition are simple