#-*- coding: utf-8 -*-
from appJar import gui
import random
import pickle

"""
Define classes
"""
class Item:
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
        self.slot = "weapon"
    
    def description(self):
        return "%s, it does %i damage and you use it as a weapon"%(super().description(),self.damage)

class Armor(Item):
    def __init__(self,name,desc,armor,slot):
        super().__init__(name,desc) #calls init of item class
        self.armor = armor
        self.slot = slot
    
    def description(self):
        return "%s, it blocks %i damage and you wear it on your %s"%(super().description(),self.armor,self.slot.lower())

class Mob:
    def __init__(self,name,health,damage,armor,attackTypes):
        self.name = name
        self.health = health
        self.maxHealth = health
        self.damage = damage
        self.armor = armor
        self.attackTypes = attackTypes
    
    def attackDesc(self,other,damage):
        return "%s %s at %s, doing %i damage"%(self.name,random.choice(self.attackTypes),other.name,damage)

class Player(Mob): #subclass of Mob
    def __init__(self,name,health,damage,armor,attackTypes,posX,posY,inventory):
        super().__init__(name,health,damage,armor,attackTypes)
        self.posX = posX
        self.posY = posY
        self.icon = "X"
        self.color = "white"
        self.inventory = inventory
        self.equipped = {"weapon":None,"head":None,"body":None,"legs":None}
        
    def updateStats(self):
        self.damage = 0
        self.armor = 0
        for item in self.equipped:
            try:
                self.damage += self.equipped[item].damage
            except:
                pass
            try:
                self.armor += self.equipped[item].armor
            except:
                pass
    
    def equip(self,item):
        try:
            self.equipped[item.slot] = item
            output("Equipped %s"%item.name.lower())
            self.updateStats()
        except:
            output("You can't equip that!")
        updateInventory()
            
    def unEquip(self,slot):
        item = self.equipped[slot]
        if(self.equipped[slot] != None):
            output("Unequipped %s"%item.name.lower())
            self.equipped[slot] = None
            self.updateStats()
        updateInventory()
        
class Biome:
    def __init__(self,name,color,icon):
        self.name = name
        self.color = color
        self.icon = icon


"""
functions
"""
def output(text):
    app.setLabel("output",text)

def saveMap(): #save map
    file = open("map.txt","wb")
    pickle.dump(gameMap, file)
    file.close()
    
def saveStats(): #save player stats
    file = open("player.txt","wb")
    pickle.dump(player,file)
    file.close()    

def saveAll():
    output("Game saved")
    saveMap()
    saveStats()

def generateMap(): #create new map
    for y in range(mapSize):
        gameMap.append([])
        for x in range(mapSize):
            gameMap[y].append(random.choice(biomes))
    saveMap()

def load(): #load player stats and map
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
        player = Player("player",#name
                10,#health
                5,#damage
                10,#armor
                ["Slash","Stab"],#attack types
                mapSize/2,#x position
                mapSize/2,#y position
                [Weapon("Sword","A stabby metal object",10,["Slash","Stab"]),
                Armor("Chestplate","A large hunk of metal",27,"Body")])
    
    output("Game loaded")
    updateMap() #do it at end because player pos might be different

def updateMap(): #reload map
    app.clearCanvas("map")
    a = 0
    for y in gameMap:
        a+=1
        b=0   
        for x in y:
            b+=1
            name = str(a)+" "+str(b)
                   
            map.create_rectangle(b*iconSize, a*iconSize, b*iconSize+iconSize, a*iconSize+iconSize, fill=x.color) #x1, y1, x2, y2, color
            map.create_text((b*iconSize)+(iconSize/2), (a*iconSize)+(iconSize/2), text = x.icon)
    
    map.create_rectangle(player.posX*iconSize, player.posY*iconSize, player.posX*iconSize+iconSize, player.posY*iconSize+iconSize,fill=player.color,tags="player") 
    map.create_text((player.posX*iconSize)+(iconSize/2), (player.posY*iconSize)+(iconSize/2),text = player.icon,tags="player")                
    map.xview_moveto((player.posX-5)/(mapSize+2)) #show player position + 5 tiles to the left
    map.yview_moveto((player.posY-5)/(mapSize+2))  #show player position + 5 tiles up  

def onMove():
    map.xview_moveto((player.posX-5)/(mapSize+2))
    map.yview_moveto((player.posY-5)/(mapSize+2))
    
    if(random.randint(1,4)==1):
        startCombat()#testing    

def keys(key):
    currentTab = app.getTabbedFrameSelectedTab("main")
    
    if(currentTab == "map"):
        playerObj = map.find_withtag("player")
        if(key == "Left"):
            if(player.posX != 1):
                player.posX -= 1
                for p in playerObj:
                    map.move(p,-iconSize,0) #move object x, y
                onMove()
        elif(key == "Right"):
            if(player.posX != mapSize):
                player.posX += 1
                for p in playerObj:
                    map.move(p,iconSize,0)
                onMove()
        elif(key == "Up"):
            if(player.posY != 1):
                player.posY -= 1  
                for p in playerObj:
                    map.move(p,0,-iconSize)
                onMove()
        elif(key == "Down"):
            if(player.posY != mapSize):
                player.posY += 1
                for p in playerObj:
                    map.move(p,0,iconSize)
                onMove()
        
        
    elif(currentTab == "combat"):
        global currentEnemy
        if(key == "a"):
            damage = max(player.damage - currentEnemy.armor,0)
            currentEnemy.health -= damage
            output(player.attackDesc(currentEnemy,damage))
        elif(key == "b"):
            damage = max(currentEnemy.damage - player.armor,0)
            player.health -= damage
            output(currentEnemy.attackDesc(player,damage))
        
        updateCombat() #update labels to show info
        
        if(player.health <= 0):
            endCombat("enemy")
        elif(currentEnemy.health <= 0):
            endCombat("player")        
        elif(key == "r"): #elif so you can't run if you're dead
            endCombat()
    saveStats()

def updateInventory():
    if(app.getTabbedFrameSelectedTab("main") != "inventory"):
        return
    app.openFrame("items")
    app.emptyCurrentContainer()
    for i in player.inventory:
        app.addLabel(i,i.name)
        app.setLabelTooltip(i, i.description())
        app.setLabelRelief(i,"raised")
        app.setLabelDragFunction(i, [itemDrag, itemDrop])
    
    for slot in player.equipped:
        item = player.equipped[slot]
        try:
            app.setLabel(slot,item.name)
            app.setLabelTooltip(slot, item.description())
            
        except:#if no item equipped in slot
            app.setLabel(slot,"Nothing")
            app.setLabelTooltip(slot, "")

def itemDrag(widget):
    global draggedItem
    draggedItem = widget
    #print("Dragged from:", widget)
    app.raiseFrame("equipped")

def itemDrop(widget):
    #print("Dropped on:", widget)
    #print(draggedItem.slot)
    #if(widget == draggedItem.slot):
    player.equip(draggedItem)

#combat functions
def updateCombat():
    app.setMeter("playerHealth",100*player.health/player.maxHealth,text=player.health)
    app.setLabel("playerDamage","Damage: %i"%player.damage)
    app.setLabel("playerArmor","Armor: %i"%player.armor)
    
    app.setLabel("enemyName","%s"%currentEnemy.name)
    app.setMeter("enemyHealth",100*currentEnemy.health/currentEnemy.maxHealth,text=currentEnemy.health)
    app.setLabel("enemyDamage","Damage: %i"%currentEnemy.damage)
    app.setLabel("enemyArmor","Armor: %i"%currentEnemy.armor)

def startCombat():
    global currentEnemy
    currentEnemy = Mob("enemy",10,13,10,["jabs","claws"])
    player.health = player.maxHealth #change at some point
    
    app.setTabbedFrameSelectedTab("main","combat",False) #go to combat tab
    
    app.setTabbedFrameDisabledTab("main","map", True) #disable all other tabs
    app.setTabbedFrameDisabledTab("main","inventory", True)
    app.setTabbedFrameDisabledTab("main","combat", False)
    
    updateCombat()
    
def endCombat(winner="none"):#default value of no winner
    app.setTabbedFrameSelectedTab("main","map",False) #go back to normal tabs
    
    app.setTabbedFrameDisabledTab("main","map", False)
    app.setTabbedFrameDisabledTab("main","inventory", False)    
    app.setTabbedFrameDisabledTab("main","combat", True)  
    if(winner == "enemy"):
        output("You died")
    elif(winner == "player"):
        output("You win")
        player.maxHealth += 1
    elif(winner == "none"):
        output("You're a no namer dog")


"""
variables
"""
#biome info
plains = Biome("plains","green","-")
mountain = Biome("mountain","grey","▲")
desert = Biome("desert","yellow","⁕")
forest = Biome("forest","green","⇑")
ocean = Biome("ocean","blue","≈")

biomes = [plains,mountain,desert,forest,ocean]

iconSize = 20 #size of each tile on the map in pixels
gameMap = []
mapSize = 50 #size of the map

loadGame = False #load game or not

#player stats
player = Player("player",#name
                10,#health
                11,#damage
                10,#armor
                ["slashes","stabs"],#attack types
                mapSize/2,#x position
                mapSize/2,#y position
                [Weapon("Sword","A stabby metal object",11,["Slash","Stab"]),#inventory
                Armor("Chestplate","A large hunk of metal",27,"body"),
                Weapon("Big Sword","A big stabby metal object",1000,["Smash","Slam"])])
                

#enemy that's being fought
currentEnemy = Mob("enemy",#name
                   10,#health
                   13,#damage
                   10,#armor
                   ["jabs","claws"]#attack types
                   )
draggedItem = 0 #currently dragged widget


"""
setup and start gui
"""
app = gui("Waste Adventure")

app.createMenu("File")
app.addMenuItem("File", "Save", func=saveAll)
app.addMenuItem("File", "Load", func=load)


app.setStretch('column')
app.setSticky('esw')
app.addLabel("title", "Waste Adventure")


app.setSticky("NEWS")
app.setStretch("both")
app.startTabbedFrame("main")
app.setTabbedFrameTabExpand("main", expand=True)
app.setTabbedFrameChangeCommand("main", updateInventory)

#map tab
app.startTab("map")
map = app.addCanvas("map")
map.config(scrollregion=(0,0,(mapSize+2)*iconSize,(mapSize+2)*iconSize)) #x1, y1, x2, y2, height,height=(iconSize*11)+1
app.stopTab()

#inventory tab
app.startTab("inventory")
app.startFrame("items",row=0,column=0)
app.addEmptyLabel("empty")
app.stopFrame()

app.addVerticalSeparator(row=0,column=1)

app.startFrame("equipped",row=0,column=2)
itemRow = 0
for slot in player.equipped:
    app.addLabel("%s title"%slot,slot.capitalize(),row=itemRow,column=2)
    app.addLabel(slot,player.equipped[slot],row=itemRow,column=3)
    app.setLabelRelief(slot,"ridge")
    app.setLabelTooltip(slot, player.equipped[slot])
    app.setLabelSubmitFunction(slot, player.unEquip)
    
    itemRow += 1
app.stopFrame()
app.stopTab()

#combat tab
app.startTab("combat")
app.addLabel("fight","combat")

#player
app.startFrame("player",row=0,column=0)
app.addLabel("playerName","Player")

app.addMeter("playerHealth",100)
app.setMeterFill("playerHealth","Green")
app.setMeterBg("playerHealth","Red")

app.addLabel("playerDamage","Damage")
app.addLabel("playerArmor","Armor")
app.stopFrame()

app.addVerticalSeparator(row=0,column=1)

#enemy
app.startFrame("enemy",row=0,column=2)
app.addLabel("enemyName","Name")
app.addMeter("enemyHealth",100)
app.setMeterFill("enemyHealth","Green")
app.setMeterBg("enemyHealth","Red")

app.addLabel("enemyDamage","Damage")
app.addLabel("enemyArmor","Armor")
app.stopFrame()

app.stopTab()
app.stopTabbedFrame()


app.setTabbedFrameDisabledTab("main","combat", True) #disable combat tab while not in combat


#output
app.setStretch('column')
app.setSticky('ew')
app.addLabel("output","did something",colspan=3)

if(loadGame):#load by default or not
    load()
else:
    generateMap()
updateMap()

app.bindKeys(["Left","Right","Up","Down","a","b","r"], keys)
app.go()