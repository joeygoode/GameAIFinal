
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
		room_satisfaction = dict()
		for k in room_types.keys():
			room_satisfaction[k] = 0
		rooms = []
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
			
			modifiers = calculate_modifiers(room_types, furniture_in_room)
			peak_modifiers = fold(max_list, [], modifiers.items())
			peak_modifier = peak_modifiers[0][0]
			room_satisfaction[peak_modifier] += 1
			rooms.append(Room(peak_modifier, furniture_in_room, []))
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
			self.rooms.append(next_room)
		def parse_trait_file(stats):
			with open("trait_list.txt") as stat_file:
				for line in stat_file:
					if line == "\n":
						continue
					lines = line.split()
					if lines[0] == "##":
						continue
					elif lines[0] == "Stat":
						stat_type = lines[1]


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
	def __init__(self, stats):
		self.stats = stats

class Player:
	def __init__(self,world):
		self.room = world.rooms[0]
		self.isAlive = True

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
world = World()
player = Player(world)
while (player.isAlive):
	print("The room you are in looks like a " + player.room.theme + "\n")
	print("\n")
	for furniture in player.room.furniture:
		print("There is a " + furniture.name + " in the room.\n")
	for k,v in player.room.connections.items():
		if v == None:
			continue
		else:
			print("A " + v.theme + " is to the " + k + ".\n")
	action_accepted = False
	while not action_accepted:
		action = input("-->")
		action_words = action.split()
		print(action_words)
		if len(action_words) == 3:
			if action_words[0] == "go" or action_words[0] == "move":
				if(action_words[1] == "to"):
					for k,v in player.room.connections.items():
						if action_words[2] == k:
							player.room = v;
							action_accepted = True
						elif v != None and action_words[2] == v.theme:
							player.room = v;
							action_accepted = True
				else:
					print("Movement commands require a target.")
			else:
				print("I don't understand you.")
				print(action_words[0])
		elif len(action_words) == 2:
			if action_words[0] == "kill" and action_words[1] == "me":
				print("You are dead.")
				player.isAlive == False
				action_accepted = True
			else:
				print("I don't understand you.")
		else:
			print("I don't understand you.")
			print(len(action_words))


