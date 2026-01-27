# elif is like if but with second precedence /  if "if" statement is false, next checked is
# ELIF

a = 50
b = 50
if (b < a):
    print("b is smaller than a")
elif b == a:
    print("b is equal to a")

#example
age = 25

if age < 13:
  print("You are a child")
elif age < 20:
  print("You are a teenager")
elif age < 65:
  print("You are an adult")
elif age >= 65:
  print("You are a senior")