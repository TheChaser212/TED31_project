#-*- coding: utf-8 -*-
from appJar import gui #gui module
import random #random stuff
import pickle #saving module

"""
Define classes
"""
class Item: #class for items the player can collect
    def __init__(self,name,desc):
        self.name = name
        self.desc = desc
        
    def description(self): #return description of item
        return self.desc
        
class Weapon(Item): #subclass of item
    def __init__(self,name,desc,damage,attackTypes):
        super().__init__(name,desc) #calls init of item class
        self.damage = damage
        self.attackTypes = attackTypes
        self.slot = "weapon" #all weapons are equipped in weapon slot (by default)
    
    def description(self): #return description of weapon
        return "%s, it does %i damage and you use it as a weapon"%(super().description(),self.damage) #Item() description + extra info

class Armor(Item): #subclass of item
    def __init__(self,name,desc,armor,slot):
        super().__init__(name,desc) #calls init of item class
        self.armor = armor
        self.slot = slot
    
    def description(self): #return description of armor
        return "%s, it blocks %i damage and you wear it on your %s"%(super().description(),self.armor,self.slot.lower()) #Item() description + extra info

class Mob: #class that encompasses all characters
    def __init__(self,name,health,damage,armor,attackTypes):
        self.name = name
        self.health = health
        self.maxHealth = health
        self.damage = damage
        self.armor = armor
        self.attackTypes = attackTypes
    
    def attackDesc(self,other,damage): #description of combat between two mobs
        return "%s %s at %s, doing %i damage"%(self.name,random.choice(self.attackTypes),other.name,damage) # thing attacks at other, doing num damage

class Player(Mob): #subclass of Mob
    def __init__(self,name,health,damage,armor,attackTypes,posX,posY,inventory):
        super().__init__(name,health,damage,armor,attackTypes)
        self.posX = posX
        self.posY = posY
        self.icon = "X" #default icon
        self.color = "white" #default color
        self.inventory = inventory
        self.equipped = {"weapon":None,"head":None,"body":None,"legs":None} #nothing equipped by default
        
    def updateStats(self): #set stats to match equipment
        self.damage = 0
        self.armor = 0
        for item in self.equipped:
            try: #make sure it actually has a damage
                self.damage += self.equipped[item].damage
            except:
                pass
            
            try: #make sure it actually has armor
                self.armor += self.equipped[item].armor
            except:
                pass
    
    def equip(self,item): #equip an item
        try: #in case players try to equip items that can't be equipped
            self.equipped[item.slot] = item
            output("Equipped %s"%item.name.lower())
            self.updateStats()
        except: 
            output("You can't equip that!")
        updateInventory()
            
    def unEquip(self,slot): #unequip an item
        item = self.equipped[slot]
        if(self.equipped[slot] != None): #can't unequip nothing
            output("Unequipped %s"%item.name.lower()) #give player feedback
            self.equipped[slot] = None
            self.updateStats()
            updateInventory()
        
class Biome: #class for biomes
    def __init__(self,name,color,icon,enemies,cleanBiome=None):
        self.name = name
        self.color = color
        self.icon = icon
        self.enemies = enemies
        self.cleanBiome = cleanBiome
    
    def clean(self):
        if(self.cleanBiome != None):
            gameMap[player.posY][player.posX] = self.cleanBiome
            updateTile(player.posX,player.posY)

class Recipe: #class for recipes
    def __init__(self,required,crafted):
        self.required = required #list of items needed
        self.crafted = crafted #what is made
        
    def craft(self):
        for requirement in self.required:
            if(not (player.inventory.count(requirement) >= 1)): #if not at least one of the required item (may cause issues if a recipe needs multiple of the same item)
                #print("failed to craft "+self.crafted.name)
                output("You don't have a %s!"%requirement.name.lower())
                return #can't craft something if you don't have the requirements
        
        for requirement in self.required:
            player.inventory.remove(requirement) #remove each required item
        
        output("Crafted a "+self.crafted.name.lower())
        player.inventory.append(self.crafted) #add the item
    
    def description(self):
        desc = "To craft the %s you need: "%self.crafted.name.lower()
        for requirement in self.required:
            desc += "\n%s"%requirement.name.lower()
        return desc
"""
functions
"""
def output(text): #set output label text to something
    app.setLabel("output",text)

def loot():
    item = random.choice(items)
    output("You pick up a "+item.name)
    player.inventory.append(item)

"""
saving/loading functions
"""
def saveMap(): #save map
    file = open("map.txt","wb")
    pickle.dump(gameMap, file)
    file.close()
    
def saveStats(): #save player stats
    file = open("player.txt","wb")
    pickle.dump(player,file)
    file.close()    

def saveAll(): #save everything
    output("Game saved")
    saveMap()
    saveStats()
    
def load(): #load player stats and map
    global gameMap, player
    try: #don't open files that don't exist
        file = open("map.txt","rb")
        gameMap = pickle.load(file)
        file.close()
    except FileNotFoundError: #create a map if no file found (file will be created when it's saved)
        generateMap()
    
    try: #don't open files that don't exist
        file = open("player.txt","rb")
        player = pickle.load(file)
        file.close()
    except FileNotFoundError: #create player with default stats if no file found (file will be created when it's saved)
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
    updateMap() #update map at end because player pos might have changed


"""
map functions
"""
def generateMap(): #create new map
    for y in range(mapSize):
        gameMap.append([])
        for x in range(mapSize):
            gameMap[y].append(random.choice(biomes)) #add a random biome for each tile
    updateMap()
    saveMap() #save the map once it's generated

def updateMap(): #clear all the tiles on the map and readd them
    app.clearCanvas("map")
    a = 0
    for y in gameMap:
        b=0   
        for x in y:
            name = str(b)+" "+str(a) # "x y" so we can change the tiles later
                   
            map.create_rectangle(b*iconSize, a*iconSize, b*iconSize+iconSize, a*iconSize+iconSize, fill=x.color, width=0, tags=[name]) #x1, y1, x2, y2, color
            map.create_text((b*iconSize)+(iconSize/2), (a*iconSize)+(iconSize/2), text = x.icon, tags=[name])
            b+=1
        a+=1
    
    #create and move to player tile
    map.create_rectangle(player.posX*iconSize, player.posY*iconSize, player.posX*iconSize+iconSize-1, player.posY*iconSize+iconSize-1,fill=player.color,tags="player") 
    map.create_text((player.posX*iconSize)+(iconSize/2), (player.posY*iconSize)+(iconSize/2),text = player.icon,tags="player")                
    map.xview_moveto((player.posX-5)/(mapSize+2)) #show player position + 5 tiles to the left
    map.yview_moveto((player.posY-5)/(mapSize+2)) #show player position + 5 tiles up  

def updateTile(x,y):
    biome = gameMap[y][x]
    name = str(x)+" "+str(y)
    for t in map.find_withtag(name):
        if(map.type(t) == "rectangle"):
            map.itemconfig(t,fill=biome.color)
        elif(map.type(t) == "text"):
            map.itemconfig(t,text=biome.icon)

"""
input related functions
"""
def onMove(): #things to do when the player moves
    #move map to where player is
    map.xview_moveto((player.posX-5)/(mapSize+2))
    map.yview_moveto((player.posY-5)/(mapSize+2))
    
    event = random.randint(1,4)
    if(event == 1): #1 in 4 chance of starting combat
        startCombat()   
    elif(event == 2):
        loot()
    else:#2 in 4 chance of no event
        pass
    gameMap[player.posY][player.posX].clean() #'clean' the biome once you've done something

def keys(key): #what to do whenever a key is pressed
    currentTab = app.getTabbedFrameSelectedTab("main") #find the current tab
    
    if(key == "c"):
        recipes[0].craft()
    
    if(currentTab == "map"): #movement on map
        playerObj = map.find_withtag("player") #get all canvas objects with 'player' tag
        if(key == "Left"):
            if(player.posX != 0): #prevent going off the map
                player.posX -= 1
                for p in playerObj:
                    map.move(p,-iconSize,0) #move object x, y
                onMove()
        elif(key == "Right"):
            if(player.posX != mapSize-1): #prevent going off the map
                player.posX += 1
                for p in playerObj:
                    map.move(p,iconSize,0)
                onMove()
        elif(key == "Up"):
            if(player.posY != 0): #prevent going off the map
                player.posY -= 1  
                for p in playerObj:
                    map.move(p,0,-iconSize)
                onMove()
        elif(key == "Down"):
            if(player.posY != mapSize-1): #prevent going off the map
                player.posY += 1
                for p in playerObj:
                    map.move(p,0,iconSize)
                onMove()
        
        
    elif(currentTab == "combat"): #only work on combat tab
        if(key in ["a","b","r"]):#only get attacked when using keys related to combat   
            global currentEnemy
            enemyAttacks = (random.random() > 0.5) #50% chance enemy attacks
            if(key == "a"):
                damage = max(player.damage - currentEnemy.armor,1) #prevent negative damage
                currentEnemy.health -= damage
                
                if(enemyAttacks):
                    damage = max(currentEnemy.damage - player.armor,1) #prevent negative damage
                    player.health -= damage
                    output(player.attackDesc(currentEnemy,damage)+"\n"+currentEnemy.attackDesc(player,damage))
                else:
                    output(player.attackDesc(currentEnemy,damage))
            elif(key == "b"):
                output("You block the %s's attack!"%currentEnemy.name)
            elif(key == "r"):
                if(enemyAttacks):
                    damage = max(currentEnemy.damage - player.armor,1) #prevent negative damage
                    player.health -= damage
                    output(currentEnemy.attackDesc(player,damage))  
                else:
                    endCombat() #end combat with no winner
            
            
            updateCombat() #update labels to show info
            
            if(player.health <= 0):
                endCombat("enemy")
            elif(currentEnemy.health <= 0):
                endCombat("player")        
    #saveStats()


"""
inventory functions
"""
def updateInventory(): #add labels for all the items in the player's inventory and what they have equipped
    if(app.getTabbedFrameSelectedTab("main") != "inventory"): #dont bother updating inventory labels if not on the tab
        return
    app.openFrame("items")
    app.emptyCurrentContainer()
    for i in player.inventory:
        try: #in case there are multiple of the same item
            app.addLabel(i,i.name)
            app.setLabelTooltip(i, i.description())
            app.setLabelRelief(i,"raised")
            app.setLabelDragFunction(i, [itemDrag, itemDrop])
        except: #if multiple of the same item set the label to show the amount
            app.setLabel(i,"%s x%i"%(i.name,player.inventory.count(i))) #Thing xNum
    app.stopFrame()
    
    
    for slot in player.equipped:
        item = player.equipped[slot]
        try: #make sure it's an actual equipment
            app.setLabel(slot,item.name)
            app.setLabelTooltip(slot, item.description())
        except:#if no item equipped in slot
            app.setLabel(slot,"Nothing")
            app.setLabelTooltip(slot, "")

def itemDrag(widget): #find the item that's being dragged by mouse
    global draggedItem
    draggedItem = widget
    app.raiseFrame("equipped")

def itemDrop(widget): #equip item that is dropped by mouse
    player.equip(draggedItem)


def showRecipe(widget):
    app.openFrame("craftInfo")
    app.emptyCurrentContainer()
    app.addLabel("craftDesc",widget.description())
    app.addButton("craft",widget.craft)
    app.stopFrame()

"""
combat functions
"""
def updateCombat(): #set labels/meters to match new stats
    app.setMeter("playerHealth",100*player.health/player.maxHealth,text=player.health)
    app.setLabel("playerDamage","Damage: %i"%player.damage)
    app.setLabel("playerArmor","Armor: %i"%player.armor)
    
    app.setLabel("enemyName","%s"%currentEnemy.name)
    app.setMeter("enemyHealth",100*currentEnemy.health/currentEnemy.maxHealth,text=currentEnemy.health)
    app.setLabel("enemyDamage","Damage: %i"%currentEnemy.damage)
    app.setLabel("enemyArmor","Armor: %i"%currentEnemy.armor)

def startCombat(): #start combat by generating an enemy and disabling unrelated tabs
    global currentEnemy
    if not (gameMap[player.posY][player.posX].enemies):
        print("no enemies in this biome")
        return
    currentEnemy = random.choice(gameMap[player.posY][player.posX].enemies) #choose an enemy from the biome the player is in
    currentEnemy.maxHealth += round(random.uniform(-currentEnemy.maxHealth/2,currentEnemy.maxHealth/2)) #add some variation on their health
    currentEnemy.health = currentEnemy.maxHealth  
    
    player.health = player.maxHealth #reset player health
    
    app.setTabbedFrameDisabledTab("main","map", True) #disable all other tabs
    app.setTabbedFrameDisabledTab("main","inventory", True)
    app.setTabbedFrameDisabledTab("main","combat", False)    

    app.setTabbedFrameSelectedTab("main","combat",False) #go to combat tab
    
    
    
    updateCombat()
    
def endCombat(winner="none"):#end the combat with default value of no winner
    
    app.setTabbedFrameDisabledTab("main","map", False) #go back to normal tabs
    app.setTabbedFrameDisabledTab("main","inventory", False)    
    app.setTabbedFrameDisabledTab("main","combat", True)      

    app.setTabbedFrameSelectedTab("main","map",False) 
    
    #stuff do based on who won
    if(winner == "enemy"):
        output("You died")
    elif(winner == "player"):
        output("You win")
        player.maxHealth += 1
        loot()
    elif(winner == "none"): #player ran away
        output("You managed to ran away")
    else: #shouldn't ever happen
        output("Something went wrong")


"""
variables
"""
#biome info
biomes = [
    Biome("toxic dump","gold","-",[Mob("Slime",5,5,0,["glomps","slops"])],Biome("plains","limegreen","-",None)),
    Biome("wasteland","coral","⁕",[Mob("Radscorpion",25,15,5,["stings","claws"])],Biome("desert","palegoldenrod","⁕",None)),
    Biome("burnt forest","sienna","⇑",[Mob("Burning Gorilla",5,25,9,["burns","clubs"])],Biome("forest","seagreen","⇑",None)),
    Biome("polluted ocean","darkorchid","≈",[Mob("Plastic Kraken",50,50,10,["stings","claws"])],Biome("ocean","dodgerblue","≈",None))
    ]

#list of every item
items = [Weapon("Sword","A stabby metal object",11,["Slash","Stab"]),
        Armor("Chestplate","A large hunk of metal",27,"body"),
        Weapon("Big Sword","A big stabby metal object",1000,["Smash","Slam"])]

#list of every recipe
#need to use index of the item in the items list so that the Item object is correct
recipes = [Recipe([items[0],items[1]],items[2]),
           Recipe([items[2],items[1]],items[0])] 

iconSize = 20 #size of each tile on the map in pixels
gameMap = []
mapSize = 4 #size of the map

loadGame = False #load game or not

#player stats
player = Player("player",#name
                10,#health
                11,#damage
                10,#armor
                ["slashes","stabs"],#attack types
                round(mapSize/2),#x position
                round(mapSize/2),#y position
                []#inventory
                )
                

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


app.setSticky("nesw")
app.setStretch("both")

app.startTabbedFrame("main")#tabs in the gui
app.setTabbedFrameTabExpand("main", expand=True) #expand to fit whole gui
app.setTabbedFrameChangeCommand("main", updateInventory) #when changing tab call updateInventory(), a return in that function prevents it from happening on wrong tab


#map tab
app.startTab("map")
map = app.addCanvas("map")
map.config(scrollregion=(0,0,(mapSize+2)*iconSize,(mapSize+2)*iconSize)) #x1, y1, x2, y2, height,height=(iconSize*11)+1
app.stopTab()


#inventory tab
app.startTab("inventory") #items in inventory
app.startFrame("items",row=0,column=0)
app.stopFrame()

app.addVerticalSeparator(row=0,column=1)

app.startFrame("equipped",row=0,column=2) #equipped items
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



#crafting tab
app.startTab("crafting")
app.startFrame("recipes",row=0,column=0)
for recipe in recipes:
    app.setSticky("ew")  
    app.addLabel(recipe,recipe.crafted.name)
    app.setLabelTooltip(recipe, recipe.description())
    app.setLabelRelief(recipe,"raised")
    app.setLabelSubmitFunction(recipe, showRecipe)
app.stopFrame()

app.addVerticalSeparator(row=0,column=1)

app.startFrame("craftInfo",row=0,column=3)#place where crafting description and button go
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


app.startTab("help")
app.addLabel("helpLabel","""Use the arrow keys to move around the map.
Click or drag items you want to equip.
When in combat use A to attack, B to block and R to run.""")
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

app.bindKeys(["Left","Right","Up","Down","a","b","r","c"], keys)
app.go()