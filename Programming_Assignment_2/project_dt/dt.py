# get minimum support, input file name, output file name
import sys
from math import log
training_file = sys.argv[1]
test_file = sys.argv[2]
result_file = sys.argv[3]

minimum_data = 0

def parse_file_to_attribute_list (filename) :
    # read file and parsing it to data.
    with open(filename) as input_file :
        attributes = input_file.readline()
        attributes = attributes.split()
        data = input_file.read().split()
        data = [data[i: i + len(attributes)] for i in range(0, len(data), len(attributes))]

    attribute_list = {}
    for i in attributes:
        attribute_list[i] = []
    
    for i in data :
        for j in range(len(attributes)) :
            if i[j] not in attribute_list[attributes[j]] :
                attribute_list[attributes[j]].append(i[j])
    return attributes, attribute_list, data

def generate_decision_tree (attribute_list, data_set, attributes) :
    tree = [[[{}, [], data_set]]]

    level = 0
    while True :
        count = 0
        new_level_nodes = []
        for i in tree[level] :
            label = get_label_for_splitting(i, attribute_list, attributes, i[0])

            if label == None :
                continue
            
            if label == "homo" :
                count = count + 1
                continue

            # 데이터 나누는 과정 필요
            i[1].append(label)
            new_level_nodes.extend(split_database(i[2], label, attribute_list, attributes, i[0]))

        tree.append(list(new_level_nodes))
        if label == None or count == len(tree[level]) :
            break
        level = level + 1

    reduced_tree = tree.copy()
    index = 0
    for i in tree :
        position = 0
        for j in i :
            if len(j[1]) <= 0 : #if child node
                frequent_class = get_frequent(j[2], attribute_list, attributes)
                if frequent_class == None :
                    reduced_tree[index].remove(j)
                    continue
                reduced_tree[index][position][1].append(frequent_class)
            position = position + 1
        index = index + 1

    return reduced_tree

def get_frequent (data_list, attribute_list, attributes) :
    position = len(attributes) - 1
    label = attributes[len(attributes) - 1]

    count = [0 for _ in attribute_list[label]]
    count_copy = count.copy()
    for i in data_list :
        count[attribute_list[label].index(i[position])] += 1

    if (count == count_copy) :
        return None
    else :
        return attribute_list[label][count.index(max(count))]

def split_database (data_list, label, attributes_list, attributes, parent_attributes) :
    new_level = [[{}, [], []] for _ in attribute_list[label]]
    for i in attributes_list[label] :
        new_level[attributes_list[label].index(i)][0][label] = i
    for i in data_list :
        new_level[attributes_list[label].index(i[attributes.index(label)])][2].append(i)
    for i in new_level :
        i[0].update(parent_attributes)
    return new_level

def get_label_for_splitting (internal_node, attribute_list, attributes, used_label) :

    information_gain = [0 for _ in attribute_list]

    # attribute list dictionary key access
    if len(list(attribute_list.keys())) <= 1 :
        return None

    for i in set(list(attribute_list.keys())[: -1])-set(used_label) :
        # attribute list dictionary attribute value list access by key
        for j in attribute_list[i] :
            # generate attribute value list element counting list
            attribute_element_data = [[] for _ in attribute_list[i]]
            # access data set in internal node and counting each attribute value
            internal_data = []
            for m in internal_node[2] :
                attribute_element_data[attribute_list[i].index(m[attributes.index(i)])].append(m)
                internal_data.append(m)
            information_gain[attributes.index(i)] = get_info_gain(attributes, attribute_list, attribute_element_data, i, get_total_info(attributes, attribute_list, internal_data))

    if max(information_gain) == 0 :
        return "homo"
    max_label = attributes[information_gain.index(max(information_gain))]
    return max_label

def get_total_info (attributes, attribute_list, data) :
    attribute_element_cnt = [0 for _ in attribute_list[attributes[len(attributes) - 1]]]
    for i in data :
        attribute_element_cnt[attribute_list[attributes[len(attributes) - 1]].index(i[len(attributes) - 1])] += 1

    return get_info(attribute_element_cnt)

def get_info_gain (attributes, attribute_list, data_by_attribute, label, total_info) :
    attribute_element_cnt = [[0 for _ in attribute_list[attributes[len(attributes) - 1]]] for __ in attribute_list[label]]
    for i in data_by_attribute :
        for j in i :
            attribute_element_cnt[attribute_list[label].index(j[attributes.index(label)])][attribute_list[attributes[len(attributes) - 1]].index(j[len(attributes) - 1])] += 1

    info = 0
    total = 0
    for i in data_by_attribute :
        total += len(i)
    if total == 0 :
        return -1
    for i in attribute_element_cnt :
        info += sum(i)/total * get_info(i)
    return total_info - info

def get_info (pi) :
    info = 0
    total = sum(pi)
    if total == 0 :
        return -1
    for i in pi :
        if i / total != 0 :
            info -= (i/total * log(i/total, 2))
    return info

def get_data_class (attributes, attribute_list, tree, data) :
    label = {}
    child_label = tree[0][0][1][0]

    if child_label not in attribute_list : #if leaf node
        return child_label
    value = data[attributes.index(child_label)]
    level = 0

    for i in tree : #each level in tree
        level = level + 1
        index = 0
        for j in i : #each node in level
            index = index + 1
            if label.items() <= j[0].items() :
                if child_label in j[0].keys() :
                    if value != None and value == j[0][child_label] :
                        if len(j[1]) <= 0 :
                            return get_frequent(j[2], attribute_list, attributes)
                        label = j[0]
                        next_label = check_existing_in_next_level(tree, label, level - 1, j[1])
                        if next_label == None :
                            print(label, get_class(label, tree, attributes, attribute_list))
                            return get_class(label, tree, attributes, attribute_list)
                        else :
                            child_label = next_label



                        #if child_label not in attribute_list :
                        #    return child_label
                        value = data[attributes.index(child_label)]
                        break

    return get_class(label, tree, attributes, attribute_list)

def check_existing_in_next_level(tree, label, current, next_label) :
    for i in tree :
        if current != 0 :
            current = current - 1
            continue
        for j in i :
            if label.items() <= j[0].items() :
                for k in next_label :
                    if k in j[0].keys() :
                        return k
    return None


def get_class(label, tree, attributes, attribute_list) :
    for i in tree :
        for j in i :
            if len(list(j[0].keys())) >= 0 :
                if label == j[0] :
                    frequent = get_frequent(j[2], attribute_list, attributes)
                    if frequent != None :
                        return frequent
            else :
                if frequent != None:
                    return frequent
    label_copy = label.copy()
    del label_copy[list(label_copy.keys())[0]]
    return get_class(label_copy, tree, attributes, attribute_list)

def branch(tree, min_data, attributes, attribute_list) :

    reduced_tree = tree.copy()
    reversed_tree = tree.copy()
    reversed_tree.reverse()
    index = len(tree)
    #parent = None
    for i in reversed_tree :
        index = index - 1
        for j in i :
            if len(j[2]) < min_data :
                reduced_tree[index].remove(j)
                parent = get_parent(tree, j[0])
                parent[1].append(get_class(parent[0], tree, attributes, attribute_list))
            #parent = j

    return reduced_tree

def get_parent(tree, label) :
    for i in tree :
        for j in i :
            if j[0] == label :
                return j

    label_copy = label.copy()
    del label_copy[list(label_copy.keys())[0]]
    return get_parent(tree, label_copy)

attributes, attribute_list, data = parse_file_to_attribute_list(training_file)

for i in attribute_list.keys() :
    sorted(attribute_list[i])

tree = generate_decision_tree (attribute_list, data, attributes)
tree = branch(tree, minimum_data, attributes, attribute_list)
t_attributes, t_attribute_list, t_data = parse_file_to_attribute_list(test_file)

"""
for i in tree :
    for j in i :
        print(str(j))
    print("\n\n")
"""

for i in tree :
    for j in i :
        print(str(j[0]), len(j[2]))
        #print("data : ", str(j[2]), "\n")
    print("\n\n")

with open(result_file, "w") as result :
    for i in attributes :
        if attributes.index(i) != len(attributes) - 1 :
            result.write("{}\t".format(i))
        else :
            result.write("{}\n".format(i))

    for i in t_data :
        for j in i :
            result.write("{}\t".format(j))
        result.write("{}\n".format(get_data_class(attributes, attribute_list, tree, i)))
