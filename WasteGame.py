#-*- coding: utf-8 -*-
from appJar import gui
import random
import pickle

"""
Define classes
"""
class Item(object):
    def __init__(self,name,desc):
        self.name = name
        self.desc = desc
        
    def description(self):
        return self.desc
        
class Weapon(Item): #subclass of item
    def __init__(self,name,desc,damage,attackTypes):
        super().__init__(name,desc) #calls init of item class
        self.damage = damage
        self.attackTypes = attackTypes
    
    def description(self):
        return "%s, it does %i damage"%(super().description(),self.damage)

class Armor(Item):
    def __init__(self,name,desc,armor,slot):
        super().__init__(name,desc) #calls init of item class
        self.armor = armor
        self.slot = slot
    
    def description(self):
        return "%s, it blocks %i damage and you wear it on your %s"%(super().description(),self.armor,self.slot.lower())


class Enemy(object):
    def __init__(self,name,health,damage,armor,attackTypes):
        self.name = name
        self.health = health
        self.damage = damage
        self.armor = armor
        self.attackTypes = attackTypes
        
"""
variables
"""
plains = {"name":"plains","color":"green","icon":"-"}
mountain = {"name":"mountain","color":"grey","icon":"▲"}
desert = {"name":"desert","color":"yellow","icon":"⁕"}
forest = {"name":"forest","color":"green","icon":"⇑"}
ocean = {"name":"ocean","color":"blue","icon":"≈"}

biomes = [plains,mountain,desert,forest,ocean]

iconSize = 20
gameMap = []
mapSize = 50

loadGame = False

player = {"color":"white",
          "icon":"X",
          "posX":mapSize/2,
          "posY":mapSize/2,
          "health":20,
          "damage":10,
          "armor":5,
          "inventory":[Weapon("Sword","A stabby metal object",10,["Slash","Stab"]),
                       Armor("Chestplate","A large hunk of metal",27,"Body")]}

currentEnemy = Enemy("name",10,5,10,["attack1","attack2"])

"""
functions
"""


def saveMap():
    file = open("map.txt","wb")
    pickle.dump(gameMap, file)
    file.close()
    
def saveStats():
    file = open("player.txt","wb")
    pickle.dump(player,file)
    file.close()    

def generateMap():
    for y in range(mapSize):
        gameMap.append([])
        for x in range(mapSize):
            gameMap[y].append(random.choice(biomes))
    saveMap()

def load():
    global gameMap
    global player
    try:
        file = open("map.txt","rb")
        gameMap = pickle.load(file)
        file.close()
    except FileNotFoundError:
        generateMap()
    
    try:
        file = open("player.txt","rb")
        player = pickle.load(file)
        file.close()
    except FileNotFoundError:
        player = {"color":"white",
                  "icon":"X",
                  "posX":1,
                  "posY":1,
                  "inventory":[]}

def updateMap():
    app.clearCanvas("map")
    a = 0
    for y in gameMap:
        a+=1
        b=0   
        for x in y:
            b+=1
            name = str(a)+" "+str(b)
                   
            map.create_rectangle(b*iconSize, a*iconSize, b*iconSize+iconSize, a*iconSize+iconSize,fill=x["color"])
            map.create_text((b*iconSize)+(iconSize/2), (a*iconSize)+(iconSize/2),text = x["icon"])
    
    map.create_rectangle(player["posX"]*iconSize, player["posY"]*iconSize, player["posX"]*iconSize+iconSize, player["posY"]*iconSize+iconSize,fill=player["color"],tags="player") 
    map.create_text((player["posX"]*iconSize)+(iconSize/2), (player["posY"]*iconSize)+(iconSize/2),text = player["icon"],tags="player")                
    map.xview_moveto((player["posX"]-5)/(mapSize+2))
    map.yview_moveto((player["posY"]-5)/(mapSize+2))    

def onMove():
    map.xview_moveto((player["posX"]-5)/(mapSize+2))
    map.yview_moveto((player["posY"]-5)/(mapSize+2))
    
    fight()#testing    

def keys(key):
    currentTab = app.getTabbedFrameSelectedTab("main")
    
    if(currentTab == "map"):
        playerObj = map.find_withtag("player")
        if(key == "<Left>"):
            if(player["posX"] != 1):
                player["posX"] -= 1
                for p in playerObj:
                    map.move(p,-iconSize,0) #thing, x, y
                onMove()
        elif(key == "<Right>"):
            if(player["posX"] != mapSize):
                player["posX"] += 1
                for p in playerObj:
                    map.move(p,iconSize,0)
                onMove()
        elif(key == "<Up>"):
            if(player["posY"] != 1):
                player["posY"] -= 1  
                for p in playerObj:
                    map.move(p,0,-iconSize)
                onMove()
        elif(key == "<Down>"):
            if(player["posY"] != mapSize):
                player["posY"] += 1
                for p in playerObj:
                    map.move(p,0,iconSize)
                onMove()
        
        
    elif(currentTab == "combat"):
        global currentEnemy
        
        print("Player")
        print("health:%i,damage:%i,armor:%i"%(player["health"],player["damage"],player["armor"]))        
        
        print("Enemy")
        print("name:%s,health:%i,damage:%i,armor:%i"%(currentEnemy.name,currentEnemy.health,currentEnemy.damage,currentEnemy.armor))
        
        if(key == "<a>"):
            print("attack")
            currentEnemy.health -= (player["damage"] - currentEnemy.armor)
        elif(key == "<b>"):
            print("block")
            player["health"] -= (currentEnemy.damage - player["armor"])
        
        if(player["health"] <= 0):
            endCombat("enemy")
        elif(key == "<r>"): #elif so you can't run if you're dead
            print("run")
            endCombat()
        elif(currentEnemy.health <= 0):
            endCombat("player")
    saveStats()

def updateInventory():
    if(app.getTabbedFrameSelectedTab("main") != "inventory"):
        return
    app.openTab("main","inventory")
    app.emptyCurrentContainer()
    for i in player["inventory"]:
        app.addLabel(i.name,i.name)
        app.setLabelTooltip(i.name, i.description())

def fight():
    global currentEnemy
    currentEnemy = Enemy("name",10,10,2,["attack1","attack2"])
    
    app.setTabbedFrameSelectedTab("main","combat",False)
    
    app.setTabbedFrameDisabledTab("main","map", True)
    app.setTabbedFrameDisabledTab("main","inventory", True)
    app.setTabbedFrameDisabledTab("main","combat", False)  
    
def endCombat(winner="none"):
    app.setTabbedFrameSelectedTab("main","map",False)
    
    app.setTabbedFrameDisabledTab("main","map", False)
    app.setTabbedFrameDisabledTab("main","inventory", False)    
    app.setTabbedFrameDisabledTab("main","combat", True)  
    if(winner == "enemy"):
        print("you died")
    elif(winner == "player"):
        print("you win")
        player["damage"] += 1
    elif(winner == "none"):
        print("you're a coward")
"""
setup and start gui
"""

app = gui("Waste Adventure")
app.setSticky("NEWS")
app.setStretch("both")

app.addLabel("title", "Waste Adventure")

app.startTabbedFrame("main")
app.setTabbedFrameTabExpand("main", expand=True)
app.setTabbedFrameChangeCommand("main", updateInventory)
app.startTab("map")
map = app.addCanvas("map")
map.config(scrollregion=(0,0,(mapSize+2)*iconSize,(mapSize+2)*iconSize),height=(iconSize*11)+1) #x1, y1, x2, y2, height
app.stopTab()

app.startTab("inventory")
app.addLabel("inv","inventory")
app.stopTab()

app.startTab("combat")
app.addLabel("fight","combat")
app.stopTab()
app.stopTabbedFrame()

if(loadGame):
    load()
else:
    generateMap()
updateMap()

app.bindKeys(["<Left>","<Right>","<Up>","<Down>","<a>","<b>","<r>"], keys)
app.go()