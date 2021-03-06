#-*- coding: utf-8 -*-
from appJar import gui #gui module
import random #random numbers
import pickle #saving module
import os #checking file exists

"""
Define classes
"""
class Item: #class for items the player can collect
    def __init__(self,name,desc):
        self.name = name
        self.desc = desc
        
    def description(self): #return description of item
        return self.desc
        
class Weapon(Item): #subclass of item for weapons used by the player
    def __init__(self,name,desc,damage,attackTypes):
        super().__init__(name,desc) #calls init of item class
        self.damage = damage #integer value for damage
        self.attackTypes = attackTypes #list of verbs used when attacking
        self.slot = "weapon" #all weapons are equipped in weapon slot (by default)
    
    def description(self): #return description of weapon
        return "%s, it does %i damage and you use it as a weapon"%(super().description(),self.damage) #Item() description + extra info

class Armor(Item): #subclass of item for armor
    def __init__(self,name,desc,armor,slot):
        super().__init__(name,desc) #calls init of item class
        self.armor = armor #armor value
        self.slot = slot #slot it's equipped in
    
    def description(self): #return description of armor
        return "%s, it blocks %i damage and you wear it on your %s"%(super().description(),self.armor,self.slot.lower()) #Item() description + extra info

class Mob: #class that encompasses all characters
    def __init__(self,name,health,damage,armor,attackTypes):
        self.name = name #name of mob
        self.health = health #current health of mob
        self.maxHealth = health #max health of mob (equal to current at beginning)
        self.damage = damage #damage mob does
        self.armor = armor #amount of armor mob has
        self.attackTypes = attackTypes #list of verbs used when attacking
    
    def attackDesc(self,other,damage): #description of combat between two mobs
        return "%s %s at %s, doing %i damage"%(self.name,random.choice(self.attackTypes),other.name,damage) # thing attackTypes at other, doing num damage

class Player(Mob): #subclass of Mob
    def __init__(self,name,health,damage,armor,attackTypes,posX,posY,inventory):
        super().__init__(name,health,damage,armor,attackTypes)
        self.posX = posX #X position on map
        self.posY = posY #Y position on map
        self.icon = "X" #default icon
        self.color = "white" #default color
        self.inventory = inventory #list of items player has
        self.equipped = {"weapon":None,"head":None,"body":None,"legs":None} #slots for equipment which are empty by default
        self.amountCleaned = 0 #amount of tiles cleaned
        
    def updateStats(self): #set stats to match equipment
        self.damage = 0
        self.armor = 0
        for item in self.equipped: #go through each equipped item and add their stats to the player
            if hasattr(self.equipped[item], "damage"): #make sure it actually has a damage
                self.damage += self.equipped[item].damage #for each equipped item that provides damage add it to player damage
            
            if hasattr(self.equipped[item], "armor"): #make sure it actually has armor
                self.armor += self.equipped[item].armor #for each equipped item that provides armor add it to player armor
    
    def equip(self,item): #equip an item
        if hasattr(item, "slot"): #in case players try to equip items that can't be equipped
            self.equipped[item.slot] = item
            output("Equipped %s"%item.name.lower())
            self.updateStats() #update stats when something is equipped
            updateInventory() #update labels to match what's now equipped
        else: 
            output("You can't equip that!")
            
    def unEquip(self,slot): #unequip an item
        if(self.equipped[slot] != None): #can't unequip nothing
            output("Unequipped %s"%self.equipped[slot].name.lower()) #give player feedback
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
            output("Cleaned the "+self.name)
            gameMap[player.posY][player.posX] = self.cleanBiome
            updateTile(player.posX,player.posY)
            player.amountCleaned += 1
            if player.amountCleaned >= mapSize**2: #if cleaned every tile (mapSize squared)
                endGame()

class Recipe: #class for recipes
    def __init__(self,required,crafted):
        self.required = required #list of items needed
        self.crafted = crafted #what is made
        
    def craft(self): #craft the recipe's item
        tempInv = player.inventory.copy()
        for requirement in self.required:
            try:
                tempInv.remove(requirement)
            except:
                output("You don't have a %s!"%requirement.name.lower())
                return #can't craft something if you don't have the requirements
        
        player.inventory = tempInv.copy()
        
        output("Crafted a "+self.crafted.name.lower())
        player.inventory.append(self.crafted) #add the item
    
    def description(self): #description of the recipe
        desc = "To craft the %s you need: "%self.crafted.name.lower()
        for requirement in self.required:
            if(self.required.count(requirement) == 1):
                desc += "\n%s"%requirement.name.lower()   
            else:
                desc += "\n%s x%i"%(requirement.name.lower(),self.required.count(requirement))
                break
        return desc
"""
functions
"""
def output(text): #set output label text to something
    app.setLabel("output","%s\n%s"%(app.getLabel("output"),text))

def loot(): #add a random item to the inventory
    item = random.choice(items)
    output("You pick up a "+item.name)
    player.inventory.append(item)

def endGame(): #what to do when game finishes
    app.removeAllWidgets()
    app.addLabel("endText","You've saved the planet!")

"""
saving/loading functions
"""
def saveMap(): #save map
    try:
        file = open("map.txt","wb")
        pickle.dump(gameMap, file)
        file.close()
    except:
        output("Unable to save map")
    
def saveStats(): #save player stats
    try:
        file = open("player.txt","wb")
        pickle.dump(player,file)
        file.close()    
    except:
        output("Unable to save player file")

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
    except: #create a map if no file found (file will be created when it's saved)
        generateMap()
    
    try: #don't open files that don't exist
        file = open("player.txt","rb")
        player = pickle.load(file)
        file.close()
    except: #create player with default stats if no file found (file will be created when it's saved)
        player = Player("Player",#name
                10,#health
                5,#damage
                0,#armor
                ["slashes","stabs"],#attack types
                round(mapSize/2),#x position
                round(mapSize/2),#y position
                []#inventory
                )
    
    output("Game loaded")
    updateMap() #update map at end because player pos might have changed

def startGame(widget): #do stuff based on button chosen
    if (widget == "Continue"):
        load()
        
    elif (widget == "New Game"):
        generateMap()
    
    #save/load menu, added after game is started so people don't save when nothing is made
    
    app.addMenuItem("File", "Save", func=saveAll)
    app.addMenuItem("File", "Load", func=load)    
    
    app.setTabbedFrameDisableAllTabs("main", disabled=False)
    app.setTabbedFrameDisabledTab("main", "combat", disabled=True)
    app.hideTabbedFrameTab("main","title")
    app.setTabbedFrameDisabledTab("main", "title", disabled=True)


"""
map functions
"""
def generateMap(): #create new map
    for y in range(mapSize):
        gameMap.append([])
        for x in range(mapSize):
            gameMap[y].append(random.choice(biomes)) #add a random biome for each tile
    gameMap[player.posY][player.posX].clean() #'clean' the starting biome
    updateMap()
    #saveMap() #save the map once it's generated

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

def rebind(): #rebinds the arrow keys because scrolling on the pane messes it up
    app.unbindKeys(["Left","Right","Up","Down"])
    app.bindKeys(["Left","Right","Up","Down"], keys)

def keys(key): #what to do whenever a key is pressed
    currentTab = app.getTabbedFrameSelectedTab("main") #find the current tab
    
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
                output(player.attackDesc(currentEnemy,damage))
                if(enemyAttacks):
                    damage = max(currentEnemy.damage - player.armor,1) #prevent negative damage
                    player.health -= damage
                    output(currentEnemy.attackDesc(player,damage))
                    
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
            app.setLabelSubmitFunction(i, itemSelect) #what to do when label is clicked
        except: #if multiple of the same item set the label to show the amount
            app.setLabel(i,"%s x%i"%(i.name,player.inventory.count(i))) #Thing xNum
    app.stopFrame()
    
    
    for slot in player.equipped:
        item = player.equipped[slot]
        if item != None: #make sure it's an actual equipment
            app.setLabel(slot,item.name)
            app.setLabelTooltip(slot, item.description())
        else:#if no item equipped in slot
            app.setLabel(slot,"Nothing")
            app.setLabelTooltip(slot, "")


def itemSelect(widget): #equip item that is clicked by mouse
    player.equip(widget)


def showRecipe(widget): #change the label to show information on recipe
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
        return
    currentEnemy = random.choice(gameMap[player.posY][player.posX].enemies) #choose an enemy from the biome the player is in
    currentEnemy.maxHealth += round(random.uniform(-currentEnemy.maxHealth/2,currentEnemy.maxHealth/2)) #add some variation on their health between 0.5 and 1.5 times 
    currentEnemy.health = currentEnemy.maxHealth  
    
    player.health = player.maxHealth #reset player health
    
    app.setTabbedFrameDisabledTab("main","map", True) #disable all other tabs
    app.setTabbedFrameDisabledTab("main","inventory", True)
    app.setTabbedFrameDisabledTab("main","crafting", True)
    app.setTabbedFrameDisabledTab("main","combat", False) #enable combat tab 

    app.setTabbedFrameSelectedTab("main","combat",False) #go to combat tab
    
    updateCombat()
    
def endCombat(winner="none"):#end the combat with default value of no winner
    
    app.setTabbedFrameDisabledTab("main","map", False) #go back to normal tabs
    app.setTabbedFrameDisabledTab("main","inventory", False)    
    app.setTabbedFrameDisabledTab("main","crafting", False)
    app.setTabbedFrameDisabledTab("main","combat", True)      

    app.setTabbedFrameSelectedTab("main","map",False) 
    
    #do stuff based on who won
    if(winner == "enemy"):
        output("You lost")
    elif(winner == "player"):
        output("You win")
        player.maxHealth += 1 #add one to player's health each time they win
        loot()
    elif(winner == "none"): #player ran away
        output("You managed to run away")
    else: #shouldn't ever happen but just in case
        output("Something went wrong")


"""
variables
"""
#biome list
biomes = [
    Biome("toxic dump","gold","-",[Mob("Toxic Sludge",5,5,0,["glomps","slops"])],Biome("plains","limegreen","-",None)), #toxic dump cleans to plains
    Biome("wasteland","coral","⁕",[Mob("Radscorpion",25,15,5,["stings","claws"])],Biome("desert","palegoldenrod","⁕",None)), #wasteland cleans to desert
    Biome("burnt forest","sienna","⇑",[Mob("Burning Gorilla",5,25,9,["burns","clubs"])],Biome("forest","seagreen","⇑",None)), #burnt forest cleans to forest
    Biome("polluted ocean","darkorchid","≈",[Mob("Plastic Kraken",50,50,10,["stings","claws"])],Biome("ocean","dodgerblue","≈",None)) #polluted ocean cleans to ocean
    ]

#list of every item
items = [
    Weapon("Sword","A stabby metal object",11,["Slash","Stab"]),
    Armor("Chestplate","A large hunk of metal",27,"body"),
    Weapon("Big Sword","A big stabby metal object",1000,["Smash","Slam"]),
    Item("Scrap Metal","A piece of scrap metal")
    ]

#list of every recipe
#need to use index of the item in the items list so that the Item object is correct
recipes = [
    Recipe([items[0],items[3],items[3],items[3],items[3],items[3]],items[2]),#create big sword with sword and 5 scrap metal
    Recipe([items[3],items[3]],items[1]),#create chestplate with 2 scrap metal
    Recipe([items[3]],items[0])#create sword with 1 scrap metal
    ] 

iconSize = 20 #size of each tile on the map in pixels
gameMap = []
mapSize = 50 #size of the map

#player stats
player = Player("Player",#name
                10,#health
                5,#damage
                0,#armor
                ["slashes","stabs"],#attack types
                round(mapSize/2),#x position
                round(mapSize/2),#y position
                []#inventory
                )

#enemy that's being fought
currentEnemy = Mob("Enemy",#name
                   1,#health
                   1,#damage
                   1,#armor
                   ["jabs","claws"]#attack types
                   )



"""
setup and start gui
"""
app = gui("Waste Adventure")
app.setSticky("nesw")
app.setStretch("both")





#tabs in the gui
app.startTabbedFrame("main")
app.setTabbedFrameTabExpand("main", expand=True) #expand to fit whole gui
app.setTabbedFrameChangeCommand("main", updateInventory) #when changing tab call updateInventory(), a return in that function prevents it from happening on wrong tab


#title tab
app.startTab("title")
app.setStretch('column')
app.setSticky('esw')
app.addLabel("title", "Waste Adventure")

if(os.path.isfile('./map.txt')):#don't create continue button if no file to load
    if(os.path.isfile('./player.txt')):
        app.addButton("Continue", startGame) #load save
app.addButton("New Game", startGame) #create new save
app.stopTab()

#File menu for saving/loading, functions added after game is started
app.createMenu("File")

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
for slot in player.equipped: #create a label for each equipment slot
    app.addLabel("%s title"%slot,slot.capitalize(),row=itemRow,column=2)
    app.addLabel(slot,player.equipped[slot],row=itemRow,column=3)
    app.setLabelRelief(slot,"ridge")
    app.setLabelTooltip(slot, player.equipped[slot])
    app.setLabelSubmitFunction(slot, player.unEquip) #unequip on click
    
    itemRow += 1
app.stopFrame()
app.stopTab()



#crafting tab
app.startTab("crafting")
app.startFrame("recipes",row=0,column=0)
for recipe in recipes: #recipe list doesn't change so only needs to be done at start of gui
    app.setSticky("ew")  
    app.addLabel(recipe,recipe.crafted.name)
    app.setLabelTooltip(recipe, recipe.description())
    app.setLabelRelief(recipe,"raised")
    app.setLabelSubmitFunction(recipe, showRecipe) #on click
app.stopFrame()

app.addVerticalSeparator(row=0,column=1)

app.startFrame("craftInfo",row=0,column=3)#place where crafting description and button go
app.stopFrame()

app.stopTab()


#combat tab
app.startTab("combat")
app.addLabel("fight","combat")

#player side of combat
app.startFrame("player",row=0,column=0)
app.addLabel("playerName","Player")

app.addMeter("playerHealth",100)
app.setMeterFill("playerHealth","Green")
app.setMeterBg("playerHealth","Red")

app.addLabel("playerDamage","Damage")
app.addLabel("playerArmor","Armor")
app.stopFrame()

app.addVerticalSeparator(row=0,column=1)

#enemy side of combat
app.startFrame("enemy",row=0,column=2)
app.addLabel("enemyName","Name")

app.addMeter("enemyHealth",100)
app.setMeterFill("enemyHealth","Green")
app.setMeterBg("enemyHealth","Red")

app.addLabel("enemyDamage","Damage")
app.addLabel("enemyArmor","Armor")
app.stopFrame()

app.stopTab()


#help tab
app.startTab("help")
app.addLabel("helpLabel","""Use the arrow keys to move around the map.
Click or drag items you want to equip.
When in combat use A to attack, B to block and R to run.""")
app.stopTab()
app.stopTabbedFrame()


#output log
app.startScrollPane("outputPane",row=0,column=3)
app.addLabel("output","")
app.stopScrollPane()


#disable all tabs but title screen
app.setTabbedFrameDisableAllTabs("main", disabled=True)
app.setTabbedFrameDisabledTab("main", "title", disabled=False)

generateMap()
app.bindKeys(["Left","Right","Up","Down","a","b","r"], keys) #bind these keys to 'keys' function

app.registerEvent(rebind) #every second rebind the arrow keys because scrolling unbinds them
app.go()