# get minimum support, input file name, output file name
import sys
from math import log
training_file = sys.argv[1]
test_file = sys.argv[2]
result_file = sys.argv[3]

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

def write_file_with_decision_tree (attributes, data, filename) :
    with open(filename, "w") as output_file :
        for i in attributes :
            output_file.write("{} ", i)
        output_file.write("\n")

        for i in data :
            for j in i :
                output_file.write("{} ", j)
            output_file.write("\n")

def generate_decision_tree (attribute_list, data_set, attributes) :
    tree = [[[{}, [], data_set]]]
    used_labels = []

    while True :
        level = len(tree) - 1
        new_level_node = []
        count = 0
        for i in tree[level] :
            label = get_label_for_splitting (i, attribute_list, attributes, used_labels)
            if label == None :
                break

            if label == "homo" :
                count = count + 1
                continue

            # 데이터 나누는 과정 필요
            i[1].append(label)
            tree.append(split_database(i[2], label, attribute_list, attributes))
            used_labels.append(label)

        if label == None or count == len(tree[level]):
            break

    for i in tree :
        for j in i :
            if len(j[1]) <= 0 : #if child node
                j[1].append(get_frequent (j[2], attribute_list, attributes))

    return tree

def get_frequent (data_list, attribute_list, attributes) :
    position = len(attributes) - 1
    label = attributes[len(attributes) - 1]

    count = [0 for _ in attribute_list[label]]
    for i in data_list :
        count[attribute_list[label].index(i[position])] += 1
    return attribute_list[label][count.index(max(count))]

def split_database (data_list, label, attributes_list, attributes) :
    new_level = [[{}, [], []] for _ in attribute_list[label]]
    for i in attributes_list[label] :
        new_level[attributes_list[label].index(i)][0][label] = i
    for i in data_list :
        new_level[attributes_list[label].index(i[attributes.index(label)])][2].append(i)
    return new_level

def get_label_for_splitting (internal_node, attribute_list, attributes, used_label) :

    information_gain = [0 for _ in attribute_list]

    # attribute list dictionary key access
    if len(list(attribute_list.keys())) <= 1 :
        return None

    for i in set(list(attribute_list.keys())[: -1])-set(used_label) :
        #print(i)
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
    #information_gain = get_info_gain(information_gain[: len(information_gain) - 1], information_gain[len(information_gain) - 1])

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

def get_data_class (attributes, attributes_list, tree, data) :
    print("new", data)

    label = None
    value = None
    for i in tree : #each level nodes
        for j in i : # each nodes
            print("each node in same level :", str(j))

            if label == None :
                label = j[1][0]
                if label not in attributes:
                    return label
                print("None", label)
                value = data[attributes.index(label)]
                continue

            if label not in attributes :
                return label

            #print(str(j))
            if label in j[0].keys() :
                if j[0][label] == value :
                    label = j[1][0]
                    print(label)

                    if label not in attributes:
                        return label
                    value = data[attributes.index(label)]
                    break

            #elif j[0] == label


attributes, attribute_list, data = parse_file_to_attribute_list(training_file)
tree = generate_decision_tree (attribute_list, data, attributes)

t_attributes, t_attribute_list, t_data = parse_file_to_attribute_list(test_file)
"""
for i in tree :
    print(str(i))
"""
with open(result_file, "w") as result :

    for i in attributes :
        result.write("{}\t".format(i))
    result.write("\n")

    for i in t_data :
        for j in i :
            result.write("{}\t".format(j))
        result.write("{}\n".format(get_data_class(attributes, attribute_list, tree, i)))
