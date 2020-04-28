#-*- coding: utf-8 -*-
from appJar import gui
import random

plains = {"color":"green","icon":"-"}
mountain = {"color":"grey","icon":"▲"}
desert = {"color":"yellow","icon":"⁕"}
forest = {"color":"green","icon":"⇑"}
ocean = {"color":"blue","icon":"≈"}

player = {"color":"white","icon":"X","posX":1,"posY":1}

biomes = [plains,mountain,desert,forest,ocean]
iconSize = 20
gameMap = []
mapSize = 15
for y in range(mapSize):
    gameMap.append([])
    for x in range(mapSize):
        gameMap[y].append(random.choice(biomes))

"""
def load():
    global player
    save = open("gamesave.txt", "r")
    #mapline = save.readline()
    #gameMap = mapline
    lines = save.readlines()
    for line in lines:
        splitline = line.strip().split(":")
        try:
            splitline[1] = int(splitline[1])
        except:
            pass
        print(splitline)
        player[splitline[0]] = splitline[1] 
    save.close()

def save():
    save = open("gamesave.txt", "w")
    save.write("")
    save.close()    
    
    save = open("gamesave.txt", "a")
    #save.write(str(gameMap))
    for item in player:
        save.write(str(item)+":"+str(player[item])+'\n')
    save.close()
"""
def updateMap():
    app.clearCanvas("map")
    a = 0
    for y in gameMap:
        a+=1
        b=0   
        for x in y:
            b+=1
            if((player["posY"] == a) and (player["posX"] == b)):
                x = player        
            name = str(a)+" "+str(b)
            app.addCanvasRectangle("map", b*iconSize, a*iconSize, iconSize, iconSize,fill=x["color"],width=0)
            app.addCanvasText("map", (b*iconSize)+(iconSize/2), (a*iconSize)+(iconSize/2), x["icon"])

def move(key):
    if(key == "<Left>"):
        if(player["posX"] != 1):
            player["posX"] -= 1
    elif(key == "<Right>"):
        if(player["posX"] != mapSize):
            player["posX"] += 1
    elif(key == "<Up>"):
        if(player["posY"] != 1):
            player["posY"] -= 1    
    elif(key == "<Down>"):
        if(player["posY"] != mapSize):
            player["posY"] += 1
    updateMap()
    #save()
    
#load()
app = gui("newMap","500x500")

app.addCanvas("map")
app.setSticky("nesw")
app.setStretch("both")

updateMap()
app.bindKeys(["<Left>","<Right>","<Up>","<Down>"], move)
app.go()