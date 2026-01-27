# if else usually supports logical/comparison conditions from math
#VERY IMPORTANT IS TABULATION
a = 33
b = 200
if b > a:
    print("b is greater than a")
if b == a:
    print("b is equal to a") #this will not work because condition is false
if b != a:
    print("b is not equal to a")

#there can be several statements!
if b > a:
    print("b is greater than a")
    print("a is smaller than b")
    print(f"b is bigger than a by {b-a}")

#we can use variables also
is_he_student = True
if is_he_student:
    print("YEs he is")


