### ROOM SCHEMATIC
class Interactable:
    
    """
    Base class for all interactable objects.

    Attributes:
        name (string): Display name of interactable.
        description (string): Given description of interactable.
        contains (Interactable list): List of objects contained by interactable.
        useCase (string): Text given when object is interacted with, resulting in no result.
        takeAble (boolen): Value reguarding whether object is able to be grabbed.

    Methods:
        add(item):
            Adds item or list of items to interactable's container.
        remove(item):
            Removes item from interactable's container.
        use(player):
            Has player "use" item, defaulted in returning useCase. Designed to be overloaded.

    """

    def __init__(self, name = "Unanmed Object", description = "Unnamed Description", takeAble = False):
        self.name = name
        self.description = description
        self.contains = []
        self.useCase = "You can't interact with {}.".format(self.name)
        self.takeAble = takeAble
       
    def __str__(self):
        return "Item: {}\nType: {}\nDescription: {}\nContains {} items.".format(self.name, str(type(self)), self.description, len(self.contains)) #Outputs item data

    def add(self, item):
        if type(item) == list:
            self.contains = self.contains + item
        else:
            self.contains.append(item)
    
    def remove(self, item):
        self.contains.remove(item)

    def removeSelf(self, subject):
        if self in subject.contains:
            subject.remove(self)
            return
        if self in inContainer(subject):
            for subobject in subject.contains:
                self.removeSelf(subobject)
        return

    def use(self, player = 0):
        return self.useCase

class Room(Interactable):
    def __init__(self, name = "Unnamed Room", description = "Empty Room", x = 0, y = 0):
        super().__init__(name, description)
        self.worldX = 0; #Location in world
        self.worldY = 0; #Location in world
    
class Wall(Interactable):
    def __init__(self, name = "Unnamed Wall", description = "Blank Wall", direction = "N"):
        super().__init__(name, description)
        self.direction = direction #Directions - Can be N, E, W, or S
    
class Door(Interactable):
    
    def __init__(self, name = "Unnamed Door", description = "Blank Door", key = 0, destination = 0):
        super().__init__(name, description)
        self.key = key
        self.destination = destination
    
    def lock(self, item):
        self.key = item
        
    def setDestination(room):
        destination = room
    
class Player(Interactable):
    def __init__(self, name = "Player", description = "Soulless Husk", room = 0):
        super().__init__(name, description)
        self.health = 100
        self.room = 0
        
    def setRoom(self, room):
        self.room = room
    
    def move(self, door):
        if not (type(door) == Door): #Confirm player is walking through door
            "You can't walk through the {}.".format(door)

        if not (door in inContainer(self.room)): #Confirm door is in room
            return "The {} is not in this room.".format(door.name)
        
        if door.key != 0: #Confirm door is unlocked
            return "The {} is locked.".format(door.name)

        self.room.remove(self) #Pass player through door
        self.setRoom(door.destination)
        door.destination.add(self)

        return "You move to the {}.".format(self.room.name) #Output feedback
    
    def grab(self, obj):
        if not (obj in inContainer(self.room)): #Confirm object is in room
            return "The {} is not in this room.".format(obj.name)
        if not obj.takeAble: #Confirm object is takeAble
            return "You cannot grab the {}.".format(obj.name)
        
        obj.removeSelf(self.room)
        self.add(obj)
        
        return "You grab the {}.".format(obj.name)
    
    def look(self, obj):
        if obj.name == "Nothing":
            return "You can't see that."

        #Code below might be unnecessary, as only items in room can be selected.

        #if not (obj in inContainer(self.room)): #Confirm object is in room 
        #    return "The {} is not in this room".format(obj.name)
        
        if obj == self:
            return self.checkInventory()

        return "You look at the {}. {}".format(obj.name, obj.description)
    
    def checkInventory(self):
        output = ""
        output += "You look in your pockets.\n"
        if self.contains == []:
            output += "You find nothing."
            
        elif len(self.contains) == 1:
            output += "You find a {}.".format(self.contains[0].name)
        else:
            output += "You find the following items:\n"
            for item in self.contains:
                output += "-{}\n".format(item.name)
            output = output[:-1]
        return output

"""Possible Commands:
Look
Use
Unlock
Fight
Break
Grab
Drop
Move
"""

    

### ------------------------------------------------------------------

# Text Processing
aliases = {}
with open("aliases.csv", "r") as f: #CSV File Reading
    for line in f:
        dat = line[:-1].split(",")
        aliases[dat[0]] = dat[1]

def getAlias(text):

    text = text.lower()
    try:
        return aliases[text]
    except:
        return text


### Player Actions ------------------------------------------------------------------

# TODO: Add case for looking up, down, and "around", as well as putting cases in user obj

def lookDirection(player, direction): 
    wall = ""
    for object in player.room.contains:
        if isinstance(object, Wall):
            if object.direction == direction:
                wall = object
    
    if wall == "":
        print("There is no wall there.")
        return
    
    print("You look at the " + wall.name + ". It's description is " + wall.description)
    print("On the wall you see the following objects: ")
    #printItems(player) #TODO: FIX
    
def LookObject(player, object):
    #Check if object is in room, or is the room
    room = player.room
    if not (object in inContainer(room) or object == room):
        print("You can't see anything of that description in this room.")
        return
    print("You see the " + object.name + ". It has the description '" + object.description + "'")
        
# Build Room -----------------------------------------------------------------------
user = Player("You", "It's you! Very Handsome!")
Living = Room("Living Room", "Looks like hone.", 0, 0)
Dining = Room("Dining Room", "It smells warm.", 0, -1)

north_Living = Wall("North Wall", "A wall painted red, facing north.", "N")
east_Living = Wall("East Wall", "A wall painted yellow, facing east. There is a key hanging on the wall.", "E")
south_Living = Wall("South Wall", "A wall painted Blue, facing south. On it there is an oak door.", "S")
west_Living = Wall("West Wall", "A wall painted Green, facing west. ", "W")

north_Dining = Wall("Red Wall", "A wall painted red, facing north. On it there is an oak door.", "N")
east_Dining = Wall("Yellow Wall", "A wall painted yellow, facing east.", "E")
south_Dining = Wall("Blue Wall", "A wall painted Blue, facing south.", "S")
west_Dining = Wall("Green Wall", "A wall painted Green, facing west. ", "W")

brassKey = Interactable("Brass Key", "It's slightly rusted. You're not sure if brass can rust.", takeAble = True)
chair = Interactable("Wooden Chair", "It looks uncomfortable.", takeAble = True)

east_Living.add(brassKey)
Dining.add(chair)

Living.add([north_Living, east_Living, south_Living, west_Living])
Dining.add([north_Dining, east_Dining, south_Dining, west_Dining])

door_south_Living = Door("Oak Door", "It looks locked.", key = 0, destination = Dining)
door_north_Dining = Door("Oak Door", "It looks unlocked.", key = 0, destination = Living)

south_Living.add(door_south_Living)
north_Dining.add(door_north_Dining)

user.setRoom(Living)
Living.add(user)

world = Interactable("World", "The universe")
world.add([Living, Dining])

# ------------------------------------------------------------------------------------------

#Helper object methods
def inContainer(obj, recursive = True):
    '''
    Returns every object contained in an object.

    Parameters:
        obj (interactable): The parent object, of which to be searched.
        recursive (boolean): Setting to check sub-contents of content objects.
        
    Returns:
        items (list): List of found objects within obj.
    '''
    
    items = []
    for item in obj.contains:
        if recursive:    
            items += inContainer(item, recursive = True)
        items.append(item)
    return items

def objectTree(obj, depth = 0):
    """Prints a tree of all known objects behind a given object.

    Args:
        obj (Interactable): Root object for search
        depth (int, optional): Depth of recursion, used for tree visual. Defaults to 0.
    """
    print((depth * 1 * "\t") + obj.name)
    for item in obj.contains:
        objectTree(item, depth = depth + 1)

def main():
    debug = False
    
    print("You stand in a room.")

    response = ""
    while response != "quit":
        response = input("> ")
        if response == "quit":
            continue
        if response == "debug":
            print("Running in debug mode.")
            debug = True
            continue

        verb = "None"
        noun = "None"
        adjective = "None"

        #Define Possible Actions
        verbs = ["look", "grab", "move"]
        nouns = {"room" : user.room}
        adjectives = ["N", "E", "W", "S"]
        for item in inContainer(user.room):
            nouns[item.name.lower()] = item

        if debug:
            print("Selectable Objects: ")
            for item in nouns:
                print(item + ", ", end="")
            print()


        terms = response.split() #Parse Terms, Define Subjects
        for term in terms: 
            term = getAlias(term)
            if term in verbs:
                verb = term
            elif term in nouns:
                noun = term
            elif term in adjectives:
                adjective = term
            else:
                for sub in nouns:
                    if term in sub:
                        noun = sub

        
        

        #Reasign strings to objects
        subject = Interactable("Nothing", "Nothing")

        if noun != "None":
            subject = nouns[noun]

        if noun == "self": #Inventory Commands
            if verb == "None":
                verb = "look"

        if noun == "wall" or noun == "None": #Check for wall noun
            if adjective == "None":
                adjective = "N"
            
            for item in user.room.contains:
                if type(item) == Wall:
                    if item.direction == adjective:
                        subject = item
        
        if debug: print("Verb:\t\t{}\nNoun:\t\t{}\nAdjective:\t{}".format(verb, noun, adjective))
        if debug: print("Subject: {}\t".format(subject.name))

        # Run Commands
        if (verb == "look"): #Run "Look"
            if subject.name == "Nothing":
                print("You can't look there.")
            else:
                print(user.look(subject))

        if (verb == "move"): #Run "Move"
            if subject.name == "Nothing":
                print("You can't move there.")
            elif type(subject) == Wall: # Case like "Move South"
                for obj in inContainer(subject):
                    if type(obj) == Door:
                        subject = obj
                        print(user.move(subject))
            elif type(subject) == Door: # Case like "Move through Door"
                print(user.move(subject))
            else:
                print("You can't move that.")

        if (verb == "grab"): #Run "Grab"
            if subject.name == "Nothing":
                print("You can't see anything of that name.")
            else:
                print(user.grab(subject))

main()



