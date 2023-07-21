def add_n(n: int, l=[]):
    l.append(n)
    return print(l)


add_n(1) # [1]
add_n(2,[1]) # [1, 2]
add_n(3) # [3]