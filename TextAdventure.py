"""
There are two primary systems to this text adventure game, the objects, and the text engine.

Every item in this game, including the player, is an "Interactable", with relevant statitistics based on the item type.
One thing in common with all interactables is that they have a container, which is objects they store.
The world is linked through several stored objects inside each other, or with links provided by door objects.

The following is a list of item types with their properties:

    Interactable (Base Class):
        This is the most basic layer of class. They, and every other item, has the following properties:
            Name: The given name of the object, which is searched when interacted with in the text engine
            Description: A description of the object when looked at. The contained items are also displayed, so that a "Chest" item will reveal the "Treasure" inside when searched.
            Contains: A list of contained items.
            UseCase: Text displayed when interacted with, if not already another item.
            TakeAble: Value determining whether object can be picked up or dropped.
            BreakAble: Value determining whether object can be broken.
            BrokenItem: Item dropped when broken. This can be used to "hide" items. For instance, a crate can drop a broken crate, which contains a sword. The broken crate and the sword will not be shown when the crate is inspected.
            BreakKey: Object needed in Player's inventory to break item. Can be any Interactable.

    Room: 
        Has stored coordinates (currently UNUSED) and is pointed to by Player objects as an area to be interacted with.
        Players can only interact with items in the same room they are in.

    Wall:
        Has a stored direction, so that when a Player "Looks Left" they are directed to the Wall in their room with the matching orientation.

    Door:
        Has a linked destination and can be locked with a defined item (currently only keys can unlock doors). 

    Key:
        Has a saved "target" to search for, assumedly a Door object. When used, if the target object is in the same room as the player, the door unlocks.

    Player:
        Has a defined room, and all actions run through Player.
        The player's "contains" serves as the inventory for purposes of picking up and dropping objects.

Nested objects can be difficult to sort through, so a helper class objectTree() was created to print out every avalible item behind a larger one.
Hidden objects are denoted with a "-" symbol behind the item
An example tree is attached, in the file worldTree.txt.
                
The text engine runs by taking user input as a string, splitting up the string into the defined noun, verb, and adjective.
Before assigning terms, each term in the input is run through an alias dictionary, converting similar words into a set of predefined words. (Changing "Steel" to "Metal")
In a perfect system, the noun points to an Interactable, which is then passed to a method in the Player object defined by the Verb.
Obviously there are edge cases where assumptions have to be made, for example the input "Look" implies the noun "Room", and other similar cases.
There are also cases where multible targets are selected, for instance, "look at wall" can imply four different walls, so the first result is defaulted to, unless an included adjective can break the tie.
For example, "Open Oak Door" reconizes "Door" as the noun, sees "Oak Door" and "Steel Door" in room, and selects "Oak Door" from a reconized "Oak" adjective.

For the purpose of debugging, the command "debug" can be run, which shows more informational data reguarding the series of events.
"""

### ROOM SCHEMATIC
class Interactable:
    
    """
    Base class for all interactable objects.

    Attributes:
        name (string): Display name of interactable.
        description (string): Given description of interactable.
        contains (Interactable list): List of objects contained by interactable.
        useCase (string): Text given when object is interacted with, resulting in no result.
        takeAble (boolean): Value reguarding whether object is able to be grabbed.
        breakAble (boolean): Value reguarding whether object is able to be broken.
        brokenItem (boolean): Item dropping in place when Interactable is broken
        breakKey (boolean): Item that can break Interactable

    Methods:
        add(item):
            Adds item or list of items to interactable's container.
        remove(item):
            Removes item from interactable's container.
        removeSelf(subject):
            Removes self from any item contained within subject and its subcontainers.
        use(player):
            Has player "use" item, defaulted in returning useCase.
        destroy(player):
            Has player "destroy" item, if possible.

    """

    def __init__(self, name = "Unanmed Object", description = "Unnamed Description", takeAble = False, customUseText = "", breakAble = False, brakeContent = 0, breakKey = 0):
        self.name = name
        self.description = description
        self.contains = []
        self.useCase = customUseText
        self.breakAble = breakAble
        if customUseText == "":
            self.useCase = "You can't interact with {}.".format(self.name)
        self.takeAble = takeAble
        self.brokenItem = brakeContent
        self.breakKey = breakKey
        
    def __str__(self):
        return "Item: {}\nType: {}\nDescription: {}\nContains {} items.".format(self.name, str(type(self)), self.description, len(self.contains)) #Outputs item data

    def add(self, item):
        """
        Adds item or list of items into Interactable's container.

        Parameters:
            item (Interactable): The item being added.
            item (list of Interactable): List of items being added.
        """
        if type(item) == list:
            self.contains = self.contains + item
        else:
            self.contains.append(item)
    
    def remove(self, item):
        """
        Removes item from Interactable's container, if possible.

        Parameters:
            item (Interactable): The item being removed.
        """
        if item in self.contains:
            self.contains.remove(item)

    def removeSelf(self, subject):
        """
        Searches for instnaces of self within container of "subject" as well as subcontainers, and removes self from containers.

        Parameters:
            subject (Interactable): The container holder of which to be searched.
        """
        if self in subject.contains:
            subject.remove(self)
            return
        if self in inContainer(subject):
            for subobject in subject.contains:
                self.removeSelf(subobject)
        return

    def use(self, player = 0):
        """
        Executes when Player "uses" Interactable, returns "useCase" text.

        Parameters:
            player (Player): The player running the action.
        """
        if player == 0:
            return "Who is using the {}?".format(self.name)
        return self.useCase
    
    def destroy(self, player = 0):
        """
        When player tries to destroy Interactable, the following is considered:

        Is a player breaking Interactable?
        Is Interactable breakable?
        Does Interactable drop any items?
        Does Interactable need to be broken with a specific item?

        If the player can break the item, the item breaks, leaving behind an item if necessary.

        Parameters:
            player (Player): The player running the action.
        """

        if player == 0:
            return "Who is breaking the {}?".format(self.name) #No Player
        elif not self.breakAble:
            return "You can't break the {}.".format(self.name) #Not Breakable
        elif self.breakKey == 0: #Breakable without item
            self.removeSelf(player.room)
            if self.brokenItem != 0:
                player.room.add(self.brokenItem)
                return "You destroy the {}, leaving behind a {}.".format(self.name, self.brokenItem.name) #Holds item
            return "You destroy the {}.".format(self.name) #Doesn't hold item
        elif not self.breakKey in player.contains: #Breakable with item
            return "You need a {} to break the {}.".format(self.breakKey.name, self.name) #Player does not have item
        else:
            self.removeSelf(player.room)
            if self.brokenItem != 0:
                player.room.add(self.brokenItem)
                return "You destroy the {} with the {}, leaving behind a {}.".format(self.name, self.breakKey.name, self.brokenItem.name) #Holds item
            return "You destroy the {} with the {}.".format(self.name, self.breakKey.name) #Doesn't hold item

class Room(Interactable):
    """
    Class for "Room" objects. Acts as any other object, but with viewing priority and coordinate positions.

    Attributes:
        x (int): X coordinate of room (Currently UNUSED)
        y (int): Y coordinate of room (Currently UNUSED)
    """
    def __init__(self, name = "Unnamed Room", description = "Empty Room", x = 0, y = 0):
        super().__init__(name, description)
        self.worldX = 0; #Location in world
        self.worldY = 0; #Location in world
    
class Wall(Interactable):
    """
    Class for "Wall" objects. Acts as any other object, but with an assigned orientation and viewing priority.

    Attributes:
        Direction (string): Direction of the wall. Has to be "N", "E", "S", or "W"

    """
    def __init__(self, name = "Unnamed Wall", description = "Blank Wall", direction = "N"):
        super().__init__(name, description)
        self.direction = direction #Directions - Can be N, E, W, or S
    
class Door(Interactable):
    """
    Base class for all "Door" objects.

    Attributes:
        key (Key): Item required to unlock door.
        destination (Room): Destination of door when passed through.

    Methods:
        lock(item):
            Locks door, with selected item serving as a key.
        setDestination(room):
            Sets destination of door, or location that will be gone to when passed through.
        use(player):
            Passes player through door if unlocked.
        
    """

    def __init__(self, name = "Unnamed Door", description = "Blank Door", key = 0, destination = 0):
        super().__init__(name, description)
        self.key = key
        self.destination = destination
    
    def lock(self, item):
        self.key = item
        
    def setDestination(self, room):
        self.destination = room

    global debug
    def use(self, player = 0):
        if debug: print("=== {} is being opened. Key: '{}'. {}.".format(self.name, self.key, self.key != 0))
        return player.move(self)
    
class Player(Interactable):
    """
    Base class for all "Player" objects.

    Attributes:
        room (Room): Room player is contained in.
        health (int): Health of player. Currently UNUSED.

    Methods:
        setRoom(Room):
            Sets player's room to "room".
        move(Door):
            Moves player through door.
        grab(Interactable):
            Adds item to inventory (contains), if possible.
        look(Interactable):
            Has player look at item.
        use(Interactable):
            Has player "use" item, if possible.
        unlock(Interactable):
            If Item is a Door, unlock it.
        drop(Interactable):
            If item is in inventory, drop it in current room.
        destroy(Interactable):
            Break Interactable, if possible.
        checkInventory():
            Returns player's inventory.
    """
    
    def __init__(self, name = "Player", description = "Soulless Husk", room = 0):
        super().__init__(name, description)
        self.health = 100
        self.room = room
        
    def setRoom(self, room):
        self.room = room
    
    def move(self, door):
        #print(door.name)
        if not (type(door) == Door): #Confirm player is walking through door
            "You can't walk through the {}.".format(door)

        if not (door in inContainer(self.room)): #Confirm door is in room
            return "The {} is not in this room.".format(door.name)
        
        if door.key != 0: #Confirm door is unlocked
            if debug: print("=== {} locked. Key: '{}'".format(door.name, door.key))
            return "The {} is locked.".format(door.name)

        self.room.remove(self) #Pass player through door
        self.setRoom(door.destination)
        door.destination.add(self)

        return "You move through the {} into the {}.".format(door.name, self.room.name) #Output feedback
    
    def grab(self, obj):
        if not (obj in inContainer(self.room) or obj == self.room): #Confirm object is in room
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

        output = "You look at the {}. {}".format(obj.name, obj.description) #Nested items.
        objectContents = obj.contains.copy()
        if self in objectContents: objectContents.remove(self)
        if (objectContents != []):
            if len(objectContents) == 1:
                output += "\nInside the {}, you see a {}.".format(obj.name, objectContents[0].name)
            else:
                output += "\nInside the {}, you see multible items:".format(obj.name)
                for item in objectContents:
                    output += "\n-{}".format(item.name)
        return output
    
    def use(self, obj):
        if obj.name == "Nothing":
            return "You can't use that."
        elif obj.takeAble and not obj in self.contains:
            return "You need to pick up the {} first.".format(obj.name)
        else:
            return obj.use(player = self)
    
    def unlock(self, obj):
        if obj.name == "Nothing":
            return "What do you want to unlock?"
        if type(obj) != Door:
            return("You can't unlock the {}.".format(obj.name))
        elif obj.key == 0:
            return("The {} is already unlocked.".format(obj.name))
        else:
            if obj.key in inContainer(self):
                output = ("You unlock the {} with the {}.".format(obj.name, obj.key.name))
                obj.key = 0
                return output
            else:
                return "You don't have a key."

    def drop(self, obj):
        if not obj in self.contains:
            return "You can't drop something you don't have."
        else:
            self.remove(obj)
            self.room.add(obj)
            return "You drop the {} in the {}.".format(obj.name, self.room.name)

    def destroy(self, obj):
        if obj == self:
            return "You can't be harmed! You're the protaginist!"
        return obj.destroy(self)

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

class Key(Interactable):
    """
    Base class for all "Key" objects.

    Attributes:
        target (Room): Target of what "Key" unlocks.

    Methods:
        use(Player):
            Checks if "target" is in same room as Player, unlocks if possible.
        setTarget(Interactable):
            Moves player through door.
    """

    def __init__(self, name = "Unnamed Door", description = "Blank Door", target = 0, takeAble = True):
        super().__init__(name, description, takeAble)
        self.target = target

    def use(self, player = 0):
        if player == 0:
            return "Who is using the {}?".format(self.name)
        if self.target == 0:
            return "This key does not go anywhere new."
        if self.target in inContainer(player.room):
            output = "You unlock the {} with the {}.".format(self.target.name, self.name)
            self.target.key = 0
            self.target = 0
            return output
        else:
            output("You can't unlock anything in this room with the {}.".format(self.name))

    def setTarget(self, obj):
        self.target = obj

### ------------------------------------------------------------------

# Text Processing : Condenses several words on CSV file to small set of possible terms
aliases = {}
with open("aliases.csv", "r") as f: #CSV File Reading
    for line in f:
        dat = line[:-1].split(",")
        aliases[dat[0]] = dat[1]

def getAlias(text):
    '''
    Returns an alias for a given text input.

    Parameters:
        text (string): Single term to search, no whitespace included.
        
    Returns:
        items (string): Condensed synynom of word for processing, returns same word if none found.
    '''

    text = text.lower()
    try:
        return aliases[text]
    except:
        return text

def reverseAlias(text):
    '''
    Returns every synynom for a given word in the alias dict.

    Parameters:
        text (string): The string to reverse search.
        
    Returns:
        items (list): List of found reverse-searched strings.
    '''

    output = []
    for alias in aliases:
        if aliases[alias] == text:
            output.append(alias)
    return output
        
# Build Room -----------------------------------------------------------------------

# Room creation - Currently manual but planned to be procedural.
def generateWorld(returnPlayer = True):

    """
    Generates a sample game world.

    Parameters:
        returnPlayer(boolean, optional): Returns Player if true, World if false.

    Returns: 
        Player in world, or world object itself if returnPlayer is false.
    """

    #Creates user in rooms
    user = Player("Self", "It's you! Very Handsome!")
    Living = Room("Living Room", "A lovely living room, with each wall painted a different color. On the south wall, there is an oak door. On the east wall, there is a metal door.", 0, 0)
    Dining = Room("Dining Room", "A cute little kitchen. There is an oak door on the south wall.", 0, -1)
    Bedroom = Room("Bedroom", "A cozy bedroom. There is nothing of note inside it.", 1, 0)

    #Creates Living Room Walls
    north_Living = Wall("North Wall", "A wall painted red, facing north.", "N")
    east_Living = Wall("East Wall", "A wall painted yellow, facing east.", "E")
    south_Living = Wall("South Wall", "A wall painted Blue, facing south.", "S")
    west_Living = Wall("West Wall", "A wall painted Green, facing west. There is a key hanging on the wall.", "W")

    #Creates Dining Room Walls
    north_Dining = Wall("Red Wall", "A wall painted red, facing north.", "N")
    east_Dining = Wall("Yellow Wall", "A wall painted yellow, facing east.", "E")
    south_Dining = Wall("Blue Wall", "A wall painted Blue, facing south.", "S")
    west_Dining = Wall("Green Wall", "A wall painted Green, facing west. ", "W")

    #Creates smaller items in rooms
    brassKey = Key("Brass Key", "It's slightly rusted. You're not sure if brass can rust.", takeAble = True)
    chair = Interactable("Wooden Chair", "It looks uncomfortable.", takeAble = True, customUseText = "You sit in the chair. It feels awful.", breakAble = True)
    broken_crate = Interactable("Broken Crate", "The crate has been broken open.", takeAble = True, customUseText = "It's not useful anymore.")
    crate = Interactable("Wooden Crate", "There doesn't look like a way to open this.", takeAble = True, customUseText = "You need to break this to see what is inside.", breakAble = True, brakeContent = broken_crate)
    sword = Interactable("Silvered Sword", "An honored family blade, kept in pristine condition", takeAble = True, customUseText = "The sword feels good in your hands.")
    
    #Put items in their locations
    broken_crate.add(sword)
    west_Living.add(brassKey)
    Dining.add(chair)
    Dining.add(crate)
    
    #Adds Walls to Rooms
    Living.add([north_Living, east_Living, south_Living, west_Living])
    Dining.add([north_Dining, east_Dining, south_Dining, west_Dining])

    #Create bedroom walls
    for n in ["North", "East", "West", "South"]:
        Bedroom.add(Wall("{} Wall".format(n), "A wall on the {} side of the room.".format(n), n[0]))

    #Creates bedroom objects
    Bed = Interactable("Bed", "It looks comfy.", takeAble = False, customUseText = "The bed is occupied.")
    GoldBar = Interactable("Gold Bar", "A very expensive golden bar.", customUseText = "You win!", takeAble = True)
    Monster = Interactable("Monster", "A scary guy, sleeping in the bed.", customUseText = "It doesn't want to be bothered.", breakAble = True, breakKey = sword, brakeContent = GoldBar)

    #Adds bedroom objects to bedroom
    Bed.add(Monster)
    Bedroom.add(Bed)

    #Adds and locks oak door
    door_south_Living = Door("Oak Door", "It has a lock on it.", key = brassKey, destination = Dining)
    brassKey.setTarget(door_south_Living)
    door_north_Dining = Door("Oak Door", "It was unlocked from the other side.", key = 0, destination = Living)
    south_Living.add(door_south_Living)
    north_Dining.add(door_north_Dining)

    #Adds Metal door
    door_east_Living = Door("Metal Door", "Despite being made of metal, it is unlocked.", key = 0, destination = Bedroom)
    east_Living.add(door_east_Living)
    door_west_Bedroom = Door("Metal Door", "Despite being made of metal, it is unlocked.", key = 0, destination = Living)
    Bedroom.contains[2].add(door_west_Bedroom)

    #Adds user to living
    user.setRoom(Living)
    Living.add(user)

    #Adds world object #Currently UNUSED
    world = Interactable("World", "The universe")
    world.add([Living, Dining, Bedroom])

    if returnPlayer: return user
    return world

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

def objectTree(obj, depth = 0, hidden = False):
    """Prints a tree of all known objects behind a given object, including hidden objects. Debugging use only.

    Parameters:
        obj (Interactable): Root object for search
        depth (int, optional): Depth of recursion, used for tree visual. Defaults to 0.
        hidden (bool, optional): Whether or not object is hidden within another object.
    """
    if not hidden:
        print((depth * 1 * "..." + " + ") + obj.name + (50 - (depth * 3 + len(obj.name))) * " " + str(type(obj).__name__))
    else:
        print((depth * 1 * "..." + " - ") + obj.name + (50 - (depth * 3 + len(obj.name))) * " " + str(type(obj).__name__))
    for item in obj.contains:
        objectTree(item, depth = depth + 1)
    if obj.brokenItem != 0:
        objectTree(obj.brokenItem, depth = depth + 1, hidden = True)

#Main Game Loop
def main():
    user = generateWorld()

    global debug
    debug = False
    
    print("Welcome to Text Adventure! Type commands in the provided line to move yourself, interact with items, and hopefully find the secret gold bar!")
    print("You should start by looking around the room you're in.")

    response = ""
    while (response != "quit" and response != "exit"): #Main play loop
        print()
        response = input("> ")
        print()
        if response == "quit" or response == "exit":
            continue
        if response == "debug":
            print("Toggling debug mode")
            debug = not debug
            continue

        verb = "None"
        noun = "None"
        adjective = "None"

        #Define Possible Actions
        verbs = ["help", "look", "grab", "move", "use", "unlock", "drop", "destroy"] #Possible actions
        nouns = {"room" : user.room}
        adjectives = ["N", "E", "W", "S", "red", "yellow", "green", "blue", "oak", "metal", "broken"]
        for item in inContainer(user.room): #"Load" objects in room
            nouns[item.name.lower()] = item

        if debug:
            print("=== Selectable Objects: ", end = "")
            for item in nouns:
                print(item + ", ", end="")
            print()

        #Parse Terms, Define Subjects
        terms = response.split() 
        for term in terms: 
            term = getAlias(term)
            if term in verbs: #Locks in terms based off predefined verbs, nouns, and adjectives
                verb = term
            elif term in nouns:
                noun = term
            elif term in adjectives:
                adjective = term
            else: #If nothing is found from a term, check whether or not item is described partially, preferring ones with matching adjectives
                matches = []
                for sub in nouns:
                    if term in sub:
                        matches.append(sub)
                        #Defaults similar named objects
                if len(matches) == 0: #No objects found
                    pass
                elif len(matches) == 1:
                    noun = matches[0]
                else: #Multible objects with similar name discrepancy
                    if debug and matches != []:
                        print("=== Multible subjects found for term {}:".format(term))
                        print("=== Adjective Matches: " + str(reverseAlias(adjective)))
                        print("=== Checking matches for adjective {}.".format(adjective))
                    for match in matches:
                        if debug: print("=== Possible Subject: " + str(match))
                        for subAdjective in reverseAlias(adjective):
                            if subAdjective in match and len(subAdjective) != 1:
                                noun = match
                                if debug: print("=== Item {} matches adjective {}.".format(match, subAdjective))
                    if noun == "None": #If no object can be found based on adjective, the first one is chosen by default.
                        if debug : print("=== No exact match found, selecting first object, {}.".format(matches[0]))
                        noun = matches[0] #TODO : Maybe change to asking the player? 


        #Reasign strings to objects
        subject = Interactable("Nothing", "Nothing")

        #Set Subject to Noun
        if noun != "None":
            subject = nouns[noun]

        #"self" implied to mean "look at self" or "check inventory"
        if noun == "self" and len(terms) == 1: 
            if verb == "None":
                terms.append("look")
                verb = "look"

        #"look" implied to mean "look at wall" or "look around"
        if (verb == "look"): 
            if len(terms) == 1:
                noun == "room"
                subject = user.room
            elif adjective in ["N", "E", "W", "S"]:
                    for item in inContainer(user.room):
                        if type(item) == Wall:
                            if item.direction == adjective:
                                subject = item

        #"N" or similar implied to mean "move north"
        if (noun == "none" and len(terms) == 1 and adjective in ["N", "E", "W", "S"]):
            noun = "moves"
        
        if debug: 
            print("=== Verb:\t{}\n=== Noun:\t{}\n=== Adjective:\t{}.".format(verb, noun, adjective))
            print("=== Subject: {}\t".format(subject.name))

        # Run Commands
        if (verb == "None"):
            print("I don't understand that action. Type \"Help\" for assistance.")

        if (verb == "help"):
            print("In the provided field, tell me what you do as simply as possible. For example, \"Look Left\" or \"Grab Sword\".")
            print("Suggested Actions: Look, Grab, Move, Use, Drop, Break")

        if (verb == "look"): #Run "Look"
            if subject.name == "Nothing":
                print("You can't look there.")
            else:
                print(user.look(subject))

        if (verb == "move"): #Run "Move"
            if subject.name == "Nothing": #If command like "move north"
                if adjective in ["N", "E", "W", "S"]:
                    for item in inContainer(user.room):
                        if type(item) == Wall:
                            if item.direction == adjective:
                                subject = item
                    
                else:
                    print("You can't move there.") 

            if type(subject) == Wall: # Case like "Move South"
                for obj in inContainer(subject):
                    if type(obj) == Door:
                        subject = obj
                        print(user.move(subject))
                        continue
                if type(subject) != Door:
                    print("There is no door on the {}.".format(subject.name))
            elif type(subject) == Door: # Case like "Move through Door"
                print(user.move(subject))
            else:
                print("You can't move that.")

        if (verb == "grab"): #Run "Grab"
            if subject.name == "Nothing":
                print("You can't see anything of that name.")
            else:
                print(user.grab(subject))

        if (verb == "use"): #Run "Use"
            print(user.use(subject))

        if (verb == "unlock"): #Run Unlock
            print(user.unlock(subject))

        if (verb == "drop"): #Run Drop
            print(user.drop(subject))

        if (verb == "destroy"): #Run Destroy
            print(user.destroy(subject))

main()


