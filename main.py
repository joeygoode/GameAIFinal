
import os
import random
import math
import functools
from abc import ABCMeta

random.seed()

class World:
	def __init__(self):
		self.rooms = []
		self.characters = []
		def generate_rooms():
			class FurnitureParser:
				def __init__(self, name):
					self.name = name
					self.modifiers = dict()
					self.attributes = dict()
					self.actions = dict()
				def to_furniture(self):
					return Furniture(self.name, self.attributes, self.actions)
			class RoomParser():
				def __init__(self, theme, furniture):
					self.theme = theme
					self.furniture = furniture
					self.connections = {"north":None, "south":None, "east":None, "west":None, "up":None, "down":None}
				def to_room(self):
					return Room(self.theme, map(self.furniture, lambda f: f.toFurniture), self.connections)
				def __repr__(self):
					return "\n" + repr(self.theme) + "\n" + repr(self.furniture)
			def parse_furniture_file(room_types, furniture):
				print("Reading furniture from disk...")
				with open("furniture_list.txt") as room_file:
					for line in room_file:
						if line == "\n": continue
						lines = line.split()
						if lines[0] == "##":
							continue
						elif lines[0] == "Type":
							room_type = lines[1]
							room_attributes = dict()
							if lines[2] == "->":
								for attributes_line in room_file:
									if attributes_line == "\n":
										break
									else:
										split_line = attributes_line.split()
										if split_line[0] == ":":
											if split_line[1] == "near":
												if "near" not in room_attributes:
													room_attributes["near"] = []
												room_attributes["near"].append(split_line[2])
											else:
												room_attributes[split_line[1]] = split_line[2]
							room_types[room_type] = room_attributes
						elif lines[0] == "Furniture":
							this_item = FurnitureParser(lines[1])
							def parse_modifier(line):
								room_type = line[1]
								if room_type in room_types.keys():
									room_modifier = int(line[2])
									this_item.modifiers[room_type] = room_modifier
							def parse_attribute(line):
								attribute_name = line[1]
								if attribute_name == "state":
										this_item.attributes["state"] = line[2]
								else:
									try:
										attribute_value = int(line[2])
									except ValueError:
										attribute_value = line[2]
									this_item.attributes[attribute_name] = attribute_value
							def parse_action(line):
								action_name = line[1]
								action_preconditions = None
								action_effects = []
								for andclause in line[2].split("&"):
									ormap = None
									for orclause in andclause.split("|"):
										entity = orclause.split("=")[0].split(".")[0]
										value = orclause.split("=")[1]
										field = orclause.split("=")[0].split(".")[1]
										ormap = OrCombinator(ormap, Precondition(entity,field,value))
									action_preconditions = AndCombinator(action_preconditions,ormap)
								for effect in line[3].split(","):
									variable = effect.split("=")[0].split(".")[0]
									field = effect.split("=")[0].split(".")[1]
									try:
										value = int(effect.split("=")[1])
										if (field[-1] == "+"):
											action_effects.append(IncrementorEffect(variable, field[:-1], value))
										elif (field[-1] == "-"):
											action_effects.append(DecrementorEffect(variable, field[:-1], value))
										else:
											action_effects.append(Effect(variable, field, value))
									except ValueError:
										value = effect.split("=")[1]
										action_effects.append(Effect(variable, field, value))
								this_item.actions[str(action_name)] = Action(action_preconditions, action_effects, "Success!", "Failed.")
								print(action_name + ": " + repr(Action))
								print(action_name == "sit")
							if (lines[2] == "->"):
								for attributes_line in room_file:
									if attributes_line == "\n":
										break
									else:
										split_line = attributes_line.split()
										if split_line[0] == ":":
											parse_modifier(split_line)
										elif split_line[0] == "$":
											parse_attribute(split_line)
										elif split_line[0] == ">":
											parse_action(split_line)
							furniture.append(this_item)
			def are_rooms_satisfied(room_satisfaction, room_types):
				for k in room_types.keys():
					minimum = int(room_types[k].get("minimum", 0))
					maximum = int(room_types[k].get("maximum", 0))
					if minimum > room_satisfaction[k]:
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
					modifiers[k] += 50 * (max(int(room_types[k].get("minimum", 0)), satisfaction) - satisfaction)
					modifiers[k] -= 1000 * (satisfaction - min(int(room_types[k].get("maximum", 2000)), satisfaction))
				return modifiers
			room_list = []
			room_types = dict()
			furniture = []
			parse_furniture_file(room_types, furniture)
			room_satisfaction = dict()
			for k in room_types.keys():
				room_satisfaction[k] = 0
			rooms = []
			print("Generating rooms...")
			while random.random() > .2 or not are_rooms_satisfied(room_satisfaction, room_types):
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
				furniture_in_room = []
				room_size = random.randint(75,125)
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
				rooms.append(Room(peak_modifier, furniture_in_room))
			return (rooms,room_types)
		def connect_rooms(rooms,room_types):
			def connect_1room(next_room):
				def has_available_connections(room):
					for v in room.connections.values():
						if v == None:
							return True
					else:
						return False 
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
				rooms.remove(next_room)
				nearby_room_types = []
				for k,v in room_types[next_room.theme].items():
					if k == "near":
						nearby_room_types = v
				adjacent_room = None
				adjacent_connection = None
				if nearby_room_types:
					possible_nearby_rooms = list(filter(has_available_connections, list(filter(lambda r: r.theme in nearby_room_types, self.rooms))))
					while possible_nearby_rooms:
						adjacent_room = possible_nearby_rooms[random.randint(0,len(possible_nearby_rooms)- 1)]
						connections = list(adjacent_room.connections.items())
						random.shuffle(connections)
						for k,v in connections:
							if v == None:
								adjacent_connection = k
								break
						else:
							continue
						break
					else:
						adjacent_rooms = list(filter(has_available_connections, self.rooms))
						adjacent_room = adjacent_rooms[random.randint(0,len(adjacent_rooms) - 1)]
						connections = list(adjacent_room.connections.items())
						random.shuffle(connections)
						for k,v in connections:
							if v == None:
								adjacent_connection = k
				else:
					adjacent_rooms = list(filter(has_available_connections, self.rooms))
					adjacent_room = adjacent_rooms[random.randint(0,len(adjacent_rooms) - 1)]
					connections = list(adjacent_room.connections.items())
					random.shuffle(connections)
					for k,v in connections:
						if v == None:
							adjacent_connection = k
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
			print("Connecting rooms...")
			current_room = Room("outside",[])
			del current_room.connections["up"]
			del current_room.connections["down"]
			keep = random.randint(0,3)
			count = 0
			keys_to_delete = []
			for k in current_room.connections.keys():
				if count != keep:
					keys_to_delete.append(k)
				count += 1
			for k in keys_to_delete:
				del current_room.connections[k]
			self.rooms.append(current_room)
			while rooms:
				next_room = rooms[random.randint(0,len(rooms) - 1)]
				connect_1room(next_room)

		def generate_characters():
			def parse_trait_file(stats, first_names, last_names, dialog):
				print("Reading character data from disk...")
				with open("trait_list.txt") as stat_file:
					for line in stat_file:
						if line == "\n":
							continue
						elif line[:-1] == "#|":
							for l in stat_file:
								if l[:-1] == "|#":
									break
							continue
						lines = line.split()
						if lines[0] == "##":
							continue
						elif lines[0] == "Stat":
							stat_type = lines[1]
							stats.append(stat_type)
						elif lines[0] == "Trait":
							pass
						elif lines[0] == "Name":
							if lines[1] == "First":
								for name_line in stat_file:
									if name_line == "\n":
										break
									first_names.append(name_line[:-1])
							elif lines[1] == "Last":
								for name_line in stat_file:
									if name_line == "\n":
										break
									last_names.append(name_line[:-1])
						else:
							## We've got some dialog to parse.
							dialog_type = []
							while(lines[0] != "->"):
								if (lines[0] == "\n"):
									break
								dialog_type.append(lines[0])
								if lines[0] not in dialog.keys():
									dialog[lines[0]] = []
								lines.pop(0)
							else:
								current_lines = []
								reading_attributes = False
								current_attributes = dict()
								#each line is a new dialog line or attribute for current lines
								for dialog_line in stat_file:
									if dialog_line == "\n":
										break
									elif dialog_line.split()[0] == ':':
										reading_attributes = True
										attribute_line = dialog_line.split()
										current_attributes[attribute_line[1]] = int(attribute_line[2])
									else:
										if reading_attributes == True:
											for d in current_lines:
												for t in dialog_type:
													dialog[t].append((d,current_attributes))
											reading_attributes = False
											current_lines = []
											current_attributes = dict()
										current_lines.append(dialog_line[:-1])
			def generate_character(stats, first_names, last_names):
				character_stats = dict()
				for stat in stats:
					character_stats[stat] = random.randint(0,9)
				return AI(character_stats, 
					first_names[random.randint(0,len(first_names) - 1)],
					last_names[random.randint(0,len(last_names) - 1)])
			def filter_dialog(character, dialog):
				def optimality(dialog_line):
					optimality = 0
					for k,v in dialog_line[1].items():
						for stat, value in character.attributes.items():
							if k == stat:
								optimality += math.fabs(v - value)
					return optimality
				for k,v in dialog.items():
					dialog_list = sorted(v, key=optimality)
					for i in range(len(dialog_list)):
						if optimality(dialog_list[i]) > 3:
							if not dialog_list[:i]:
								character.attributes["dialog"][k] = dialog_list[:1]
							else:
								character.attributes["dialog"][k] = dialog_list[:i]
							break
				return character
			stats = []
			dialog = dict()
			first_names = []
			last_names = []
			parse_trait_file(stats, first_names, last_names,dialog)
			number_of_characters = random.randint(len(self.rooms), 2 * len(self.rooms))
			print("Generating characters...")
			for i in range(number_of_characters):
				print(str(int(i/number_of_characters * 100)) + '%' + " complete.", end="\r")
				self.characters.append(filter_dialog(generate_character(stats, first_names, last_names),dialog))
			print("100"+'%'+" complete.")
		def populate_world():
			print("Populating the world...")
			for character in self.characters:
				room = self.rooms[random.randint(0,len(self.rooms) - 1)]
				room.people.append(character)
		connect_rooms(*generate_rooms())
		generate_characters()
		populate_world()
	# def update(self):
	# 	for char in self.characters:
	#		char.select_action(self)
		


def fold(function, base, l):
	for e in l:
		base = function(e,base)
	return base;

def add(a, b):
	return a + b

class Furniture:
	def __init__(self, name, attributes, actions):
		#String
		self.name = name
		#{String -> String or Integer}
		self.attributes = attributes
		#{String -> Action}
		self.actions = actions
	def __repr__(self):
		string = "\n" + self.name + ": \n"
		string = string + repr(self.modifiers) + "\n"
		string = string + repr(self.attributes) + "\n"
		string =  string + repr(self.actions)
		return string

class Action:
	def __init__(self, preconditions, effects, success, failure):
		# [Conditional]
		self.preconditions = preconditions
		# [Effect]
		self.effects = effects
		# String
		self.success = success
		# String
		self.failure = failure
	def attempt(self, character, target):
		if self.preconditions.eval(character,target):
			for effect in self.effects:
				effect.apply(character, target)
			print(self.success)
			return True
		print(self.failure)
		return False

class Conditional:
	def eval(self,character, furniture):
		pass

class OrCombinator(Conditional):
	def __init__(self,lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs
	def eval(self,character, furniture):
		rhs = False
		lhs = False
		try:
			rhs = self.rhs.eval(character, furniture)
		except AttributeError:
			rhs = False
		try:
			lhs = self.lhs.eval(character, furniture)
		except AttributeError:
			lhs = False
		return lhs or rhs

class AndCombinator(Conditional):
	def __init__(self,lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs
	def eval(self,character, furniture):
		rhs = True
		lhs = True
		try:
			rhs = self.rhs.eval(character, furniture)
		except AttributeError:
			rhs = True
		try:
			lhs = self.lhs.eval(character, furniture)
		except AttributeError:
			lhs = True
		return lhs and rhs

class Precondition:
	def __init__(self,target_entity, target_attribute, expected_value):
		self.entity = target_entity
		self.attribute = target_attribute
		self.expected_value = expected_value
	def eval(self,character, furniture):
		if self.entity == "user":
			return character.attributes[self.attribute] == self.expected_value
		else:
			return furniture.attributes[self.attribute] == self.expected_value

class Effect:
	def __init__(self,target_entity, target_attribute, value):
		self.entity = target_entity
		self.attribute = target_attribute
		self.value = value
	def apply(self,character, furniture):
		if self.entity == "user":
			character.attributes[self.attribute] = self.value
		else:
			furniture.attributes[self.attribute] = self.value

class IncrementorEffect(Effect):
	def apply(self,character, furniture):
		if self.entity == "user":
			character.attributes[self.attribute] += self.value
		else:
			furniture.attributes[self.attribute] += self.value

class DecrementorEffect(Effect):
	def apply(self,character, furniture):
		if self.entity == "user":
			character.attributes[self.attribute] -= self.value
		else:
			furniture.attributes[self.attribute] -= self.value

class Room:
	def __init__(self, theme, furniture):
		self.theme = theme
		self.furniture = furniture
		self.people = []
		self.connections = {"north":None, "south":None, "east":None, "west":None, "up":None, "down":None}
	def __repr__(self):
		return "\n" + repr(self.theme) + "\n" + repr(self.furniture)

class Character:
	def __init__(self):
		self.attributes = dict()
		self.attributes["energy_per_turn"] = 0
		self.attributes["seat"] = "None"

class AI(Character):
	def __init__(self, stats, first_name, last_name):
		super(AI, self).__init__()
		self.attributes["first_name"] = first_name 
		self.attributes["last_name"] = last_name
		self.attributes = dict(list(self.attributes.items()) + list(stats.items()))
		self.attributes["room"] = None
		self.attributes["dialog"] = dict()
	def __repr__(self):
		pass
		#return repr(self.first_name) + " " + repr(self.last_name) + "\n" + repr(self.stats) + "\n" + repr(self.dialog) + "\n"
	def get_dialog(self,phrase):
		return self.attributes["dialog"][phrase][random.randint(0,len(self.attributes["dialog"][phrase]) - 1)][0]

class Player(Character):
	def __init__(self,world):
		super(Player, self).__init__()
		self.attributes["room"] = world.rooms[0]
		self.attributes["is_Alive"] = True

"""
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
"""

        





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
while player.attributes["is_Alive"]:
	print("The room you are in looks like a " + player.attributes["room"].theme + "\n")
	#if player.attributes["energy_per_turn"] != 0:
	print("You are gaining " + str(player.attributes["energy_per_turn"]) + " energy per turn.")
	print("\n")
	for furniture in player.attributes["room"].furniture:
		print("There is a " + furniture.name + " in the room.\n")
	for character in player.attributes["room"].people:
		print(character.attributes["first_name"] + " " + character.attributes["last_name"] + " is in the room.\n")
	for k,v in player.attributes["room"].connections.items():
		if v == None:
			continue
		else:
			print("A " + v.theme + " is to the " + k + ".\n")
	action_accepted = False
	while not action_accepted:
		action = input("-->")
		action_words = action.split()
		for furniture in player.attributes["room"].furniture:
			if action_words[-1] == furniture.name:
				act = functools.reduce(lambda x, y: x + y, action_words[:-1])
				try:
					action_accepted = furniture.actions[act].attempt(player, furniture)
				except KeyError:
					print(furniture.name + " has no command " + functools.reduce(lambda x, y: x + y, action_words[:-1], ""))
				break
		else:
			if len(action_words) == 4:
				if action_words[0] == "talk":
					if action_words[1] == "to":
						for character in player.attributes["room"].people:
							if action_words[2] == character.attributes["first_name"] and action_words[3] == character.attributes["last_name"]:
								print(character.get_dialog("Greeting") + "\n")
								break
						else:
							print("You talk at " + action_words[2] + ", but it's incapable of hearing.")
					else:
						print("You talk at nobody, and nobody is listening.")
			elif len(action_words) == 3:
				if action_words[0] == "go" or action_words[0] == "move":
					if player.attributes["seat"] != "None":
						print("You're sitting down! get_up first!")
						continue
					if(action_words[1] == "to"):
						for k,v in player.attributes["room"].connections.items():
							if v != None and action_words[2] == v.theme:
								player.room = v;
								action_accepted = True
								break
						else:
							print("You don't know how to get to the " + action_words[2])
					else:
						print("Movement commands require a target.")
				else:
					print("I don't understand you.")
			elif len(action_words) == 2:
				if action_words[0] == "kill" and action_words[1] == "me":
					player.attributes["is_Alive"] = False
					action_accepted = True
				elif action_words[0] == "go" or action_words[0] == "move":
					if player.attributes["seat"] != "None":
						print("You're sitting down! get_up first!")
						continue
					for k,v in player.attributes["room"].connections.items():
						if action_words[1] == k and v != None:
							player.attributes["room"] = v;
							action_accepted = True
							break
					else:
						print("There isn't anything to the " + action_words[1])
				else:
					print("I don't understand you.")
			else:
				print("I don't understand you.")
else:
	print("You are dead.")

# print("Hello World")
# world = World()
# while(True):
#	world.update()
