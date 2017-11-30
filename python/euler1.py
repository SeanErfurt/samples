# This program calculates Euler approximations

def EulApp():
    h = eval(input("What is the step size? "))
    xIn, yIn = eval(input("Enter the initial point coords: "))
    xFin = eval(input("what x value do you want to stop at? "))
    yder = input("y'= ")
    
    steps = int((xFin - xIn)/h)
    x = xIn
    y = yIn
    for i in range(0, steps):
        y = y + h*(eval(yder))
        x = x + h
        print(x, y)

EulApp()
