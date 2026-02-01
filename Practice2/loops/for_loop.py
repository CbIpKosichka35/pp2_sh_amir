fruits = ["apple", "banana", "cherry", "arbuzii", "cucumber"]
for x in fruits:
  print(x)

#for loops mostly works like iterator it will point on char of string, part of list eand etc.

for x in "megacucumber":
  print(x)

#as i said earlier, x ges through whole string and prints each char in new line

#we can use range() to get especial loop

for i in range(5):
    print(i)
#it prints all numbers from 0 to 4
for i in range(2, 5):
    print(i)
#it prints all numbers from 2 to 4
for i in range(2, 17, 2):
    print(i)\
#adds a new step, instead of +1, goes +2

for x in range(6):
  print(x)
else:
  print("Finally finished!")
#else works when for loop finished