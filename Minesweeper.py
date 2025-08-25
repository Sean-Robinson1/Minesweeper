from __future__ import annotations
from tkinter import Tk, Button, Label, Toplevel, Frame, Event
import random as R

main = Tk()
asciiChars = {'flag':'🚩','bomb':'💣','settings':'☰'}
numColours = {1:'blue',2:'green',3:'red',4:'navy',5:'maroon',6:'teal',7:'black',8:'dim gray'}

class Tile:
    def __init__(self, row: int, column: int, counter: int, numBombs: int, grid: Grid) -> None:
        self.grid = grid
        self.button = Button(main,text='',justify='center',width = 40, height = 40,bg = 'DARK GRAY',highlightbackground='Black',highlightthickness=1,font = ('Comic Sans',20))
        self.button.bind("<Button-1>", leftClick(counter,grid))
        self.button.bind("<Button-2>", rightClick(counter,grid))
        self.button.bind("<Button-3>", rightClick(counter,grid))
        self.button.place(x = column, y = row, width=40, height=40)

        self.isBomb = False
        self.num = 0
        self.gridNum = counter
        self.row = counter // grid.width
        self.column = counter % grid.width
        self.marked = False
        self.guessed = False

    def getAdjacentTiles(self) -> list[Tile]:
        adjacentTiles = []
        for i in [1,0,-1]:
            for ii in [1,0,-1]:
                row = self.row + i
                column = self.column + ii
                if 0 <= row < len(self.grid.display) and 0 <= column < len(self.grid.display[0]):
                    adjacentTiles.append([row,column])

        outputList = []
        for i in adjacentTiles:
            outputList.append(self.grid.display[i[0]][i[1]])

        return outputList

    def mark(self) -> None:
        if self.marked == False:
            if self.guessed == False:
                self.marked = True
                self.grid.numFlags += 1
                self.button.config(text = asciiChars['flag'],fg='red',bg = 'light gray')
                self.grid.label2.config(text = asciiChars['flag'] + ' : ' + str(self.grid.numFlags))
        else:
            self.marked = False
            self.button.config(text = '',fg = 'black',bg='dark gray')
            self.grid.numFlags -= 1
            self.grid.label2.config(text = asciiChars['flag'] + ' : ' + str(self.grid.numFlags))

    def guessTile(self, guessAdjacent: bool = False) -> None:
        if self.marked != True:
            if self.isBomb == False:
                if self.guessed == True:
                    if guessAdjacent == True and sum(tile.marked for tile in self.getAdjacentTiles()) == self.num:
                        for tile in self.getAdjacentTiles():
                            tile.guessTile()
                    return
                self.guessed = True
                if self.num == 0:
                    self.button.config(text = '', bg = 'light gray',fg='red')
                    stack = self.getAdjacentTiles()
                    while stack:
                        tile = stack.pop()
                        if tile.isBomb == False and tile.guessed == False and tile.marked == False:
                            if tile.num == 0:
                                tile.guessed = True
                                tile.button.config(text = '', bg = 'light gray')
                                stack.extend(tile.getAdjacentTiles())
                            else:
                                tile.guessTile()
                else:
                    self.button.config(text = self.num, bg = 'light gray',fg=numColours[self.num])

            else:
                self.button.config(text = asciiChars['bomb'], bg = 'red')

    def updateNum(self) -> None:
        for tile in self.getAdjacentTiles():
            if tile.isBomb == True:
                self.num += 1

class Grid:
    def __init__(self, main: Tk, width: int, height: int, numBombs: int):
        self.main = main
        self.width = width 
        self.height = height
        self.numBombs = numBombs
        self.numFlags = 0
        self.started = False
        self.top: Toplevel | None = None
        geoString = str(self.width * 40 + 40) + 'x' + str(self.height * 40 + 100)

        main.geometry(geoString)
        counter = 0

        self.display = []
        gridCounter = 0
        for row in range(50, 50 + self.height * 40, 40):
            self.display.append([])
            for column in range(20, 20 + self.width * 40, 40):
                tile = Tile(row,column,counter,self.numBombs,self)
                self.display[gridCounter].append(tile)
                counter += 1
            gridCounter += 1

        self.revealAllButton = Button(main,text='Reveal All',justify='center')
        self.revealAllButton.config(command = lambda:  self.revealAll())
        self.revealAllButton.place(x = (self.width * 40)/2 - 15, y = self.height * 40 + 60)

        self.label1 = Label(main,text= asciiChars['bomb'] + ' : ' + str(self.numBombs),font=('Comic Sans',20))
        self.label2 = Label(main,text= asciiChars['flag'] + ' : ' + str(0),font=('Comic Sans',20))
        self.label1.place(x = (self.width * 40 + 40) / 3 - 40, y = 10)
        self.label2.place(x = ((self.width * 40 + 40) / 3) * 2 - 40, y = 10,)
        self.settings = Button(main, text=asciiChars['settings'],justify = 'center',font = ('Comic Sans',20),command = self.openSettings)
        self.settings.place(x = 5, y = 5,width = 40, height = 40)

    def left_click(self, event: Event, x: int) -> None:
        event.widget.configure(highlightbackground='Black',highlightthickness=1)
        row =  x // self.width
        column =  x % self.width
        if self.started == False:
            self.generateBombs(self.display[row][column])
            self.started = True

            for i in self.display:
                for ii in i:
                    ii.updateNum()

        self.display[row][column].guessTile(True)

    def right_click(self, event: Event, x: int) -> None:
        event.widget.configure(highlightbackground='Black',highlightthickness=1)
        row =  x // self.width
        column =  x % self.width
        self.display[row][column].mark()

    def generateBombs(self, startTile: Tile):
        allTiles = []
        for row in range(len(self.display)):
            for column in range(len(self.display[0]) ):
                allTiles.append(self.display[row][column])

        R.shuffle(allTiles)
        counter = self.numBombs
        bombCounter = 0
        while counter > 0 and len(allTiles) > 0:
            if allTiles[0] != startTile and allTiles[0] not in startTile.getAdjacentTiles():
                allTiles[0].isBomb = True
                counter -= 1
                bombCounter += 1

            allTiles.pop(0)
        
        self.label1.config(text= asciiChars['bomb'] + ' : ' + str(bombCounter),font=('Comic Sans',20))

    def revealAll(self) -> None:
        for row in self.display:
            for tile in row:
                tile.guessTile()

    def updateWidth(self, x: int, y: Label) -> None:
        self.newWidth += x
        if self.newWidth < 1:
            self.newWidth = 1
        y.config(text = str(self.newWidth))

    def updateHeight(self, x:int , y:Label) -> None:
        self.newHeight += x
        if self.newHeight < 1:
            self.newHeight = 1
        y.config(text = str(self.newHeight))

    def updateNumBombs(self, x: int, y: Label) -> None:
        self.newNumBombs += x
        if self.newNumBombs < 1:
            self.newNumBombs = 1
        elif self.newNumBombs > self.newWidth * self.newHeight - 9:
            self.newNumBombs = max(1, self.newWidth * self.newHeight - 9)

        y.config(text = str(self.newNumBombs))

    def newGrid(self) -> None:
        for i in self.display:
            for ii in i:
                ii.button.destroy()

        self.label1.destroy()
        self.label2.destroy()
        self.settings.destroy()
        self.revealAllButton.destroy()
        if self.top is not None:
            self.top.destroy()

        Grid(self.main,self.newWidth,self.newHeight,self.newNumBombs)

    def openSettings(self) -> None:
        if self.top is not None and self.top.winfo_exists():
            self.top.lift()
            return
        self.newWidth = self.width
        self.newHeight = self.height
        self.newNumBombs = self.numBombs
        self.top = Toplevel(self.main)
        self.top.geometry("400x400")
        frame = Frame(self.top,width=400,height=400)
        title = Label(frame, text = 'SETTINGS').place(x = 140, y = 5)
        width = Label(frame,justify = 'center',font = ('Comic Sans',15),text='Grid Width: ').place(x = 20, y = 35)
        widthLabel = Label(frame,justify = 'center',bg='white',font = ('Comic Sans',20),text= str(self.width))
        widthLabel.place(x = 200, y = 35)
        reduceWidth = Button(frame, justify = 'center',text=' - ',command= lambda: self.updateWidth(-1,widthLabel)).place(x = 155, y = 35)
        increaseWidth = Button(frame, justify = 'center',text=' + ',command= lambda: self.updateWidth(1,widthLabel)).place(x = 245, y = 35)

        height = Label(frame,justify = 'center',font = ('Comic Sans',15),text='Grid Height: ').place(x = 20, y = 90)
        heightLabel = Label(frame,justify = 'center',bg='white',font = ('Comic Sans',20),text= str(self.height))
        heightLabel.place(x = 200, y = 90)
        reduceHeight = Button(frame, justify = 'center',text=' - ',command= lambda: self.updateHeight(-1,heightLabel)).place(x = 155, y = 90)
        increaseHeight = Button(frame, justify = 'center',text=' + ',command= lambda: self.updateHeight(1,heightLabel)).place(x = 245, y = 90)

        numBombs = Label(frame,justify = 'center',font = ('Comic Sans',15),text='Number of Bombs: ').place(x = 20, y = 145)
        bombLabel = Label(frame,justify = 'center',bg='white',font = ('Comic Sans',20),text= str(self.numBombs))
        bombLabel.place(x = 265, y = 145)
        reduceNumBombs = Button(frame, justify = 'center',text=' - ',command= lambda: self.updateNumBombs(-1,bombLabel)).place(x = 230, y = 145)
        reduceNumBombs2 = Button(frame, justify = 'center',text=' -- ',command= lambda: self.updateNumBombs(-10,bombLabel)).place(x = 185, y = 145)
        inceaseNumBombs = Button(frame, justify = 'center',text=' + ',command= lambda: self.updateNumBombs(1,bombLabel)).place(x = 305, y = 145)
        inceaseNumBombs2 = Button(frame, justify = 'center',text=' ++ ',command= lambda: self.updateNumBombs(10,bombLabel)).place(x = 343, y = 145)
        
        updateButton = Button(frame, justify = 'center',text=' APPLY CHANGES ',command= self.newGrid).place(x = 100, y = 300)

        exitButton = Button(frame,justify='center', text = 'EXIT',command= self.top.destroy).place(x = 150, y = 350)

        frame.pack()

def leftClick(i: int, grid: Grid):
    return lambda ev: grid.left_click(ev,i)

def rightClick(i: int, grid: Grid):
    return lambda ev: grid.right_click(ev,i)

if __name__ == '__main__':
    Grid(main,15,15,40)
    main.mainloop()



