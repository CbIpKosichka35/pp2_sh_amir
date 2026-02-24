def square(n):
    for i in range(1, n+1):
        yield i * i
n = int(input())

for i in square(n):
    print(i)

n = int(input())
print(*(i for i in range(0, n + 1, 2)), sep=",")

def devisible(n):
    for i in range(n + 1):
        if i % 3 == 0 and i%4 ==0:
            yield i
n=int(input())
for i in devisible(n):
    print(i)

def squares(a,b):
    for i in range(a, b+1):
        yield i * i
a=list(map(int,input().split()))
for i in squares(a[0],a[1]):
    print(i)

n=int(input())
print(*(i for i in range(n, -1, -1)), sep=" ")

import json
with open("sample-data.json") as f:
    text = f.read()

data = json.loads(text)

print("Interface Status")
print("="*80)
print(f"{'DN':50} {'Description':20} {'Speed':8} {'MTU':5}")
print("-"*80)

for item in data["imdata"]:
    a = item["l1PhysIf"]["attributes"]
    print(f"{a['dn']:50} {a['descr']:20} {a['speed']:8} {a['mtu']}")