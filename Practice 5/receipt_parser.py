#module RegEx(regular expressions)
import re

# \s MEANS " " or any white space character
# search() function
txt = "The rain in Spain"
x = re.search(r"\s", txt)

print("The first white-space character is located in position:", x.start())
# findall() function
txt = "The rain in Spain"
x = re.findall("ai", txt)
print(x)
#no matches findall()
txt = "The rain in Spain"
x = re.findall("Portugal", txt)
print(x)

#split func

txt = "The rain in Spain"
x = re.split("\s", txt)
print(x)
#we can add limit of splitter

x = re.split("\s", txt, 1)
print(x)

#sub function

txt = "The rain in Spain"
x = re.sub("\s", "9", txt)
print(x)

#also limit of sub

x = re.sub("\s", "9", txt, 2)
print(x)
#MATCH OBJECT (IF NO VALUE RETURNED, OUTPUT is None)

txt = "The rain in Spain"
x = re.search("ai", txt)
print(x) #this will print an object
'''
.span() returns a tuple containing the start-, and end positions of the match.
.string returns the string passed into the function
.group() returns the part of the string where there was a match
'''
#span
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.span())

#string
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.string)

#group
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.group())
