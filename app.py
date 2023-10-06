import pygame,math,random,time,copy,os
import PyUI as pyui
import json
pygame.init()
screenw = 1200
screenh = 800
screen = pygame.display.set_mode((screenw,screenh),pygame.RESIZABLE)
pygame.scrap.init()
ui = pyui.UI()
done = False
clock = pygame.time.Clock()
ui.addinbuiltimage('sudoku',pygame.image.load(pyui.resourcepath('assets\\sukoku.png')))
ui.escapeback = False

ui.styleload_lightblue()

textfilterdic = {'1':(255,0,0),'2':(0,255,0),'3':(0,0,255),'4':(255,255,0),'5':(255,255,255),'6':(0,100,160),'7':(0,0,150),'8':(255,100,0),'9':(205,0,180)}
fade = pyui.genfade([(255,0,0),(0,0,255),(0,255,0)],9)
for i in range(10,27):
    textfilterdic[str(i)] = fade[i-10]
        
def textcolfilter(st):
    out = ''
    for a in st:
        out+='{"'+a+'" col='+str(textfilterdic[a])+'}'
    return out

class Sudoku:
    def checkdupe(lis):
        lis = lis[:]
        while 0 in lis:
            lis.remove(0)
        for a in lis:
            if len([b for b in lis if b==a])>1:
                return True
        return False

    def inverse(grid):
        return [[grid[b][a] for b in range(len(grid[a]))] for a in range(len(grid))]

    def valid(bgrid):
        grid = copy.deepcopy(bgrid)
        for y in grid:
            if Sudoku.checkdupe(y):
                return False
        
        for x in Sudoku.inverse(grid):
            if Sudoku.checkdupe(x):
                return False
        for m in Sudoku.segmentgrid(grid):
            if Sudoku.checkdupe(m):
                return False
        return True

    def segmentgrid(grid):
        ngrid = [[] for b in range(len(grid))]
        mini = int(len(grid)**0.5)
        for y,a in enumerate(grid):
            for x,b in enumerate(a):
                pos = (y//mini)*mini+x//mini
                ngrid[pos].append(b)
        
        return ngrid

    def checksolved(grid):
        completed = True
        for a in grid:
            for b in a:
                if b == 0:
                    completed = False
        return completed

    def checksolveable(grid,pmap=-1):
        if pmap == -1: pmap = Sudoku.possible_map(grid)
        mini = int(len(grid)**0.5)
        for y,a in enumerate(pmap):
            for x,b in enumerate(a):
                if len(a) == 0:
                    return False
                if grid[y][x] == 0:
                    checker = [[],[],[]]
                    for c in a:
                        checker[0]+=c
                    for c in [pmap[i][x] for i in range(len(pmap))]:
                        checker[1]+=c
                    for c in Sudoku.segmentgrid(pmap)[(y//mini)*mini+x//mini]:
                        checker[2]+=c
                    for c in checker:
                        for n in range(1,len(grid)):
                            if not (n in c):
                                return False
        return True
    def checksolveamount(grid,base):
        bempty = 0
        for a in base:
            for b in a:
                if b == 0:
                    bempty+=1
        gempty = 0
        for a in grid:
            for b in a:
                if b == 0:
                    gempty+=1
        return 100-int(gempty/bempty*100)

    def makegrid(size=9):
        items = [a+1 for b in range(size) for a in range(size)]
        grid = [[0 for a in range(size)] for b in range(size)]
        while len(items)>(size**2-17):
            item = items.pop(random.randint(0,len(items)-1))
            x = random.randint(0,size-1)
            y = random.randint(0,size-1)
            if grid[y][x] == 0:
                grid[y][x] = item
                if not Sudoku.valid(grid):
                    items.append(item)
                    grid[y][x] = 0
                    
            else:
                items.append(item)
        solutions = Sudoku.solve(grid)
        if len(solutions) == 0:
            solutions = [Sudoku.makegrid(size)]
        return solutions[0]

    def strip(grid,count):
        size = len(grid)
        ngrid = copy.deepcopy(grid)
        for a in range(count):
            x = random.randint(0,size-1)
            y = random.randint(0,size-1)
            while ngrid[y][x] == 0:
                x = random.randint(0,size-1)
                y = random.randint(0,size-1)
            ngrid[y][x] = 0
        return ngrid

    def makesudoku(size=9,diff=50):
        grid = Sudoku.makegrid(size)
        stripped = 10
        grid = Sudoku.strip(grid,stripped)
        cut = 4
        attempts = 0
        while 1:
            past = copy.deepcopy(grid)
            grid = Sudoku.strip(grid,cut)
            f = Sudoku.solve(copy.deepcopy(grid),singlesolution=False,cutafterone=True)
            if len(f) == 1:
                stripped+=cut
                cut = max(int(cut*0.8),1)
                attempts = 0
            elif stripped>diff or attempts>4:
                return past
            else:
                grid = past
                attempts+=1
        

    def possible_map(grid):
        pmap = [[[] for a in range(len(grid[0]))] for b in range(len(grid))]
        for y,a in enumerate(grid):
            for x,b in enumerate(a):
                if grid[y][x] == 0:
                    for n in range(1,len(grid)+1):
                        grid[y][x] = n
                        if Sudoku.valid(grid):
                            pmap[y][x].append(n)
                    grid[y][x] = 0
                else:
                    pmap[y][x].append(grid[y][x])
        return pmap

                
    def fill(grid):
        if Sudoku.checksolved(grid):
            return grid,1
        pmap = Sudoku.possible_map(grid)
        ngrid = copy.deepcopy(grid)
        mini = int(len(grid)**0.5)
        edit = []
        for y,a in enumerate(pmap):
            for x,b in enumerate(a):    
                if ngrid[y][x] == 0:
                    for p in b:
                        checker = [[],[],[]]
                        for c in a:
                            checker[0]+=c
                        for c in [pmap[i][x] for i in range(len(pmap))]:
                            checker[1]+=c
                        for c in Sudoku.segmentgrid(pmap)[(y//mini)*mini+x//mini]:
                            checker[2]+=c
                        valid = True
                        for c in checker:
                            if len([i for i in c if i==p]) == 1:
                                edit.append([y,x,p])
        if len(edit) == 0:
            return ngrid,0
        for a in edit:
            ngrid[a[0]][a[1]] = a[2]
        ngrid,found = Sudoku.fill(ngrid)
        return ngrid,found
    def clue(grid):
        if Sudoku.checksolved(grid):
            return []
        pmap = Sudoku.possible_map(grid)
        cordmap = [[(x,y) for x in range(len(grid[y]))] for y in range(len(grid))]
        mini = int(len(grid)**0.5)
        edit = []
        for y,a in enumerate(pmap):
            for x,b in enumerate(a):    
                if grid[y][x] == 0:
                    for p in b:
                        checker = [[],[],[]]
                        hlkey = [[],[],[]]
                        for c in range(len(a)):
                            checker[0]+=a[c]
                            hlkey[0].append(cordmap[y][c])
                        for c in [pmap[i][x] for i in range(len(pmap))]:
                            checker[1]+=c
                        for c in [cordmap[i][x] for i in range(len(pmap))]:
                            hlkey[1].append(c)
                        for c in Sudoku.segmentgrid(pmap)[(y//mini)*mini+x//mini]:
                            checker[2]+=c
                        for c in Sudoku.segmentgrid(cordmap)[(y//mini)*mini+x//mini]:
                            hlkey[2].append(c)
                        valid = True
                        for k,c in enumerate(checker):
                            if len([i for i in c if i==p]) == 1:
                                edit.append([y,x,p,k,hlkey[k]])
        if len(edit) == 0:
            return []
        return edit

    def solve(grid,solutions=-1,singlesolution=True,depth=0,cutafterone=False):
        if solutions == -1:
            solutions = []
        grid,found = Sudoku.fill(grid)
        if Sudoku.checksolved(grid):
            solutions.append(grid)
            return solutions
        pmap = Sudoku.possible_map(grid)
        if not Sudoku.checksolveable(grid,pmap):
            return solutions
        else:
            for n in range(1,len(grid)+1):       
                for y,a in enumerate(pmap):
                    for x,b in enumerate(a):
                        if grid[y][x] == 0 and n in pmap[y][x]:
                            grid[y][x] = n
                            if Sudoku.checksolveable(grid):
                                solutions = Sudoku.solve(copy.deepcopy(grid),solutions,singlesolution,depth+1,cutafterone)
                            if (singlesolution and len(solutions)>0) or (cutafterone and len(solutions)>1):
                                return solutions
                            grid[y][x] = 0
            return solutions
class Minesweeper:
    unknown = pygame.image.load(pyui.resourcepath('assets\\unknown2.png'))
    unknowntop = pygame.image.load(pyui.resourcepath('assets\\unknown top.png'))
    unknownbottom = pygame.image.load(pyui.resourcepath('assets\\unknown bottom.png'))
    unknown.set_colorkey((255,255,255))
    unknowntop.set_colorkey((255,255,255))
    unknownbottom.set_colorkey((255,255,255))
    
    base = pygame.image.load(pyui.resourcepath('assets\\base.png'))
    basetop = pygame.image.load(pyui.resourcepath('assets\\basetop.png'))
    basebottom = pygame.image.load(pyui.resourcepath('assets\\basebottom.png'))
    baseboth = pygame.image.load(pyui.resourcepath('assets\\baseboth.png'))
    
    flag = pygame.image.load(pyui.resourcepath('assets\\flag.png'))
    flagsmaller = pygame.image.load(pyui.resourcepath('assets\\flag smaller.png'))
    bomb = pygame.image.load(pyui.resourcepath('assets\\bomb.png'))
    bombsmaller = pygame.image.load(pyui.resourcepath('assets\\bomb smaller.png'))
    flag.set_colorkey((255,255,255))
    flagsmaller.set_colorkey((255,255,255))
    bomb.set_colorkey((255,255,255))
    bombsmaller.set_colorkey((255,255,255))

    
    def genimage(field,x,y,z,fieldmap):
        val = field[y][z][x]
        mapped = fieldmap[y][z][x]
        up = False
        down = False
        if y == 0:
            if len(field) == 1:
                base = Minesweeper.base
            else:
                up = True
                base = Minesweeper.basetop
        else:
            down = True
            if y == len(field)-1:
                base = Minesweeper.basebottom
            else:
                up = True
                base = Minesweeper.baseboth
        base.set_colorkey((255,255,255))
        img = pygame.Surface((50,50))
        img.fill((200,200,200))
        if mapped == 0:
            img.blit(Minesweeper.unknown,(0,0))  
        elif mapped == 2:
            img.blit(Minesweeper.unknown,(0,0))
            img.blit(Minesweeper.flag,(0,0))
        elif mapped == 1 and val == -1:
            img.blit(Minesweeper.bomb,(0,0))
        elif val != 0:
            ui.write(img,25,25,str(val),30,textfilterdic[str(val)],font='calibre')

        if up:
            val = field[y+1][z][x]
            mapped = fieldmap[y+1][z][x]
            if mapped == 0:
                img.blit(Minesweeper.unknowntop,(32,3))
            elif mapped == 2:
                img.blit(Minesweeper.flagsmaller,(32,0))
            elif mapped == 1 and val == -1:
                img.blit(Minesweeper.bombsmaller,(32,0))
            elif val != 0:
                ui.write(img,42,8,str(val),14,textfilterdic[str(val)],font='calibre')
        elif mapped in [0,2]:
            img.blit(Minesweeper.unknowntop,(32,3))
        mapped = fieldmap[y][z][x]
        if down:
            val = field[y-1][z][x]
            mapped = fieldmap[y-1][z][x]
            if mapped == 0:
                img.blit(Minesweeper.unknownbottom,(3,32))
            elif mapped == 2:
                img.blit(Minesweeper.flagsmaller,(0,32))
            elif mapped == 1 and val == -1:
                img.blit(Minesweeper.bombsmaller,(0,32))
            elif val != 0:
                ui.write(img,8,42,str(val),14,textfilterdic[str(val)],font='calibre')
        elif mapped in [0,2]:
            img.blit(Minesweeper.unknownbottom,(3,32))

        img.blit(base,(0,0))
        return img
        
        
    def gengrid(x,y,z,cover):
        mines = round(x*y*z*cover)
        
        field = []
        for a in range(y):
            field.append([])
            for b in range(z):
                field[-1].append([])
                for c in range(x):
                    field[-1][-1].append(0)
        while mines>0:
            a = random.randint(0,x-1)
            b = random.randint(0,y-1)
            c = random.randint(0,z-1)
            if field[b][c][a] == 0:
                field[b][c][a] = -1
                mines-=1
            
        for a in range(y):
            for b in range(z):
                for c in range(x):
                    if field[a][b][c] == 0:
                        field[a][b][c] = Minesweeper.count(field,c,a,b)
        return field
##    def solve(field,x,y,z,fieldmap):
##        

    def count(field,x,y,z):
        if field[y][z][x] == -1:
            return -1
        count = 0
        for a in range(-1,2):
            for b in range(-1,2):
                for c in range(-1,2):
                    if Minesweeper.inbox(field,x+c,y+a,z+b):
                        if field[y+a][z+b][x+c] == -1:
                            count+=1
        return count

    def inbox(field,x,y,z):
        if x<0 or y<0 or z<0:
            return False
        if y>len(field)-1 or z>len(field[y])-1 or x>len(field[y][z])-1:
            return False
        return True

class funcersl:
    def __init__(self,main,level):
        self.func = lambda: main.opensudoku(level)
class funcerus:
    def __init__(self,main,i,j):
        self.func = lambda: main.updatesudoku(i,j)
class funcermc:
    def __init__(self,main,x,y,z):
        self.func = lambda: main.mineclicked(x,y,z)
class funcerpf:
    def __init__(self,main,x,y,z):
        self.func = lambda: main.placeflag(x,y,z)
class funcerml:
    def __init__(self,main,layer):
        self.func = lambda: main.movelayer(layer)

class Main:
    def __init__(self):
        self.points = 0
        #((x*z)**0.5)/10*y
        #5
        self.levels = [[[[0, 2, 3, 4, 7, 6, 8, 9, 5], [6, 8, 9, 5, 2, 3, 4, 7, 1], [5, 4, 7, 9, 1, 8, 2, 6, 3], [4, 1, 2, 3, 8, 9, 7, 5, 6], [7, 6, 8, 1, 5, 2, 3, 4, 9], [9, 3, 5, 6, 4, 7, 1, 2, 8], [2, 7, 6, 8, 3, 5, 9, 1, 4], [8, 9, 1, 7, 6, 4, 5, 3, 2], [3, 5, 4, 2, 9, 1, 6, 8, 7]], [[1, 2, 3, 4, 7, 6, 8, 9, 5], [6, 8, 9, 5, 2, 3, 4, 7, 1], [5, 4, 7, 9, 1, 8, 2, 6, 3], [4, 1, 2, 3, 8, 9, 7, 5, 6], [7, 6, 8, 1, 5, 2, 3, 4, 9], [9, 3, 5, 6, 4, 7, 1, 2, 8], [2, 7, 6, 8, 3, 5, 9, 1, 4], [8, 9, 1, 7, 6, 4, 5, 3, 2], [3, 5, 4, 2, 9, 1, 6, 8, 7]]], [[[0, 0, 0, 0, 0, 6, 8, 0, 0], [6, 0, 0, 0, 2, 3, 4, 0, 0], [0, 0, 0, 9, 1, 0, 2, 0, 3], [0, 0, 2, 3, 0, 9, 7, 5, 6], [0, 0, 8, 0, 5, 0, 0, 0, 9], [0, 3, 0, 6, 0, 0, 0, 2, 8], [2, 0, 6, 8, 0, 5, 0, 1, 4], [8, 9, 0, 0, 0, 4, 0, 3, 0], [0, 0, 4, 2, 0, 1, 0, 0, 0]], [[1, 2, 3, 4, 7, 6, 8, 9, 5], [6, 8, 9, 5, 2, 3, 4, 7, 1], [5, 4, 7, 9, 1, 8, 2, 6, 3], [4, 1, 2, 3, 8, 9, 7, 5, 6], [7, 6, 8, 1, 5, 2, 3, 4, 9], [9, 3, 5, 6, 4, 7, 1, 2, 8], [2, 7, 6, 8, 3, 5, 9, 1, 4], [8, 9, 1, 7, 6, 4, 5, 3, 2], [3, 5, 4, 2, 9, 1, 6, 8, 7]]], [[[2, 0, 3, 0, 0, 0, 7, 0, 0], [0, 0, 0, 0, 0, 9, 0, 0, 0], [6, 9, 8, 0, 5, 0, 0, 0, 0], [1, 0, 4, 0, 0, 0, 0, 9, 0], [3, 2, 9, 0, 8, 1, 0, 0, 0], [0, 0, 0, 0, 3, 0, 0, 2, 0], [9, 1, 0, 0, 4, 0, 0, 6, 2], [4, 0, 0, 0, 0, 6, 0, 8, 5], [0, 5, 0, 0, 0, 3, 9, 4, 7]], [[2, 4, 3, 1, 6, 8, 7, 5, 9], [5, 7, 1, 4, 2, 9, 6, 3, 8], [6, 9, 8, 3, 5, 7, 2, 1, 4], [1, 8, 4, 6, 7, 2, 5, 9, 3], [3, 2, 9, 5, 8, 1, 4, 7, 6], [7, 6, 5, 9, 3, 4, 8, 2, 1], [9, 1, 7, 8, 4, 5, 3, 6, 2], [4, 3, 2, 7, 9, 6, 1, 8, 5], [8, 5, 6, 2, 1, 3, 9, 4, 7]]], [[[0, 1, 3, 4, 9, 5, 7, 6, 8], [0, 8, 0, 1, 2, 0, 9, 4, 5], [4, 0, 0, 7, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 2, 6], [0, 2, 0, 3, 4, 0, 0, 0, 7], [0, 7, 0, 5, 0, 2, 3, 0, 0], [1, 0, 0, 0, 0, 0, 6, 0, 3], [0, 0, 9, 0, 0, 0, 5, 8, 0], [0, 5, 8, 0, 0, 9, 0, 0, 4]], [[2, 1, 3, 4, 9, 5, 7, 6, 8], [6, 8, 7, 1, 2, 3, 9, 4, 5], [4, 9, 5, 7, 8, 6, 1, 3, 2], [5, 3, 1, 9, 7, 8, 4, 2, 6], [9, 2, 6, 3, 4, 1, 8, 5, 7], [8, 7, 4, 5, 6, 2, 3, 1, 9], [1, 4, 2, 8, 5, 7, 6, 9, 3], [7, 6, 9, 2, 3, 4, 5, 8, 1], [3, 5, 8, 6, 1, 9, 2, 7, 4]]], [[[1, 2, 0, 0, 8, 0, 0, 3, 7], [0, 0, 8, 0, 1, 7, 0, 0, 9], [0, 6, 0, 0, 9, 2, 0, 0, 0], [2, 0, 0, 0, 5, 4, 8, 9, 0], [4, 9, 6, 0, 2, 8, 0, 0, 0], [8, 7, 5, 0, 0, 0, 0, 2, 1], [0, 4, 2, 0, 7, 1, 0, 0, 3], [6, 1, 7, 0, 4, 0, 0, 8, 0], [0, 0, 0, 2, 0, 0, 0, 0, 4]], [[1, 2, 9, 4, 8, 5, 6, 3, 7], [3, 5, 8, 6, 1, 7, 2, 4, 9], [7, 6, 4, 3, 9, 2, 1, 5, 8], [2, 3, 1, 7, 5, 4, 8, 9, 6], [4, 9, 6, 1, 2, 8, 3, 7, 5], [8, 7, 5, 9, 3, 6, 4, 2, 1], [9, 4, 2, 8, 7, 1, 5, 6, 3], [6, 1, 7, 5, 4, 3, 9, 8, 2], [5, 8, 3, 2, 6, 9, 7, 1, 4]]], [[[0, 2, 7, 4, 0, 6, 0, 5, 8], [8, 4, 9, 0, 0, 0, 6, 0, 2], [0, 3, 6, 0, 0, 0, 1, 0, 0], [2, 0, 4, 0, 0, 9, 0, 0, 7], [0, 0, 5, 7, 0, 0, 2, 0, 0], [0, 6, 0, 2, 4, 0, 0, 1, 5], [0, 5, 0, 3, 0, 8, 0, 0, 9], [6, 7, 2, 0, 0, 4, 5, 0, 3], [0, 0, 3, 6, 5, 0, 0, 0, 0]], [[1, 2, 7, 4, 9, 6, 3, 5, 8], [8, 4, 9, 1, 3, 5, 6, 7, 2], [5, 3, 6, 8, 7, 2, 1, 9, 4], [2, 1, 4, 5, 6, 9, 8, 3, 7], [3, 9, 5, 7, 8, 1, 2, 4, 6], [7, 6, 8, 2, 4, 3, 9, 1, 5], [4, 5, 1, 3, 2, 8, 7, 6, 9], [6, 7, 2, 9, 1, 4, 5, 8, 3], [9, 8, 3, 6, 5, 7, 4, 2, 1]]], [[[0, 5, 0, 0, 0, 6, 0, 0, 0], [0, 0, 0, 3, 0, 8, 0, 9, 0], [1, 0, 0, 0, 0, 0, 4, 3, 0], [0, 0, 0, 2, 0, 0, 7, 5, 0], [0, 3, 0, 4, 8, 1, 0, 2, 9], [0, 8, 2, 0, 0, 0, 0, 1, 0], [0, 0, 5, 6, 0, 4, 9, 7, 0], [4, 2, 0, 0, 0, 5, 8, 6, 1], [7, 0, 0, 8, 1, 9, 0, 0, 0]], [[3, 5, 4, 1, 9, 6, 2, 8, 7], [2, 7, 6, 3, 4, 8, 1, 9, 5], [1, 9, 8, 5, 7, 2, 4, 3, 6], [9, 4, 1, 2, 6, 3, 7, 5, 8], [5, 3, 7, 4, 8, 1, 6, 2, 9], [6, 8, 2, 9, 5, 7, 3, 1, 4], [8, 1, 5, 6, 2, 4, 9, 7, 3], [4, 2, 9, 7, 3, 5, 8, 6, 1], [7, 6, 3, 8, 1, 9, 5, 4, 2]]], [[[0, 0, 0, 0, 8, 7, 0, 0, 9], [0, 0, 0, 1, 5, 2, 3, 0, 7], [5, 0, 0, 0, 0, 9, 0, 0, 4], [7, 0, 1, 6, 2, 4, 9, 0, 0], [9, 0, 0, 7, 1, 0, 0, 0, 0], [4, 0, 2, 5, 9, 8, 0, 0, 3], [0, 0, 0, 0, 3, 0, 8, 7, 0], [0, 0, 7, 0, 4, 6, 2, 0, 5], [0, 0, 6, 2, 7, 0, 0, 0, 0]], [[1, 2, 3, 4, 8, 7, 5, 6, 9], [6, 4, 9, 1, 5, 2, 3, 8, 7], [5, 7, 8, 3, 6, 9, 1, 2, 4], [7, 3, 1, 6, 2, 4, 9, 5, 8], [9, 8, 5, 7, 1, 3, 6, 4, 2], [4, 6, 2, 5, 9, 8, 7, 1, 3], [2, 5, 4, 9, 3, 1, 8, 7, 6], [3, 1, 7, 8, 4, 6, 2, 9, 5], [8, 9, 6, 2, 7, 5, 4, 3, 1]]], [[[2, 0, 4, 0, 0, 0, 6, 7, 0], [6, 0, 0, 0, 4, 8, 0, 3, 0], [8, 1, 0, 0, 0, 7, 0, 0, 0], [0, 0, 2, 0, 9, 0, 8, 5, 0], [0, 6, 5, 8, 0, 1, 4, 0, 0], [3, 0, 0, 5, 2, 4, 7, 1, 6], [0, 2, 0, 0, 0, 0, 9, 6, 0], [4, 0, 6, 9, 0, 0, 3, 0, 0], [0, 0, 0, 0, 7, 0, 0, 0, 0]], [[2, 3, 4, 1, 5, 9, 6, 7, 8], [6, 5, 7, 2, 4, 8, 1, 3, 9], [8, 1, 9, 3, 6, 7, 5, 2, 4], [1, 4, 2, 7, 9, 6, 8, 5, 3], [7, 6, 5, 8, 3, 1, 4, 9, 2], [3, 9, 8, 5, 2, 4, 7, 1, 6], [5, 2, 1, 4, 8, 3, 9, 6, 7], [4, 7, 6, 9, 1, 2, 3, 8, 5], [9, 8, 3, 6, 7, 5, 2, 4, 1]]], [[[0, 0, 0, 0, 0, 9, 5, 8, 7], [7, 6, 4, 0, 5, 8, 0, 0, 0], [9, 0, 8, 0, 0, 7, 0, 0, 0], [4, 3, 0, 0, 0, 0, 0, 0, 0], [0, 0, 9, 0, 3, 4, 0, 0, 8], [0, 2, 5, 0, 9, 0, 0, 1, 0], [0, 0, 1, 0, 6, 0, 8, 7, 2], [3, 0, 2, 4, 7, 5, 9, 0, 0], [6, 9, 0, 0, 1, 2, 3, 0, 0]], [[2, 1, 3, 6, 4, 9, 5, 8, 7], [7, 6, 4, 1, 5, 8, 2, 3, 9], [9, 5, 8, 3, 2, 7, 1, 4, 6], [4, 3, 6, 2, 8, 1, 7, 9, 5], [1, 7, 9, 5, 3, 4, 6, 2, 8], [8, 2, 5, 7, 9, 6, 4, 1, 3], [5, 4, 1, 9, 6, 3, 8, 7, 2], [3, 8, 2, 4, 7, 5, 9, 6, 1], [6, 9, 7, 8, 1, 2, 3, 5, 4]]], [[[2, 5, 0, 4, 0, 8, 6, 0, 0], [1, 8, 0, 0, 2, 0, 0, 0, 0], [3, 9, 0, 0, 0, 6, 0, 7, 8], [4, 0, 1, 0, 8, 0, 7, 0, 0], [0, 2, 3, 0, 1, 0, 9, 0, 5], [5, 0, 0, 0, 0, 0, 1, 8, 0], [7, 1, 0, 0, 0, 9, 3, 0, 0], [0, 4, 0, 5, 6, 0, 0, 1, 0], [0, 0, 5, 8, 0, 1, 4, 9, 0]], [[2, 5, 7, 4, 9, 8, 6, 3, 1], [1, 8, 6, 3, 2, 7, 5, 4, 9], [3, 9, 4, 1, 5, 6, 2, 7, 8], [4, 6, 1, 9, 8, 5, 7, 2, 3], [8, 2, 3, 7, 1, 4, 9, 6, 5], [5, 7, 9, 6, 3, 2, 1, 8, 4], [7, 1, 8, 2, 4, 9, 3, 5, 6], [9, 4, 2, 5, 6, 3, 8, 1, 7], [6, 3, 5, 8, 7, 1, 4, 9, 2]]], [[[1, 0, 0, 0, 0, 9, 0, 0, 7], [0, 0, 8, 1, 7, 0, 0, 0, 9], [9, 0, 0, 2, 0, 0, 0, 6, 4], [2, 9, 0, 4, 1, 0, 7, 0, 8], [6, 0, 5, 0, 0, 3, 4, 9, 0], [0, 0, 0, 0, 9, 2, 3, 0, 0], [8, 0, 0, 3, 0, 0, 0, 0, 0], [0, 2, 1, 0, 0, 0, 9, 0, 5], [5, 0, 0, 0, 0, 0, 8, 7, 0]], [[1, 3, 2, 6, 4, 9, 5, 8, 7], [4, 6, 8, 1, 7, 5, 2, 3, 9], [9, 5, 7, 2, 3, 8, 1, 6, 4], [2, 9, 3, 4, 1, 6, 7, 5, 8], [6, 1, 5, 7, 8, 3, 4, 9, 2], [7, 8, 4, 5, 9, 2, 3, 1, 6], [8, 7, 9, 3, 5, 4, 6, 2, 1], [3, 2, 1, 8, 6, 7, 9, 4, 5], [5, 4, 6, 9, 2, 1, 8, 7, 3]]], [[[4, 0, 7, 1, 0, 3, 0, 0, 0], [6, 0, 0, 0, 0, 0, 0, 1, 7], [5, 0, 0, 8, 4, 0, 2, 0, 6], [0, 8, 2, 0, 3, 0, 6, 0, 0], [0, 0, 4, 6, 0, 0, 0, 0, 0], [7, 0, 6, 9, 0, 2, 1, 0, 3], [0, 7, 1, 5, 2, 9, 0, 0, 4], [0, 4, 0, 0, 1, 0, 7, 0, 9], [0, 0, 0, 4, 7, 8, 0, 0, 1]], [[4, 2, 7, 1, 6, 3, 9, 5, 8], [6, 3, 8, 2, 9, 5, 4, 1, 7], [5, 1, 9, 8, 4, 7, 2, 3, 6], [1, 8, 2, 7, 3, 4, 6, 9, 5], [3, 9, 4, 6, 5, 1, 8, 7, 2], [7, 5, 6, 9, 8, 2, 1, 4, 3], [8, 7, 1, 5, 2, 9, 3, 6, 4], [2, 4, 5, 3, 1, 6, 7, 8, 9], [9, 6, 3, 4, 7, 8, 5, 2, 1]]], [[[0, 0, 0, 0, 0, 3, 8, 0, 7], [1, 9, 0, 4, 5, 0, 3, 0, 6], [6, 0, 0, 2, 0, 9, 0, 4, 5], [0, 0, 4, 9, 6, 0, 0, 8, 0], [8, 1, 9, 0, 3, 0, 0, 0, 4], [0, 6, 3, 0, 0, 0, 0, 1, 0], [3, 5, 1, 0, 0, 4, 9, 0, 8], [4, 0, 0, 0, 0, 6, 0, 0, 0], [0, 7, 6, 0, 0, 0, 4, 0, 0]], [[2, 4, 5, 6, 1, 3, 8, 9, 7], [1, 9, 7, 4, 5, 8, 3, 2, 6], [6, 3, 8, 2, 7, 9, 1, 4, 5], [7, 2, 4, 9, 6, 1, 5, 8, 3], [8, 1, 9, 5, 3, 2, 6, 7, 4], [5, 6, 3, 8, 4, 7, 2, 1, 9], [3, 5, 1, 7, 2, 4, 9, 6, 8], [4, 8, 2, 3, 9, 6, 7, 5, 1], [9, 7, 6, 1, 8, 5, 4, 3, 2]]], [[[2, 0, 4, 7, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 5], [0, 0, 5, 0, 1, 0, 0, 0, 4], [4, 0, 0, 9, 0, 0, 6, 2, 7], [8, 2, 6, 3, 7, 0, 0, 0, 0], [0, 5, 9, 4, 0, 0, 3, 1, 8], [5, 4, 0, 1, 0, 9, 0, 0, 3], [0, 9, 0, 5, 2, 0, 8, 4, 1], [0, 8, 0, 0, 4, 7, 0, 9, 2]], [[2, 3, 4, 7, 9, 5, 1, 8, 6], [1, 6, 8, 2, 3, 4, 9, 7, 5], [9, 7, 5, 8, 1, 6, 2, 3, 4], [4, 1, 3, 9, 5, 8, 6, 2, 7], [8, 2, 6, 3, 7, 1, 4, 5, 9], [7, 5, 9, 4, 6, 2, 3, 1, 8], [5, 4, 2, 1, 8, 9, 7, 6, 3], [6, 9, 7, 5, 2, 3, 8, 4, 1], [3, 8, 1, 6, 4, 7, 5, 9, 2]]], [[[2, 0, 1, 8, 0, 0, 0, 7, 0], [0, 0, 0, 0, 7, 0, 6, 1, 0], [0, 0, 6, 1, 0, 0, 5, 0, 0], [7, 0, 2, 3, 0, 0, 4, 6, 0], [1, 0, 0, 7, 0, 4, 0, 3, 0], [8, 4, 3, 0, 0, 2, 1, 0, 0], [6, 0, 4, 5, 0, 7, 0, 0, 3], [0, 0, 0, 4, 1, 8, 0, 5, 6], [0, 0, 7, 0, 6, 3, 0, 4, 0]], [[2, 5, 1, 8, 4, 6, 3, 7, 9], [9, 3, 8, 2, 7, 5, 6, 1, 4], [4, 7, 6, 1, 3, 9, 5, 2, 8], [7, 9, 2, 3, 8, 1, 4, 6, 5], [1, 6, 5, 7, 9, 4, 8, 3, 2], [8, 4, 3, 6, 5, 2, 1, 9, 7], [6, 1, 4, 5, 2, 7, 9, 8, 3], [3, 2, 9, 4, 1, 8, 7, 5, 6], [5, 8, 7, 9, 6, 3, 2, 4, 1]]], [[[3, 0, 2, 0, 8, 7, 0, 9, 0], [6, 0, 4, 0, 0, 1, 0, 0, 5], [0, 0, 8, 0, 9, 0, 6, 0, 3], [5, 0, 0, 0, 7, 0, 0, 0, 0], [8, 4, 6, 3, 0, 9, 0, 0, 1], [0, 1, 0, 5, 0, 4, 2, 3, 8], [0, 8, 0, 9, 4, 6, 0, 1, 0], [7, 3, 1, 0, 0, 0, 0, 6, 0], [0, 0, 9, 0, 0, 0, 5, 0, 2]], [[3, 5, 2, 6, 8, 7, 1, 9, 4], [6, 9, 4, 2, 3, 1, 8, 7, 5], [1, 7, 8, 4, 9, 5, 6, 2, 3], [5, 2, 3, 1, 7, 8, 9, 4, 6], [8, 4, 6, 3, 2, 9, 7, 5, 1], [9, 1, 7, 5, 6, 4, 2, 3, 8], [2, 8, 5, 9, 4, 6, 3, 1, 7], [7, 3, 1, 8, 5, 2, 4, 6, 9], [4, 6, 9, 7, 1, 3, 5, 8, 2]]], [[[1, 0, 0, 0, 9, 0, 3, 7, 8], [8, 0, 0, 1, 0, 3, 0, 0, 0], [0, 0, 6, 0, 4, 8, 9, 0, 2], [0, 0, 0, 4, 0, 0, 6, 3, 0], [0, 0, 3, 0, 6, 0, 7, 0, 0], [5, 6, 7, 3, 0, 0, 1, 2, 0], [0, 3, 8, 0, 7, 0, 0, 4, 1], [0, 0, 2, 0, 1, 0, 8, 6, 3], [6, 1, 5, 0, 0, 4, 0, 0, 7]], [[1, 2, 4, 5, 9, 6, 3, 7, 8], [8, 7, 9, 1, 2, 3, 4, 5, 6], [3, 5, 6, 7, 4, 8, 9, 1, 2], [2, 8, 1, 4, 5, 7, 6, 3, 9], [4, 9, 3, 2, 6, 1, 7, 8, 5], [5, 6, 7, 3, 8, 9, 1, 2, 4], [9, 3, 8, 6, 7, 2, 5, 4, 1], [7, 4, 2, 9, 1, 5, 8, 6, 3], [6, 1, 5, 8, 3, 4, 2, 9, 7]]], [[[2, 0, 0, 3, 0, 8, 9, 1, 0], [6, 1, 8, 0, 0, 0, 3, 7, 0], [0, 9, 4, 0, 0, 7, 0, 0, 0], [0, 0, 0, 0, 0, 0, 8, 6, 0], [5, 8, 0, 2, 1, 6, 4, 0, 0], [0, 0, 6, 0, 0, 0, 1, 0, 0], [1, 0, 7, 0, 9, 0, 0, 0, 0], [8, 0, 0, 6, 0, 0, 5, 0, 2], [0, 6, 0, 4, 3, 0, 7, 8, 1]], [[2, 7, 5, 3, 4, 8, 9, 1, 6], [6, 1, 8, 5, 2, 9, 3, 7, 4], [3, 9, 4, 1, 6, 7, 2, 5, 8], [4, 2, 1, 7, 5, 3, 8, 6, 9], [5, 8, 9, 2, 1, 6, 4, 3, 7], [7, 3, 6, 9, 8, 4, 1, 2, 5], [1, 5, 7, 8, 9, 2, 6, 4, 3], [8, 4, 3, 6, 7, 1, 5, 9, 2], [9, 6, 2, 4, 3, 5, 7, 8, 1]]], [[[6, 4, 1, 0, 3, 8, 9, 7, 0], [0, 2, 0, 5, 0, 9, 0, 6, 4], [0, 5, 9, 0, 0, 0, 0, 3, 0], [0, 0, 4, 0, 0, 6, 0, 0, 7], [0, 6, 0, 0, 8, 0, 0, 0, 2], [0, 0, 0, 3, 0, 0, 6, 5, 0], [4, 0, 0, 0, 0, 5, 7, 0, 0], [5, 0, 0, 0, 0, 0, 4, 9, 1], [8, 9, 0, 7, 0, 0, 0, 0, 0]], [[6, 4, 1, 2, 3, 8, 9, 7, 5], [3, 2, 8, 5, 7, 9, 1, 6, 4], [7, 5, 9, 4, 6, 1, 2, 3, 8], [2, 3, 4, 9, 5, 6, 8, 1, 7], [9, 6, 5, 1, 8, 7, 3, 4, 2], [1, 8, 7, 3, 4, 2, 6, 5, 9], [4, 1, 2, 6, 9, 5, 7, 8, 3], [5, 7, 6, 8, 2, 3, 4, 9, 1], [8, 9, 3, 7, 1, 4, 5, 2, 6]]], [[[0, 0, 4, 3, 0, 0, 7, 0, 0], [0, 0, 6, 2, 0, 7, 0, 0, 0], [0, 0, 7, 9, 0, 1, 2, 0, 4], [2, 0, 1, 7, 3, 0, 9, 8, 5], [0, 7, 0, 0, 0, 2, 3, 0, 6], [6, 0, 0, 0, 5, 0, 1, 7, 2], [0, 0, 3, 8, 0, 4, 0, 0, 1], [0, 0, 2, 0, 7, 0, 0, 5, 3], [9, 6, 0, 5, 0, 3, 4, 0, 0]], [[1, 2, 4, 3, 8, 5, 7, 6, 9], [3, 9, 6, 2, 4, 7, 5, 1, 8], [5, 8, 7, 9, 6, 1, 2, 3, 4], [2, 4, 1, 7, 3, 6, 9, 8, 5], [8, 7, 5, 1, 9, 2, 3, 4, 6], [6, 3, 9, 4, 5, 8, 1, 7, 2], [7, 5, 3, 8, 2, 4, 6, 9, 1], [4, 1, 2, 6, 7, 9, 8, 5, 3], [9, 6, 8, 5, 1, 3, 4, 2, 7]]]]
        self.leveldata = self.loadleveldata()
        self.level = -1

        
        self.makegui()
    def makegui(self):
        # main menu
        ui.styleset(text_textcol = (40,40,60))
        ui.maketext(0,0,'{sudoku} Sudoku {logo}',100,anchor=('w/2','h/4'),center=True)
        ui.makebutton(0,-30,'Sudoku',55,lambda: ui.movemenu('sudoku select','left'),anchor=('w/2','h/2'),center=True)
        ui.makebutton(0,30,'Minesweeper',55,lambda: ui.movemenu('mine select','left'),anchor=('w/2','h/2'),center=True)

        ui.maketext(0,40,'Sudoku Level Select',60,'sudoku select',anchor=('w/2',0),center=True,backingdraw=True,layer=3,horizontalspacing=300,verticalspacing=20)

        # level select menu
        data = []
        for i,a in enumerate(self.levels):
            func = funcersl(self,i)
            playbutton = ui.makebutton(0,0,'Play',30,verticalspacing=6,command=func.func)
##            progress = ui.makeslider(0,0,200,32,containedslider=True,button=ui.makebutton(0,0,'',backingdraw=False,borderdraw=False,dragable=False,width=0,height=0),dragable=False,startp=random.randint(0,100),ID=f'progslider{i}',bounditems=[ui.maketext( ])
            progress = ui.maketext(0,0,'-%',30,ID=f'progslider{i}',textcenter=True)
            data.append([i+1,progress,playbutton])
        
        ui.maketable(0,100,data,['Level',''],'sudoku select',anchor=('w/2',0),objanchor=('w/2',0),boxwidth=[150,200,120],ID='sudokuleveltable')
        self.refreshleveltable()

        ui.makescroller(0,100,500,scrollbind=['sudokuleveltable'],anchor=('w',0),objanchor=('w',0),menu='sudoku select',maxp=500,pageheight=300)



        # sudoku grid
        ui.maketable(0,0,[],boxwidth=50,boxheight=50,scalesize=True,scaleby='vertical',anchor=('w/2','h/2'),center=True,menu='sudoku level',ID='sudoku grid')
        ui.maketext(0,-300,'Level: -',80,'sudoku level','sudoku level display',anchor=('w/2','h/2'),center=True,scaleby='vertical')
        ui.maketext(0,300,'-%',80,'sudoku level','sudoku progress display',anchor=('w/2','h/2'),center=True,scaleby='vertical',backingdraw=True)

        # clear button/pop up
        ui.makewindowedmenu(0,40,250,150,'clear confirm','sudoku level',anchor=('w/2',0),objanchor=('w/2',0))
        ui.makebutton(-180,300,'Clear Grid',35,lambda: ui.movemenu('clear confirm','down'),'sudoku level',anchor=('w/2','h/2'),center=True,scaleby='vertical',verticalspacing=8,horizontalspacing=8,maxwidth=100)
        ui.maketext(0,40,'Are You Sure?',40,'clear confirm',center=True,anchor=('w/2',0),backingcol=(47, 86, 179))
        ui.makebutton(-50,0,'No',40,ui.menuback,'clear confirm',anchor=('w/2','h/3*2'),center=True)
        ui.makebutton(50,0,'Yes',40,self.cleargrid,'clear confirm',anchor=('w/2','h/3*2'),center=True)

        # clue button/pop up
        ui.makebutton(180,300,'Get Clue',35,lambda: ui.movemenu('clues','down'),'sudoku level',anchor=('w/2','h/2'),center=True,scaleby='vertical',verticalspacing=8,horizontalspacing=8,maxwidth=100)
        ui.makewindowedmenu(0,40,250,140,'clues','sudoku level',anchor=('w/2',0),objanchor=('w/2',0))
        ui.maketext(15,15,'Show Wrong',32,'clues',maxwidth=110,backingcol=(47, 86, 179))
        ui.makebutton(105,25,'One',35,lambda: self.findwrong(1),'clues')
        ui.makebutton(180,25,'All',35,lambda: self.findwrong(1000),'clues')
        ui.maketext(20,75,'Get Clue',32,'clues',maxwidth=80,backingcol=(47, 86, 179))
        ui.makebutton(85,80,'Easy',35,lambda: self.findclue(True),'clues')
        ui.makebutton(165,80,'Hard',35,lambda: self.findclue(False),'clues')

        # minesweeper gui
        ui.maketext(0,80,'Minesweeper Gamemode Select',60,'mine select',anchor=('w/2',0),center=True,maxwidth=450,textcenter=True)
        ui.maketext(0,0,'2D',55,'mine select',anchor=('w*0.25','h*0.4'),center=True)
        ui.makebutton(0,50,'Easy - 10x10',40,lambda: self.openmine(10,1,10,0.2),'mine select',anchor=('w*0.25','h*0.4'),center=True)
        ui.makebutton(0,100,'Medium - 15x15',40,lambda: self.openmine(15,1,15,0.25),'mine select',anchor=('w*0.25','h*0.4'),center=True)
        ui.makebutton(0,150,'Hard - 20x20',40,lambda: self.openmine(20,1,20,0.3),'mine select',anchor=('w*0.25','h*0.4'),center=True)
        ui.maketext(0,0,'3D',55,'mine select',anchor=('w*0.5','h*0.4'),center=True)
        ui.makebutton(0,50,'Easy - 4x4x4',40,lambda: self.openmine(4,4,4,0.1),'mine select',anchor=('w*0.5','h*0.4'),center=True)
        ui.makebutton(0,100,'Medium - 6x6x6',40,lambda: self.openmine(6,6,6,0.1),'mine select',anchor=('w*0.5','h*0.4'),center=True)
        ui.makebutton(0,150,'Hard - 8x8x8',40,lambda: self.openmine(8,8,8,0.1),'mine select',anchor=('w*0.5','h*0.4'),center=True)

        # custom game sliders/gui
        ui.maketext(0,0,'Custom',55,'mine select',anchor=('w*0.75','h*0.4'),center=True)
        ui.makeslider(50,50,120,15,15,'mine select',anchor=('w*0.75','h*0.4'),center=True,startp=5,increment=1,minp=1,command=self.updatecustomsliders,ID='widthslider')
        ui.makeslider(50,90,120,15,15,'mine select',anchor=('w*0.75','h*0.4'),center=True,startp=5,increment=1,minp=1,command=self.updatecustomsliders,ID='lengthslider')
        ui.makeslider(50,130,120,15,15,'mine select',anchor=('w*0.75','h*0.4'),center=True,startp=1,increment=1,minp=1,command=self.updatecustomsliders,ID='layerslider')
        ui.makeslider(50,170,120,15,0.9,'mine select',anchor=('w*0.75','h*0.4'),center=True,startp=0.2,increment=0.01,minp=0.01,command=self.updatecustomsliders,ID='coverslider')
        ui.maketext(-25,50,'Width: 5',32,'mine select',anchor=('w*0.75','h*0.4'),objanchor=('w','h/2'),ID='widthslider text')
        ui.maketext(-25,90,'Length: 5',32,'mine select',anchor=('w*0.75','h*0.4'),objanchor=('w','h/2'),ID='lengthslider text')
        ui.maketext(-25,130,'Layers: 1',32,'mine select',anchor=('w*0.75','h*0.4'),objanchor=('w','h/2'),ID='layerslider text')
        ui.maketext(-25,170,'Bombs: 20%',32,'mine select',anchor=('w*0.75','h*0.4'),objanchor=('w','h/2'),ID='coverslider text')
        ui.makebutton(-10,215,'Play Custom',45,lambda: self.openmine(-1,-1,-1,-1),'mine select',anchor=('w*0.75','h*0.4'),center=True)
        
        # minefield game
        ui.styleset(textsize=50)
        ui.maketable(0,0,[],[],boxwidth=50,boxheight=50,scalesize=True,scaleby='vertical',anchor=('w/2','h/2'),center=True,menu='mine game',ID='minefield',linesize=0,textsize=50,bounditems=[
        ui.maketable(40,0,[],[ui.maketext(0,0,'0',40,ID='bomb count',textcenter=True)],ID='field layer',anchor=('w','h/2'),objanchor=(0,'h/2'),boxwidth=50,boxheight=50,col=(140,140,140))
            ])
        
        
        # win/lose menu
        ui.makewindowedmenu(0,0,200,150,'field layer','field layer')
        ui.maketext(0,40,'Are You Sure?',40,'clear confirm',center=True,anchor=('w/2',0),backingcol=(47, 86, 179))


    def makesudokutableinput(self,grid):
        trueg = grid
        grid = Sudoku.possible_map(grid)
        mini = int(len(grid)**0.5)
        textgrid = []
        for j,y in enumerate(grid):
            textgrid.append([])
            for i,x in enumerate(y):
                st = ''
                for a in x: st+=str(a)
                st = textcolfilter(st)
                backingcol = pyui.Style.defaults['col']
                if ((j//mini)*mini+i//mini)%2 == 0: backingcol = [backingcol[0],backingcol[1]+20,backingcol[2]]
                if len(x) == 1 and trueg[j][i]!=0:
                    textgrid[-1].append(ui.maketext(0,0,st,60,textcenter=True,backingcol=backingcol))
                else:
                    func = funcerus(self,i,j)
                    textgrid[-1].append(ui.maketextbox(0,0,command=func.func,textsize=60,chrlimit=1,backingcol=pyui.shiftcolor(backingcol,-8),col=backingcol,linelimit=1,textcenter=True,numsonly=True,imgdisplay=True,textcol=(43,43,43),commandifkey=True,bounditems=[ui.maketextbox(3,3,textsize=15,numsonly=True,lines=1,width=44,height=15,border=0,spacing=2,col=backingcol,backingdraw=False,borderdraw=False,selectbordersize=0,scalesize=True,scaleby='vertical')]))
        return textgrid

    def updatesudoku(self,x,y,updateall=True):
        box = ui.IDs['sudoku grid'].tableimages[y][x][1]
        box.chrlimit = 1
        box.text = box.text.replace('0','')
        if '"' in box.text:
            chrs = '123456789'
            if box.text[0] in chrs:
                box.text = box.text[0]
            elif box.text[-1] in chrs:
                box.text = box.text[-1]
        if len(box.text) == 0:
            box.bounditems[0].enabled = True
        else:
            box.bounditems[0].enabled = False
            if len(box.text) == 1:
                box.text = textcolfilter(box.text)
                box.typingcursor = -1
                box.chrlimit = len(box.text)
            else:
                box.text = ''
                box.bounditems[0].enabled = True
        if pyui.RECT in [type(a) for a in box.bounditems]:
            ui.delete(box.bounditems[[type(a) for a in box.bounditems].index(pyui.RECT)].ID)
        if updateall:
            self.updategrid()
    def updategrid(self):
        grid = []
        for y in ui.IDs['sudoku grid'].tableimages:
            grid.append([])
            for x in y:
                if x[1].text == '':
                    grid[-1].append(0)
                else:
                    grid[-1].append(int(x[1].text[2]))
        self.grid = grid
        self.leveldata[self.level][1] = grid
        if Sudoku.valid(grid) and Sudoku.checksolved(grid):
            self.solved()
        else:
            self.leveldata[self.level][0] = Sudoku.checksolveamount(grid,self.levels[self.level][0])
            ui.IDs['sudoku progress display'].text = f'{self.leveldata[self.level][0]}%'
            ui.IDs['sudoku progress display'].refresh(ui)
        self.refreshleveltable()

    def solved(self):
        self.leveldata[self.level][0] = 'Solved!'
        ui.IDs['sudoku progress display'].text = f'{self.leveldata[self.level][0]}'
        ui.IDs['sudoku progress display'].refresh(ui)
                    
    def refreshleveltable(self):
        fade = pyui.genfade([(255,0,0),(0,235,0)],101)
        table = ui.IDs['sudokuleveltable']
        for a in table.bounditems:
            if 'progslider' in a.ID:
                a.prog = self.leveldata[int(a.ID.removeprefix('progslider'))][0]
                if a.prog == 'Solved!':
                    a.text = a.prog
                    a.col = fade[-1]
                else:
                    a.prog = int(a.prog)
                    a.text = f'{a.prog}%'
                    a.col = fade[a.prog]
                a.refresh(ui)
        
    def opensudoku(self,level):
        self.level = level
        ui.movemenu('sudoku level','left')
        grid = ui.IDs['sudoku grid']
        grid.wipe(ui)
        grid.data = self.makesudokutableinput(self.levels[level][0])
        grid.boxwidth = 50
        grid.boxheight = 50
        grid.refresh(ui)
        ui.IDs['sudoku level display'].text = f'Level: {level+1}'
        ui.IDs['sudoku level display'].refresh(ui)
        ui.IDs['sudoku progress display'].text = f'{self.leveldata[level][0]}%'
        ui.IDs['sudoku progress display'].refresh(ui)
        for y,a in enumerate(grid.tableimages):
            for x,b in enumerate(a):
                if type(b[1]) == pyui.TEXTBOX:
                    if self.leveldata[level][1][y][x] != 0:
                        b[1].text = str(self.leveldata[level][1][y][x])
                        self.updatesudoku(x,y,False)
                        b[1].refresh(ui)
        self.updategrid()

    def cleargrid(self):
        grid = ui.IDs['sudoku grid']
        for y,a in enumerate(grid.tableimages):
            for x,b in enumerate(a):
                if type(b[1]) == pyui.TEXTBOX:
                    if self.leveldata[self.level][1][y][x] != 0:
                        b[1].text = '0'
                        self.updatesudoku(x,y,False)
                        b[1].refresh(ui)
        self.updategrid()

    def findclue(self,disptext):
        clues = Sudoku.clue(self.grid)
        if clues == []:
            txt = 'No Clues Found'
        else:
            clue = random.choice(clues)
            key = ['row','column','box']
            txt = f'A {clue[2]} can go in this {key[clue[3]]}'
            if clue[2] == 8:
                txt = txt.replace('A','An',1)
            for a in clue[4]:
                self.highlight(a[0],a[1],(20,220,10,70),5)
        if disptext:       
            self.makepopup(txt)
            
    def findwrong(self,limit):
        wrong = []
        for y,a in enumerate(self.grid):
            for x,b in enumerate(a):
                if b != 0 and b!=self.levels[self.level][1][y][x]:
                    wrong.append([x,y])
        random.shuffle(wrong)
        count = 0
        loops = 0
        while count<min(limit,len(wrong)):
            if self.highlight(wrong[count][0],wrong[count][1]):
                count+=1
            loops+=1
            if loops>60: break
        if count == 0:
            self.makepopup('No incorrect Values')
        ui.menuback()
            
    def makepopup(self,txt):
        ui.delete('sudoku pop up',False)
        ui.maketext(0,10,txt,45,'sudoku level',backingdraw=True,killtime=5,ID='sudoku pop up',anchor=('w/2',0),objanchor=('w/2',0))
    def highlight(self,x,y,glowcol=(240,40,40,90),killtime=30):
        obj = ui.IDs['sudoku grid'].tableimages[y][x][1]
        if not (pyui.RECT in [type(a) for a in obj.bounditems]):
            obj.binditem(ui.makerect(0,0,50,50,backingdraw=False,glow=2,glowcol=glowcol,killtime=killtime,scaleby='vertical'))
            obj.resetcords(ui)
            return True
        return False
    def loadleveldata(self):
        if not os.path.isfile(pyui.resourcepath('data.json')):
            data = {}
            for i,a in enumerate(self.levels):
                data[i] = [0,a[0],False]
            with open('data.json','w') as f:
                json.dump(data,f)
        with open('data.json','r') as f:
            out = json.load(f)
        data = {}
        for a in list(out):
            data[int(a)] = out[a]
        return data
    def storeleveldata(self):
        with open('data.json','w') as f:
            json.dump(self.leveldata,f)

    def openmine(self,x,y,z,cover):
        if x == -1: x = ui.IDs['widthslider'].slider
        if y == -1: y = ui.IDs['layerslider'].slider
        if z == -1: z = ui.IDs['lengthslider'].slider
        if cover == -1: cover = ui.IDs['coverslider'].slider
        self.bombcoverage = cover
        ui.IDs['minefield'].wipe(ui)
        self.field = Minesweeper.gengrid(x,y,z,cover)
        self.fieldmap = [[[0 for c in range(x)] for b in range(z)] for a in range(y)]

        data = copy.deepcopy(self.field)
        
        for a in range(y):
            for b in range(z):
                for c in range(x):
                    num = data[a][b][c]
                    func = funcermc(self,c,a,b)
                    func2 = funcerpf(self,c,a,b)
                    data[a][b][c] = ui.maketext(-100,-100,'',50,img=Minesweeper.genimage(self.field,c,a,b,self.fieldmap),scaleby='vertical',border=0,verticalspacing=0,horizontalspacing=0,command=func.func,bounditems=[
                        ui.maketext(0,0,'',width=50,height=50,command=func2.func,clicktype=2,scaleby='vertical')])
        self.fieldlayer = 0
        ui.IDs['minefield'].data = data[self.fieldlayer]
        ui.IDs['minefield'].refresh(ui)
        self.freshfield = True

        ui.IDs['field layer'].wipe(ui,False)
        data = []
        if y != 1:
            IDs = [f'layerselector{i}' for i in range(y)]
            for a in range(y):
                func = funcerml(self,a)
                data.append([ui.makebutton(0,0,'',command=func.func,col=(100,200,100),togglecol=(151,150,150),toggleable=True,bindtoggle=IDs,ID=IDs[a],backingcol=(130,130,130),toggle=False)])
            data[self.fieldlayer][self.fieldlayer].toggle = True
            
        ui.IDs['bomb count'].text = str(round(x*y*z*cover))
        data.reverse()
        ui.IDs['field layer'].data = data
        ui.IDs['field layer'].refresh(ui)

        
        ui.movemenu('mine game','left')
    def mineclicked(self,x,y,z):
        if self.fieldmap[y][z][x] != 2:
            if self.freshfield:
                while self.field[y][z][x] != 0:
                    self.field = Minesweeper.gengrid(len(self.field[0][0]),len(self.field),len(self.field[0]),self.bombcoverage)
                self.movelayer(self.fieldlayer)

            self.freshfield = False
            if self.field[y][z][x] == -1:
                print('BOMB - YOU FAILED')
            self.fieldmap[y][z][x] = 1
            self.updatemine(x,y,z)
    def updatemine(self,x,y,z):
        doubleupdate = []
        if self.field[y][z][x] == 0 and self.fieldmap[y][z][x] == 1:
            for a in range(-1,2):
                for b in range(-1,2):
                    for c in range(-1,2):
                        if not(a==0 and b==0 and c==0):
                            if Minesweeper.inbox(self.field,x+c,y+a,z+b) and self.fieldmap[y+a][z+b][x+c] == 0:
                                self.fieldmap[y+a][z+b][x+c] = 1
                                self.updatemine(x+c,y+a,z+b)
                                doubleupdate.append((x+c,y+a,z+b))
        if self.fieldlayer == y:
            ui.IDs['minefield'].data[z][x].img = Minesweeper.genimage(self.field,x,y,z,self.fieldmap)
            ui.IDs['minefield'].data[z][x].refresh(ui)
        for a in doubleupdate:
            self.updatemine(a[0],a[1],a[2])
    def placeflag(self,x,y,z):
        if not self.freshfield:
            if self.fieldmap[y][z][x] == 2:
                self.fieldmap[y][z][x] = 0
                ui.IDs['bomb count'].text = str(int(ui.IDs['bomb count'].text)+1)
            elif self.fieldmap[y][z][x] == 0:
                self.fieldmap[y][z][x] = 2
                ui.IDs['bomb count'].text = str(int(ui.IDs['bomb count'].text)-1)
            else:
                return
            ui.IDs['bomb count'].refresh(ui)
            self.updatemine(x,y,z)
            if self.checkfieldsolved():
                print('solved')
    def checkfieldsolved(self):
        solved = True
        for a in range(len(self.field)):
            for b in range(len(self.field[a])):
                for c in range(len(self.field[a][b])):
                    if self.field[a][b][c] == -1 and self.fieldmap[a][b][c] != 2:
                        solved = False
                    elif self.field[a][b][c] != -1 and self.fieldmap[a][b][c] == 2:
                        solved = False
        return solved
        
    def movelayer(self,level):
        if len(self.field)!=1:
            ui.IDs['field layer'].data[len(self.field)-level-1][0].toggle = True
        self.fieldlayer = level
        table = ui.IDs['minefield']
        for z in range(len(table.data)):
            for x in range(len(table.data[z])):
                func = funcermc(self,x,self.fieldlayer,z)
                func2 = funcerpf(self,x,self.fieldlayer,z)
                table.data[z][x].command = func.func
                table.data[z][x].img = Minesweeper.genimage(self.field,x,self.fieldlayer,z,self.fieldmap)
                table.data[z][x].refresh(ui)
                table.data[z][x].bounditems[0].command = func2.func
    def updatecustomsliders(self):
        ui.IDs['widthslider text'].text = f"Width: {ui.IDs['widthslider'].slider}"
        ui.IDs['lengthslider text'].text = f"Length: {ui.IDs['lengthslider'].slider}"
        ui.IDs['layerslider text'].text = f"Layers: {ui.IDs['layerslider'].slider}"
        ui.IDs['coverslider text'].text = f"Bombs: {int(ui.IDs['coverslider'].slider*100)}%"
        ui.IDs['widthslider text'].refresh(ui)
        ui.IDs['lengthslider text'].refresh(ui)
        ui.IDs['layerslider text'].refresh(ui)
        ui.IDs['coverslider text'].refresh(ui)

main = Main()

while not done:
    pygameeventget = ui.loadtickdata()
    for event in pygameeventget:
        if event.type == pygame.QUIT:
            main.storeleveldata()
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if ui.activemenu == 'sudoku level':
                    main.storeleveldata()
                ui.menuback()
    screen.fill(pyui.Style.wallpapercol)
    
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit()



















