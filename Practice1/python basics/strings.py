#basics

print("Hello")
print('Hello')

a = "Hello"
print(a)
a = """hello world
in 3 
different lines"""
print(a)
a = "Hello, World!"
print(a[1])

for x in "banana":
  print(x) # prints each row each letter

#string length
print(len(a))

#check string
txt = "The best things in life are free!"
print("free" in txt) #output True/False
if ("free" in txt):
   print("Yes it is in string")
if ("not free" not in txt):
    print("No, not free is not in string ") 

# SLICING STRINGS
b = "Hello World!"
print(b[2:5]) #prints all from b[2] to b[4]
print(b[2:]) #prints everything from b[2]
print(b[:5]) #prints everything below b[5]
print(b[-5:-3]) #negative numbers counts from end

# modified strings
c = "Hello, Python!"
print(c.upper()) # only upper letters
print(c.lower()) # only lower letters
c = " Hello, Python! "
print(c.strip()) # removes " " from both ends

c = "Hello, World!"
print(c.replace("H", "W"))

c = "Hello, World!"
print(a.split(","))

a = "HEllo "
b = "world!"
print(a + b)

# f strings
quantity = 40
text = f"theres {quantity} pieces of cake"
print(text)
print(f"Theres also {quantity} pieces of cucumbers")
print(f"Those shoes worth {quantity:.2f}")
# non f string method
text = "those \"Vikings\" stole our cake"
print(text)