#while loop is going on till condition is true
i = 1
while i < 6:
  print(i)
  i += 1
a = 10
while(a < 0)
    print("a is smaller than 0") #this loop will never be printed because condition is already false
while(a > 0)
    print("a is bigger than 0") #this loop will be infinite

#else statement
i = 1
while i < 6:
  print(i)
  i += 1
else:
  print("i is no longer less than 6")
#else will work when while become false
#IT WONT WORK IF LOOP STOPPED WITH break