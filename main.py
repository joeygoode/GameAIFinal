
import os

class World:
	def __init__(self, rooms):
		self.rooms = rooms
	def __init__(self):
		self.rooms = []
		room_list = []
		room_types = dict()
		furniture = dict()
		with open("furniture_list.txt") as room_file:
			for line in room_file:
				if line == "\n": continue
				lines = line.split()
				if lines[0] == "Type":
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
					furniture_name = lines[1]
					furniture[furniture_name] = dict()
					if (lines[2] == "->"):
						for attributes_line in room_file:
							if attributes_line == "\n":
								break
							else:
								split_line = attributes_line.split()
								if (split_line[0] == ":"):
									room_type = split_line[1]
									room_modifier = split_line[2]
									furniture[furniture_name][room_type] = room_modifier
		print(room_types)
		print("\n")
		print(furniture)
		



class Room:
	def __init__(self, furniture, people):
		self.furniture = furniture
		self.people = people
		self.connections = []
	def connect_room(self, room):
		self.connections.append(room)



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