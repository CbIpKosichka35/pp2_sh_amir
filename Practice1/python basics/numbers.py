# integer
x = 1
# float. can be written through e
y = 5.9
y = 35.2e3 #e means power of 10
#complex. part with j represents imaginery part
z = 1j
z = 4 + 5j
z = -10j
print(type(x))
print(type(y))
print(type(z))

#convert from int to float:
a = float(x)
#convert from float to int:
b = int(y)
#convert from int to complex:
c = complex(x)

print(a)
print(b)
print(c)

print(type(a))
print(type(b))
print(type(c))

import random
#prints random number
print(random.randrange(1, 100))