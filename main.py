
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
						if len(lines) > 2:
							attribute = lines.pop(0)
							value = lines.pop(0)
							room_attributes[attribute] = value
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
			while fold(add,0,map(getSize,furniture_in_room)) < random.random() * room_size:
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
				this_item = peak_furniture[random.randint(0,len(peak_furniture) - 1)]
				furniture_in_room.append(this_item)
				print("Adding " + repr(this_item) + "\n")
			else:
				modifiers = calculate_modifiers(room_types, furniture_in_room)
				print(modifiers)
				peak_modifiers = fold(max_list, [], modifiers.items())
				print(peak_modifiers)
				peak_modifier = peak_modifiers[0][0]
				room_satisfaction[peak_modifier] += 1
				print(room_satisfaction)
				self.rooms.append(Room(peak_modifier, furniture_in_room, []))
		#print(self.rooms)


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
		self.connections = []
	def connect_room(self, room):
		self.connections.append(room)
	def __repr__(self):
		return "\n" + repr(self.theme) + "\n" + repr(self.furniture)



"""
class Character:
	def __init__(self, traits, actions):
		self.traits = traits
		self.actions = actions
		self.goal = current_worldstate

class Player(Character):
	pass

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
var = input()
print(var)