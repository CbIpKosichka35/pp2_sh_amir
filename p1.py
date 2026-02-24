def hello(hi, *names):
    for name in names:
        print(f"{name}, {hi} ")

hello("Hello", "Oleg", "Tanya")