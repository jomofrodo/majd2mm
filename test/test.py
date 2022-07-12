'''
Created on 11 July, 2022

@author: Lars Vogel
'''


def add(a, b):
    return a + b


def addFixedValue(a):
    y = 5
    return y + a


print(add(1, 2))
print(addFixedValue(1))
