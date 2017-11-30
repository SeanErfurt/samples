# by: Sean Erfurt

from random import randrange
from time import sleep

def create_boards(size):  ## boards are lists of lists
    board = []
    hidden_board = []
    for x in range(0, size):
        board.append(["."] * size)
        hidden_board.append(["."] * size)
    return board, hidden_board

def gen_ships(hidden_board,ships):
    ship = 0
    while ship < ships:
        y = randrange(0, len(hidden_board))
        x = randrange(0, len(hidden_board[0]))
        if not hidden_board[y][x] == "B":       # prevents overlap of ships
            hidden_board[y][x] = "B"
            ship += 1         
    return hidden_board

def print_board(board):
    for row in board:
        print(" ".join(row))
    print("\n")

def turn(board, hidden_board):
    shot = 0
    while shot != 1:  # so that misfires don't count as a loss of turn
        try:
            gy, gx = input("Guess Coord(Row,Col): ").split(",")
            try:
                gy = int(gy) - 1  ## input(1,1) -> corrects for index starting at 0,0
                gx = int(gx) - 1  ## also makes sure that the inputs are ints
            except TypeError:
                print("\nYou didn't enter a coordinate properly!")
            if (gy < 0 or gy > len(board) - 1) or (gx < 0 or gx > len(board[0]) - 1):
                print("\nThat's outside the ocean!")
            elif hidden_board[gy][gx] == "B":
                print("\nHit!")
                hidden_board[gy][gx] = "."   ## enables game_over(hb) to function
                board[gy][gx] = "X"
                shot = 1
            elif board[gy][gx] == "O" or board[gy][gx] == "X":
                print("\nYou already shot there!")
            else:
                print("\nMiss!")
                board[gy][gx] = "O"
                shot = 1
        except ValueError:
            print("You didnt enter enough numbers!")
    return board, hidden_board
    
def game_over(hidden_board):  ## if all of hidden_board's elements are ".", game ends
    for i in range(0, len(hidden_board)):
        for j in range(0, len(hidden_board[i])):
            if hidden_board[i][j] == "B":
                return False
    else:
        return True

def place_ships(hb,ships):  ## for 2-player
    ship = 0
    while ship < ships:
        try:
            y, x = input("Select Coord(Row,Col): ").split(",")
            try:
                y = int(y) - 1
                x = int(x) - 1
            except TypeError:
                print("\nYou didn't enter a coordinate properly!")
            if (y < 0 or y > len(hb) - 1) or (x < 0 or x > len(hb[0]) - 1):
                print("\nThat's outside the ocean!")
            elif not hb[y][x] == "B":
                hb[y][x] = "B"
                ship += 1
                print_board(hb)
            else:
                print("\nYou already placed a ship there!")
        except ValueError:
            print("You didn't enter enough numbers!")
    return hb


def one_player(size,ships):
    board, hidden_board = create_boards(size)
    hidden_board = gen_ships(hidden_board,ships)
    turns = 0
    while True: 
        print_board(board)
        board, hidden_board = turn(board, hidden_board)
        turns += 1
        if game_over(hidden_board):
            print_board(board)
            print("You won in %d turns!"%(turns))
            break

def two_player(size,ships):
        b1,hb1 = create_boards(size)
        b2,hb2 = create_boards(size)
        print("Player 1, place your ships!")
        print_board(b1)
        hb1 = place_ships(hb1,ships)
        sleep(2)        ## all uses of sleep() are for better display in 2-player
        print("\n" * 35 +"Player 2, place your ships!") 
        print_board(b2)
        hb2 = place_ships(hb2,ships)
        sleep(2)
        print("\n" * 35) ## 'clears' board
        turns = 0
        while True:
            if turns % 2 == 0:
                print("\n\nPlayer 1's turn")
                print_board(b1)
                b1,hb2 = turn(b1, hb2)
                print_board(b1)
                sleep(2)
                turns += 1
                if game_over(hb2):
                    print("Player 1 wins!")
                    break
            elif turns % 2 == 1:
                print("\n\nPlayer 2's turn")
                print_board(b2)
                b2,hb1 = turn(b2, hb1)
                print_board(b2)
                sleep(2)
                turns += 1
                if game_over(hb1):
                    print("Player 2 wins!")
                    break
                

class Boat():
    size = 0
    def __init__(self,board,y1,x1,y2,x2):
        self.board = board
        self.y1 = y1
        self.x1 = x1
        self.y2 = y2
        self.x2 = x2

    def place(self):  ## sends boat's position to board
        if self.y1 == self.y2:
            if self.x1 < self.x2:
                for i in range(self.x1,self.x2 + 1):
                    self.board[self.y1][i] = "B"
            else:
                for i in range(self.x2,self.x1 + 1):
                    self.board[self.y1][i] = "B"
            return self.board
                
        elif self.x1 == self.x2:
            if self.y1 < self.y2:
                for i in range(self.y1,self.y2 + 1):
                    self.board[i][self.x1] = "B"
            else:
                for i in range(self.y2,self.y1 + 1):
                    self.board[i][self.x1] = "B"
            return self.board

    def getSize(self):  ## for checking length
        size = self.size
        return size

    def getCoords(self):  ## for tracking boats to determine which sank
        coords = []         ## coords stores a list of tuples for each 'B' position
        if self.y1 == self.y2:
            if self.x1 < self.x2:
                for i in range(self.x1,self.x2 + 1):
                    coords.append((self.y1,i))
            else:
                for i in range(self.x2,self.x1 + 1):
                    coords.append((self.y1,i))
            return coords
                
        elif self.x1 == self.x2:
            if self.y1 < self.y2:
                for i in range(self.y1,self.y2 + 1):
                    coords.append((i,self.x1))
            else:
                for i in range(self.y2,self.y1 + 1):
                    coords.append((i,self.x1))
            return coords
            
                
    def isSunk(self):  ## checks boat's position on board; if no 'B's, must have sank
        if self.y1 == self.y2:  ## if horizontal
            if self.x1 < self.x2:
                for i in range(self.x1,self.x2 + 1):
                    if self.board[self.y1][i] == "B":
                        return False
                else:
                    return True
            else:       ## if x1 was initiated to be smaller than x2, is possible
                for i in range(self.x2,self.x1 + 1):
                    if self.board[self.y1][i] == "B":
                        return False
                else:
                    return True
        elif self.x1 == self.x2: ## if vertical
            if self.y1 < self.y2:
                for i in range(self.y1,self.y2 + 1):
                    if self.board[i][self.x1] == "B":
                        return False
                else:
                    return True
            else:
                for i in range(self.y2,self.y1 + 1):
                    if self.board[i][self.x1] == "B":
                        return False
                else:
                    return True
    
class Tugboat(Boat):
    size = 2
    def __init__(self,board,y1,x1,y2,x2):
        self.board = board
        self.y1 = y1
        self.x1 = x1
        self.y2 = y2
        self.x2 = x2
    def __str__(self):
        return "Tugboat!"

class Submarine(Boat):
    size = 3
    def __init__(self,board,y1,x1,y2,x2):
        self.board = board
        self.y1 = y1
        self.x1 = x1
        self.y2 = y2
        self.x2 = x2
    def __str__(self):
        return "Submarine!"

class Destroyer(Boat):
    size = 3
    def __init__(self,board,y1,x1,y2,x2):
        self.board = board
        self.y1 = y1
        self.x1 = x1
        self.y2 = y2
        self.x2 = x2
    def __str__(self):
        return "Destroyer!"
    
class Battleship(Boat):
    size = 4
    def __init__(self,board,y1,x1,y2,x2):
        self.board = board
        self.y1 = y1
        self.x1 = x1
        self.y2 = y2
        self.x2 = x2
    def __str__(self):
        return "Battleship!"

class Carrier(Boat):
    size = 5
    def __init__(self,board,y1,x1,y2,x2):
        self.board = board
        self.y1 = y1
        self.x1 = x1
        self.y2 = y2
        self.x2 = x2
    def __str__(self):
        return "Carrier!"
    
def place_longships(hb,ships):
    ship = 0
    boats = {}
    while ship < ships*5:  ## creates 'sets' of ships
        try:
            if ship % 5 == 0:
                print("Place a Carrier(length of 5)")
            elif ship % 5 == 1:
                print("Place a Battleship(len of 4)")
            elif ship % 5 == 2:
                print("Place a Destroyer(len of 3)")
            elif ship % 5 == 3:
                print("Place a Submarine(len of 3)")
            elif ship % 5 == 4:
                print("Place a Tugboat(len of 2)")
                
            y, x = input("Start Coord: ").split(",")
            y2,x2= input("End Coord: ").split(",")
            try:
                y = int(y) - 1
                x = int(x) - 1
                y2=int(y2) - 1
                x2=int(x2) - 1
            except TypeError:
                print("\nYou didn't enter a coordinate properly!")
            if (y < 0 or y > len(hb) - 1) or (x < 0 or x > len(hb[0]) - 1) or \
               (y2 < 0 or y2 > len(hb) - 1) or (x2 < 0 or x2 > len(hb[0]) - 1):
                print("\nThat's outside the ocean!")

            if ship % 5 == 0:
                boat = Carrier(hb,y,x,y2,x2)
            elif ship % 5 == 1:
                boat = Battleship(hb,y,x,y2,x2)
            elif ship % 5 == 2:
                boat = Destroyer(hb,y,x,y2,x2)
            elif ship % 5 == 3:
                boat = Submarine(hb,y,x,y2,x2) ## created temporarily to test
            elif ship % 5 == 4:
                boat = Tugboat(hb,y,x,y2,x2)   ## for length and overlap
            
            if (y == y2 and abs(x - x2) + 1 != boat.getSize()) or \
               (x == x2 and abs(y - y2) + 1 != boat.getSize()):
                print("\nThat's not the right length!")
            elif y != y2 and x != x2:
                print("\nShips can only be 1 unit thick!")
            elif not boat.isSunk(): ## recycled to test for overlap
                print("\nYou already placed a ship there!")
            else: ## once all tests have passed, place and save boat
                boat.place()
                boats[ship] = boat
                print_board(hb)
                ship += 1 ## moves on to next ship
        except ValueError:
            print("You didn't enter enough numbers!")
    return hb, boats


def gen_longships(hb,ships): ## this is rate-determining step in 1-p longships
    ship = 0                 ## similar to past functions
    boats = {}
    while ship < ships*5:
        y = randrange(0, len(hb))
        x = randrange(0, len(hb[0]))
        pos = randrange(0,2)
        if pos == 0:        ## even dist of horizontal and vert ships (0==hor)
            if ship % 5 == 0 and (x+4 <= len(hb)-1): ## <- test for going off the
                boat = Carrier(hb,y,x,y,x + 4)       ## board is now integrated here
            elif ship % 5 == 1 and (x+3 <= len(hb)-1):
                boat = Battleship(hb,y,x,y,x + 3)
            elif ship % 5 == 2 and (x+2 <= len(hb)-1):
                boat = Destroyer(hb,y,x,y,x + 2)
            elif ship % 5 == 3 and (x+2 <= len(hb)-1):
                boat = Submarine(hb,y,x,y,x + 2)
            elif ship % 5 == 4 and (x+1 <= len(hb)-1):
                boat = Tugboat(hb,y,x,y,x + 1)
            try:
                if boat.isSunk():  ## if no overlap found, place boat
                    boat.place()
                    boats[ship] = boat
                    ship += 1
            except:                ## otherwise, try again
                pass
        elif pos == 1:
            if ship % 5 == 0 and (x+4 <= len(hb)-1):
                boat = Carrier(hb,y,x,y + 4,x)
            elif ship % 5 == 1 and (x+3 <= len(hb)-1):
                boat = Battleship(hb,y,x,y + 3,x)
            elif ship % 5 == 2 and (x+2 <= len(hb)-1):
                boat = Destroyer(hb,y,x,y + 2,x)
            elif ship % 5 == 3 and (x+2 <= len(hb)-1):
                boat = Submarine(hb,y,x,y + 2,x)
            elif ship % 5 == 4 and (x+1 <= len(hb)-1):
                boat = Tugboat(hb,y,x,y+ 1,x)
            try:
                if boat.isSunk():
                    boat.place()
                    boats[ship] = boat
                    ship += 1
            except:
                pass
    return hb, boats

def coordSet(boats):  ## creates the coordset(list of lists of tuples)
    coordset = []       ##to save time when tracking ships by only doing it once
    for i in boats.values():
        coordset.append(i.getCoords())
    return coordset

def long_turn(board, hidden_board, boats, coordset): ##turn for traditional
    shot = 0
    while shot != 1:
        try:
            gy, gx = input("Guess Coord(Row,Col): ").split(",")
            try:
                gy = int(gy) - 1
                gx = int(gx) - 1
            except TypeError:
                print("\nYou didn't enter a coordinate properly!")
            if (gy < 0 or gy > len(board) - 1) or (gx < 0 or gx > len(board[0]) - 1):
                print("\nThat's outside the ocean!")
            elif hidden_board[gy][gx] == "B":
                print("\nHit!")
                hidden_board[gy][gx] = "."
                board[gy][gx] = "X"
                for i in range(0, len(coordset)): ## checks if target boat was sunk.
                    for j in range(0,len(coordset[i])): ##possibly could be modularized more here
                        if coordset[i][j] == (gy, gx):  ##to prevent too much redundancy?
                            coordset[i][j] = "."
                            if boats[i].isSunk():
                                print("You sunk a",boats[i])
                shot = 1
            elif board[gy][gx] == "O" or board[gy][gx] == "X":
                print("\nYou already shot there!")
            else:
                print("\nMiss!")
                board[gy][gx] = "O"
                shot = 1
        except ValueError:
            print("You didnt enter enough numbers!")
    return board, hidden_board, coordset

def traditional(size,ships): ## essentially two_player() with new functions
    b1,hb1 = create_boards(size)
    b2,hb2 = create_boards(size)
    print("Player 1, place your ships!(Row,Col)")
    print_board(b1)
    hb1, boats1 = place_longships(hb1,ships)
    sleep(2)
    coordset1 = coordSet(boats1)
    print("\n" * 35 +"Player 2, place your ships!(Row,Col)") 
    print_board(b2)
    hb2, boats2 = place_longships(hb2,ships)
    sleep(2)
    coordset2 = coordSet(boats2)
    print("\n" * 35)
    turns = 0
    while True:
        if turns % 2 == 0:
            print("\n\nPlayer 1's turn")
            print_board(b1)
            b1,hb2,coordset2 = long_turn(b1, hb2, boats2, coordset2)
            print_board(b1)
            sleep(2)
            turns += 1
            if game_over(hb2):
                print("Player 1 wins!")
                break
        elif turns % 2 == 1:
            print("\n\nPlayer 2's turn")
            print_board(b2)
            b2,hb1,coordset1 = long_turn(b2, hb1, boats1, coordset1)
            print_board(b2)
            sleep(2)
            turns += 1
            if game_over(hb1):
                print("Player 2 wins!")
                break

def trad_one_player(size,ships):
    b1,hb1 = create_boards(size)
    hb1, boats1 = gen_longships(hb1,ships)
    coordset1 = coordSet(boats1)
    turns = 0
    while True:
        print_board(b1)
        b1,hb1,coordset1 = long_turn(b1, hb1, boats1, coordset1)
        turns += 1
        if game_over(hb1):
            print_board(b1)
            print("You won in %d turns!"%(turns))
            break
            
def play_battleship(size, ships, players=1,longships=True):
    """1-2 player battleship game with user-defined board size and # of ships.\
Longships is traditional battleship with 5 x 'ships' in play"""
    if longships == False:
        if size**2 < ships:  ## to prevent an infinite loop
            return "Board is too small for this many ships!"
        elif size > 40:             ## to prevent weird-looking rows/columns
            return "Board is too large for screen!"
        if players == 1:
            one_player(size, ships)
        else:
            two_player(size,ships)
    elif longships == True: ## lower bound here is to prevent long load times(possibly an infinite loop in gen_longships())
        if size <= round(-0.006*(ships)**2 + 0.9*(ships) + 5.5):
            return "Board is too small for this many ships!"
        elif size > 38:
            return "Board is too large for screen!"
        if players == 1:
            trad_one_player(size,ships)
        else:
            traditional(size,ships)
            
if  __name__=='__main__':  ## test
    play_battleship(10,1,2,True)
