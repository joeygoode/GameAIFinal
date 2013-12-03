
import os
import random
import math

random.seed()

class World:
	def __init__(self, rooms):
		self.rooms = rooms
	def __init__(self):
		def parse_furniture_file(room_types, furniture):
			with open("furniture_list.txt") as room_file:
				for line in room_file:
					if line == "\n": continue
					lines = line.split()
					if lines[0] == "##":
						continue
					elif lines[0] == "Type":
						room_type = lines[1]
						lines.pop(0)
						lines.pop(0)
						room_attributes = dict()
						while lines != ["->"] and len(lines) > 2:
							attribute = lines.pop(0)
							value = lines.pop(0)
							room_attributes[attribute] = value
						if lines == "->":
							for attributes_line in room_file:
								if attributes_line == "\n":
									break
								split_line = attributes_line.split()
								if split_line[0] == ":":
									if split_line[1] == "near":
										room_attributes["near"].append(split_line[2])
						room_types[room_type] = room_attributes
					elif lines[0] == "Furniture":
						this_item = Furniture(lines[1])
						if (lines[2] == "->"):
							for attributes_line in room_file:
								if attributes_line == "\n":
									break
								else:
									split_line = attributes_line.split()
									if split_line[0] == ":":
										room_type = split_line[1]
										if room_type in room_types.keys():
											room_modifier = int(split_line[2])
											this_item.modifiers[room_type] = room_modifier
									if split_line[0] == "$":
										attribute_name = split_line[1]
										attribute_value = int(split_line[2])
										this_item.attributes[attribute_name] = attribute_value
						furniture.append(this_item)
		def are_rooms_satisfied(room_satisfaction, room_types):
			for k in room_types.keys():
				minimum = int(room_types[k].get("minimum", 0))
				maximum = int(room_types[k].get("maximum", 0))
				if minimum > room_satisfaction[k]:
					return False
				if maximum != 0 and maximum < room_satisfaction[k]:
					return False
			else:
				return True
		def calculate_modifiers(room_types, furniture_in_room):
			modifiers = dict()
			for k in room_types.keys():
				modifiers[k] = 0
				for f in furniture_in_room:
					modifiers[k] = modifiers[k] + f.modifiers.get(k,0)
			return modifiers
		def adjust_modifiers(room_types, room_satisfaction, modifiers):
			for k in modifiers.keys():
				satisfaction = int(room_satisfaction[k])
				modifiers[k] += 10 * (max(int(room_types[k].get("minimum", 0)), satisfaction) - satisfaction)
				modifiers[k] -= 1000 * (satisfaction - min(int(room_types[k].get("maximum", 2000)), satisfaction))
			return modifiers
		self.rooms = []
		room_list = []
		room_types = dict()
		furniture = []
		parse_furniture_file(room_types, furniture)
		print(room_types)
		print("\n")
		print(furniture)
		room_satisfaction = dict()
		for k in room_types.keys():
			room_satisfaction[k] = 0
		rooms = []

		input("About to set up rooms...")
		
		while random.random() > .5 or not are_rooms_satisfied(room_satisfaction, room_types) :
			furniture_in_room = []
			room_size = random.randint(75,125)
			def getSize(f):
				return f.attributes.get("size", 0)
			def max_list(e, l):
				if not l:
					return [e]
				elif e[1] > l[0][1]:
					return [e]
				elif e[1] < l[0][1]:
					return l
				else:
					l[len(l):] = [e]
					return l
			while fold(add,0,map(getSize,furniture_in_room)) < room_size:
				modifiers = calculate_modifiers(room_types, furniture_in_room)
				modifiers = adjust_modifiers(room_types, room_satisfaction, modifiers)
				peak_modifiers = fold(max_list, [], modifiers.items())
				def is_peak_furniture(f):
					for m in peak_modifiers:
						if int(f.modifiers.get(m[0], 0)) > 0:
							return True
					else:
						return False
				peak_furniture = list(filter(is_peak_furniture, furniture))
				while(peak_furniture):
					this_item = peak_furniture[random.randint(0,len(peak_furniture) - 1)]
					if this_item.attributes.get("maximum",0) > 0:
						count = 1
						for f in furniture_in_room:
							if f.name == this_item.name:
								count += 1
						if count > this_item.attributes["maximum"]:
							peak_furniture.remove(this_item)
						else:
							break
					else:
						break
				else:
					break
				furniture_in_room.append(this_item)
				print("Adding " + repr(this_item) + "\n")
			
			modifiers = calculate_modifiers(room_types, furniture_in_room)
			peak_modifiers = fold(max_list, [], modifiers.items())
			peak_modifier = peak_modifiers[0][0]
			room_satisfaction[peak_modifier] += 1
			rooms.append(Room(peak_modifier, furniture_in_room, []))
		print(rooms)
		current_room = Room("outside",[],[])
		del current_room.connections["up"]
		del current_room.connections["down"]
		self.rooms.append(current_room)
		while rooms:
			next_room = rooms[random.randint(0,len(rooms) - 1)]
			rooms.remove(next_room)
			nearby_room_types = []
			for k,v in room_types.items():
				if k == "near" and v == next_room.theme:
					nearby_room_types.append[k]
			adjacent_room = None
			adjacent_connection = None
			if nearby_room_types:
				possible_nearby_rooms = list(filter(lambda r: r.theme() in nearby_room_types, self.rooms))
				while possible_nearby_rooms:
					adjacent_room = possible_nearby_rooms[random.randint(0,len(possible_nearby_rooms)- 1)]
					connections = adjacent_room.connections.items()
					random.shuffle(connections)
					for k,v in connections:
						if v == None:
							adjacent_connection = k
							break
				else:
					adjacent_room = self.rooms[random.randint(0,len(self.rooms) - 1)]
					connections = adjacent_room.connections.items()
					random.shuffle(connections)
					for k,v in connections:
						if v == None:
							adjacent_connection = k
			else:
				adjacent_room = self.rooms[random.randint(0,len(self.rooms) - 1)]
				connections = list(adjacent_room.connections.items())
				random.shuffle(connections)
				for k,v in connections:
					if v == None:
						adjacent_connection = k
			def get_opposite_connection(direction):
				if direction == "up":
					return "down"
				elif direction == "down":
					return "up"
				elif direction == "east":
					return "west"
				elif direction == "west":
					return "east"
				elif direction == "north":
					return "south"
				elif direction == "south":
					return "north"
				else:
					return None
			def get_connection_search_directions(direction):
				if direction == "up" or direction == "down":
					return ["north","south","east","west"]
				elif direction == "east" or direction == "west":
					return ["north","south","up","down"]
				elif direction == "north" or direction == "south":
					return ["east","west","up","down"]
				else:
					return None
			adjacent_room.connections[adjacent_connection] = next_room
			next_room.connections[get_opposite_connection(adjacent_connection)] = adjacent_room
			for direction in get_connection_search_directions(adjacent_connection):
				if adjacent_room.connections.get(direction,None) == None:
					continue
				if adjacent_room.connections[direction].connections.get(adjacent_connection,None) == None:
					continue
				adjacent_room.connections[direction].connections[adjacent_connection].connections[get_opposite_connection(direction)] = next_room;
				next_room.connections[direction] = adjacent_room.connections[direction].connections[adjacent_connection]
		self.characters = []
		self.characters.append(Player([], [], random.choice(self.rooms)))
		print(self.rooms)
	def update(self):
		for char in self.characters:
			char.select_action(self)
		

def fold(function, base, l):
	for e in l:
		base = function(e,base)
	return base;

def add(a, b):
	return a + b

class Furniture:
	def __init__(self, name):
		self.name = name
		self.modifiers = dict()
		self.attributes = dict()
	def __repr__(self):
		string = "\n" + self.name + ": \n"
		string = string + repr(self.modifiers) + "\n"
		string = string + repr(self.attributes)
		return string

class Room:
	def __init__(self, theme, furniture, people):
		self.theme = theme
		self.furniture = furniture
		self.people = people
		self.connections = {"north":None, "south":None, "east":None, "west":None, "up":None, "down":None}
	def __repr__(self):
		return "\n" + repr(self.theme) + "\n" + repr(self.furniture)




class Character:
	def __init__(self, traits, actions, location):
		self.traits = traits
		self.actions = actions
		# self.goal = current_worldstate
		self.location = location
	def __repr__(self):
		return "\nCharacter at " + repr(self.location) + "\n"

class Player(Character):
	def select_action(self, world):
		instring = input(">> ")
		for act in self.actions:
			if act == instring:
				act.attempt(self, world)
				return
		print("\nInvalid Command\n")

# precondition functions ==============================================

def room_in_direction(character, direction):
        if (character.location.connections[direction] == None):
                return False
        else:
                return True

def room_to_north(character, world):
        return room_in_direction(character, "north")

def room_to_south(character, world):
        return room_in_direction(character, "south")

def room_to_east(character, world):
        return room_in_direction(character, "east")

def room_to_west(character, world):
        return room_in_direction(character, "west")

def room_to_up(character, world):
        return room_in_direction(character, "up")

def room_to_down(character, world):
        return room_in_direction(character, "down")

# effect functions ====================================================

def goto_direction(character, direction):
        character.location = character.location.connections[direction]

def goto_north(character, world):
        goto_direction(character, "north")

def goto_south(character, world):
        goto_direction(character, "south")

def goto_east(character, world):
        goto_direction(character, "east")

def goto_west(character, world):
        goto_direction(character, "west")

def goto_up(character, world):
        goto_direction(character, "up")

def goto_down(character, world):
        goto_direction(character, "down")
        

class Action:
	def __init__(self, preconditions, effects, command, report_success, report_failure):
		self.preconditions = preconditions
		self.effects = effects
		self.command = command
		self.report_success = report_success
		self.report_failure = report_failure
	def attempt(self, character, world):
		for cond in self.preconditions:
			if not cond(character, world):
				if(isinstance(character, Player)):
					print("\n" + self.report_failure + "\n")
				return False
		# preconditions all true, now process effects
		for eff in self.effects:
			eff(character, world)
			if(isinstance(character, Player)):
				print("\n" + self.report_success + "\n")
		return True



"""

class KnowledgeRepresentation:
	def __init__(self):
		self.room_knowledge = []
		self.character_knowledge = []
		self.event_knowledge = []


class RoomKnowledge:
	def __init__(self, room, entity):
		self.room = room
		self.entity = entity
	def update(self, room, entity):
		if entity == self.entity:
			self.room = room

class CharacterKnowledge:
	def __init__(self, character, entity):
		self.character = character
		self.entity = entity
	def update(self, character, entity):
		if entity == self.entity:
			self.character = character

class EventKnowledge:
	def __init__(self, character, action, targets):
		self.character = character
		self.action = action
		self.targets = targets

class Trait:
	def __init__(self, kr_to_score):
		self.function = kr_to_score
	def evaluate(self, knowledge_representation):
		return self.function(knowledge_representation)
"""
print("Hello World")
world = World()
while(True):
	world.update()
