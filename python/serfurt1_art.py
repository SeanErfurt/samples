# This program creates art using random

from graphics import *
import random

i = eval(input("Enter any integer: "))

size = 400
m = 255
x=size/2
y=size/2
r=m/2
g=m/2
b=m/2
f = 10
win = GraphWin("Random Art", size, size)
win.setBackground('black')

for i in range(7500):
    x=x+f*(random.randint(0,2)-1)
    y=y+f*(random.randint(0,2)-1)
    x=min(x,size)
    x=max(x,0)
    y=min(y,size)
    y=max(y,0)
    
    p1=Point(x,y)
    p2=Point((x+f*(random.randint(0,2)-1)),(y+f*(random.randint(0,2)-1)))
    p3=Point((x+f*(random.randint(0,2)-1)),(y+f*(random.randint(0,2)-1)))
    shape = Polygon(p1, p2, p3)

    r=r+f*(random.randint(0,2)-1)
    g=g+f*(random.randint(0,2)-1)
    b=b+f*(random.randint(0,2)-1)
    r=min(r,m)
    r=max(r,0)
    g=min(g,m)
    g=max(g,0)
    b=min(b,m)
    b=max(b,0)
    
    shape.setFill(color_rgb(r,g,b))
    shape.setOutline(color_rgb(r,g,b))
    shape.draw(win)
    
prompt = Text(Point(300,370), " -le Computer")
prompt.setFill('dark green')
prompt.draw(win)
