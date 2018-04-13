import sys
from math import log

# get name of files from argument
training_file = sys.argv[1]
test_file = sys.argv[2]
result_file = sys.argv[3]

# parsing file to attribute list, data list
# attribute_list : {'attribute name' : 'attribute value'}
# data : [data]
def parse_file_to_attribute_list (filename) :
	# read file and parsing it to data
	with open(filename) as file :
		attributes = file.readline().split()
		data = file.read().split()
		data = [data[i : i + len(attributes)] for i in range(0, len(data), len(attributes))]

	# generate attribute dictionary
	attribute_list = {}
	for i in attributes :
		attribute_list[i] = []

	# get attribute list
	for i in data :
		for j in range(len(attributes)) :
			if i[j] not in attribute_list[attributes[j]] :
				attribute_list[attributes[j]].append(i[j])

	return attribute_list, data

# generate decision tree
def generate_decision_tree (attribute_list, data_set) :
	tree = [[[{}, [], data_set]]] # [tree [level [node]]]
								# node : {label}, [child label of class], [data list]

	# make data homogeneous by splitting
	level = 0
	while True :
		count = 0
		new_level_nodes = [] # [level [node]]
		for i in tree[level] :
			label = get_label(i[0], i[2], attribute_list, tree)

			if label == None : # no more label or homogenous
				count = count + 1
				continue

			i[1].append(label)
			new_level_nodes.extend(split_data(i[0], label, attribute_list[label], list(attribute_list.keys()).index(label), i[2]))
		tree.append(list(new_level_nodes))
		if count == len(tree[level]) :
			break
		level = level + 1


	# if tree node has no data -> remove
	# if tree node homogenous -> child label location = class
	reduced_tree = tree.copy()
	tree.reverse()

	index = len(tree) - 1
	for i in tree :
		position = 0
		for j in i :
			if len(j[1]) <= 0 : # if child node
				majority_class = get_majority(j[2], list(attribute_list.values())[-1])
				if majority_class == None : # no data
					print("no data", j[0])
				#	parent_idx, parent_pos = get_parent_index(j[0], reduced_tree)
				#	reduced_tree[parent_idx][parent_pos][1] = get_majority(reduced_tree[parent_idx][parent_pos][2], list(attribute_list.values())[-1])
					reduced_tree[index].remove(j)
					continue
				reduced_tree[index][position][1].append(majority_class)
			position = position + 1
		index = index - 1
	return reduced_tree

def get_label (used_label, data_set, attribute_list, tree) :
	label_candidate = list(set(list(attribute_list.keys())[:-1])-set(used_label))

	# list for saving gini values
	gini = {}
	gini_compare = []
	for i in label_candidate :
		gini[i] = 0
		gini_compare.append(0)

	# no more usable label, return None
	if len(list(gini.keys())) <= 0 :
		return None

	gain = gini.copy()
	gain_ratio = gain.copy()

	# calculate gini each labels
	gini_val = get_gini(list(attribute_list.keys())[-1], list(attribute_list.values())[-1], data_set)
	info_val = get_info(list(attribute_list.keys())[-1], list(attribute_list.values())[-1], data_set)

	for i in label_candidate :
		# append data by attribute by i (label)
		data_set_by_label_attribute = [[] for _ in attribute_list[i]]
		gini[i] = get_gini_impurity(gini_val, i, attribute_list[i], list(attribute_list.keys()).index(i), list(attribute_list.keys())[-1], list(attribute_list.values())[-1], data_set)
		gain[i] = get_gain(info_val, i, attribute_list[i], list(attribute_list.keys()).index(i), list(attribute_list.keys())[-1], list(attribute_list.values())[-1], data_set)
		splitted = get_splitted_info(i, attribute_list[i], list(attribute_list.keys()).index(i), data_set)
		if splitted != 0 :
			gain_ratio[i] = gain[i] / splitted
		else :
			gain_ratio[i] = gain[i]

	# find homogenous or return max label by gain ratio
	if max(gain_ratio.values()) == 1 :
		return None
	elif list(gain_ratio.values()) == gini_compare :
		return None
	else :
		new_label = label_candidate[list(gain_ratio.values()).index(max(list(gain_ratio.values())))]
		return new_label
	"""
	# find homogenous or return max label by gini
	if max(gini.values()) == 1 :
		return None
		#pass
	elif list(gini.values()) == gini_compare :
		return None
		#pass
	else :
		new_label = label_candidate[list(gini.values()).index(max(list(gini.values())))]
		return new_label
	"""



def get_info (class_label, class_attribute, data_set) :
	# count by class attribute
	count = [0 for _ in class_attribute]
	for i in data_set :
		count[class_attribute.index(i[-1])] += 1

	# if no data, return None
	total = len(data_set)
	if total <= 0 :
		return 0

	# calculate info
	info = 0
	for i in count :
		if i != 0 :
			info -= ((i/total)*log(i/total, 2))
	return info

def get_average_info (label, label_attribute, label_index, class_label, class_attribute, data_set) :
	count_by_label_attribute = [0 for _ in label_attribute]
	data_set_by_label_attribute = [[] for _ in label_attribute]

	# count data by label attribute
	for i in data_set :
		count_by_label_attribute[label_attribute.index(i[label_index])] += 1
		data_set_by_label_attribute[label_attribute.index(i[label_index])].append(i)

	if sum(count_by_label_attribute) <= 0 : # no data
		return 0

	info_avg = 0
	index = 0
	for i in count_by_label_attribute :
		info_avg += (i/sum(count_by_label_attribute) * get_info(class_label, class_attribute, data_set_by_label_attribute[index]))
		index = index + 1

	return info_avg

def get_gain (info, label, label_attribute, label_index, class_label, class_attribute, data_set) :
	return info - get_average_info(label, label_attribute, label_index, class_label, class_attribute, data_set)

def get_splitted_info (label, label_attribute, label_index, data_set) :
	count_by_label_attribute = [0 for _ in label_attribute]

	# count data by label attribute
	for i in data_set :
		count_by_label_attribute[label_attribute.index(i[label_index])] += 1

	# if no data, return None
	total = len(data_set)
	if total <= 0 :
		return 0

	# calculate info
	info = 0
	for i in count_by_label_attribute :
		if i != 0 :
			info -= ((i/total)*log(i/total, 2))
	return info

def get_gini (class_label, class_attribute, data_set) :
	# count by class attribute
	count = [0 for _ in class_attribute]
	for i in data_set :
		count[class_attribute.index(i[-1])] += 1

	# if no data, return None
	total = len(data_set)
	if total <= 0 :
		return 0

	# calculate gini
	gini = 0
	for i in count :
		gini -= ((i/total) * (i/total))

	return gini

def get_average_gini (label, label_attribute, label_index, class_label, class_attribute, data_set) :
	count_by_label_attribute = [0 for _ in label_attribute]
	data_set_by_label_attribute = [[] for _ in label_attribute]
	# count data by label attribute
	for i in data_set :
		count_by_label_attribute[label_attribute.index(i[label_index])] += 1
		data_set_by_label_attribute[label_attribute.index(i[label_index])].append(i)

	if sum(count_by_label_attribute) <= 0 : # no data
		return 0

	gini_avg = 0
	index = 0
	for i in count_by_label_attribute :
		gini_avg += (i/sum(count_by_label_attribute)) * get_gini(class_label, class_attribute, data_set_by_label_attribute[index])
		index = index + 1

	return gini_avg


def get_gini_impurity (gini, label, label_attribute, label_index, class_label, class_attribute, data_set) :
	return gini - get_average_gini(label, label_attribute, label_index, class_label, class_attribute, data_set)

def split_data (parent_label, new_label, new_label_attributes, new_label_index, data_set) :
	new_level_nodes = [[{}, [], []] for _ in new_label_attributes]

	# append label
	index = 0
	for i in new_level_nodes :
		i[0][new_label] = new_label_attributes[index]
		i[0].update(parent_label)
		index = index + 1

	# append data
	for i in data_set :
		new_level_nodes[new_label_attributes.index(i[new_label_index])][2].append(i)

	return new_level_nodes

# if leaf node get class by majority
def get_majority (data_set, class_attribute) :
	count = [0 for _ in class_attribute]
	origin_count = count.copy()

	for i in data_set :
		count[class_attribute.index(i[-1])] += 1

	if count == origin_count : # no data
		return None

	max_count = 0
	for i in count :
		if i == max(count) :
			max_count = max_count + 1

	# 만약 개수가 같은 항목이 있다면 부모에게서 같은 개수의 항목 중 어떤 것이 많은지 확인

	return class_attribute[count.index(max(count))]

def get_parent (label, tree) :
	label_copy = label.copy()
	del label_copy[list(label_copy.keys())[0]]

	for i in tree :
		for j in i :
			if j[0] == label:
				return j

	return get_parent(label_copy, tree)

def get_parent_index (label, tree) :
	label_copy = label.copy()
	del label_copy[list(label_copy.keys())[0]]

	index = 0
	position = 0
	for i in tree :
		position = 0
		for j in i :
			if j[0] == label:
				return index, position
			position = position + 1
		index = index + 1

	return get_parent_index(tree, label_copy)

def get_class (data, attribute_list, tree) :
	# initial search settings
	label = {}

	# tree search
	for i in tree : # each level in tree
		for j in i : # each node in level
			if label.items() <= j[0].items() : # if all label in current node label
				if len(j[1]) <= 0 : # no next label
					parent_label = label.copy()
					current_class = None
					while current_class == None :
						parent = get_parent(parent_label, tree)
						current_class = get_majority(parent[2], list(attribute_list.values())[-1])
						parent_label = parent[0]
					return current_class
					#return get_majority(j[2], list(attribute_list.values())[-1])
				elif j[1][0] in list(attribute_list.values())[-1] : # if child label == class (leaf node)
					return j[1][0]
				else : # get next level
					label = {}
					label[j[1][0]] = data[list(attribute_list.keys()).index(j[1][0])]
					label.update(j[0])
					break

	parent_label = label.copy()
	current_class = None
	while current_class == None :
		print(parent_label)
		parent = get_parent(parent_label, tree)
		current_class = get_majority(parent[2], list(attribute_list.values())[-1])
		parent_label = parent[0]
	return current_class


attribute_list, data = parse_file_to_attribute_list(training_file)
test_attribute_list, test_data = parse_file_to_attribute_list(test_file)
decision_tree = generate_decision_tree(attribute_list, data)

print("tree :")
for i in decision_tree :
	for j in i :
		print(str(j[0]), str(j[1]), len(j[2]))
	print("\n\n")

with open(result_file, "w") as result :
	attributes = list(attribute_list.keys())
	for i in attributes :
		if attributes.index(i) != len(attributes) - 1 :
			result.write("{}\t".format(i))
		else :
			result.write("{}\n".format(i))

	for i in test_data :
		for j in i :
			result.write("{}\t".format(j))
		result.write("{}\n".format(get_class(i, attribute_list, decision_tree)))
