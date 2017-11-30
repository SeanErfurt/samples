
from graphics import *
from random import randrange
from os import remove

def moviepicker():
    """chooses a movie at random from C:\\Python33\\Doc\\movielist.txt"""
    infile = open("movielist.txt", 'r')
    List = []
    for movie in infile.readlines():
        List.append(str(movie))
    rand = randrange(0,len(List))
    choice = List.pop(rand)
    infile.close()
    remove("movielist.txt")
    with open("movielist.txt", 'w') as outfile:
        for i in List:
            outfile.write(i)
    win = GraphWin("MoviePicker",600,200)
    win.setBackground(color_rgb(230,230,100))
    ans = Text(Point(300,120),"TONIGHT'S SHOWING WILL BE\n"+choice.upper())
    ans.setSize(24)
    ans.setFace("courier")
    ans.setStyle("bold")
    ans.draw(win)
    win.getMouse()
    win.close()
    
if __name__=='__main__':
    moviepicker()
