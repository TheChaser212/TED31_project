#-*- coding: utf-8 -*-
from appJar import gui
import random

class item(object):
    def __init__(self,name,desc):
        self.name = name
        self.desc = desc
        
    def description(self):
        return self.desc
        
class weapon(item): #subclass of item
    def __init__(self,name,desc,damage,attackTypes):
        super().__init__(name,desc) #calls init of item class
        self.damage = damage
        self.attackTypes = attackTypes
    
    def description(self):
        return "%s, it does %i damage"%(super().description(),self.damage)

class armor(item):
    def __init__(self,name,desc,armor,slot):
        super().__init__(name,desc) #calls init of item class
        self.armor = armor
        self.slot = slot
    
    def description(self):
        return "%s, it blocks %i damage and you wear it on your %s"%(super().description(),self.armor,self.slot.lower())


plains = {"color":"green","icon":"-"}
mountain = {"color":"grey","icon":"▲"}
desert = {"color":"yellow","icon":"⁕"}
forest = {"color":"green","icon":"⇑"}
ocean = {"color":"blue","icon":"≈"}

biomes = [plains,mountain,desert,forest,ocean]


player = {"color":"white",
          "icon":"X",
          "posX":1,
          "posY":1,
          "inventory":[weapon("Sword","A stabby metal object",10,["Slash","Stab"]),
                       armor("Chestplate","A large hunk of metal",27,"Body")]}

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
            name = str(a)+" "+str(b)
            if((player["posY"] == a) and (player["posX"] == b)):
                x = player        
            map.create_rectangle(b*iconSize, a*iconSize, b*iconSize+iconSize, a*iconSize+iconSize,fill=x["color"])
            map.create_text((b*iconSize)+(iconSize/2), (a*iconSize)+(iconSize/2),text = x["icon"])

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

def showInventory():
    for i in player["inventory"]:
        print(i.name)
        print(i.description())

#load()
app = gui("newMap")
app.setSticky("NEWS")
app.setStretch("both")

app.startScrollPane("mapPane")
map = app.addCanvas("map")
map.config(height=iconSize*(len(gameMap)+1))
app.stopScrollPane()

updateMap()

app.bindKeys(["<Left>","<Right>","<Up>","<Down>"], move)
app.bindKeys(["i","<Tab>"], showInventory)
app.go()