#get minimum support, input file name, output file name
import sys
import itertools
import decimal
import math
minimun_support = float(sys.argv[1])
input_filename = sys.argv[2]
output_filename = sys.argv[3]

#read input.txt file and parsing it to data.
with open(input_filename) as input_file :
	input_data = input_file.readlines()

input_file.close()

transactions = [] # to store transaction list and items in transaction
total_transaction = 0 # for getting number of transactions
for i in input_data :
	temp = i.split()
	temp = list(map(int, temp))
	transactions.append(temp)
	total_transaction = total_transaction + 1

def RoundAtSecondPoint(num) :
	math.ceil(num, 4)
	

# get support of item_set
def GetSupport(item_set, tranx):
	count = 0  # for check how many times in transaction
	item_set = set(item_set)
	for i in tranx:
		if item_set.issubset(set(i)):
			count = count + 1

	return round(decimal.Decimal((count / total_transaction) * 100), 2)

# get confidence of item_set
def GetConfidence(item_set_x, item_set_y, tranx):
	count = 0
	total_count = 0
	item_set_x = set(item_set_x)
	item_set_y = set(item_set_y)
	#print("Get  Confidence :", item_set_x, item_set_y)
	for i in tranx:
		#print(item_set_x, i)
		if item_set_x.issubset(i) :
			total_count = total_count + 1
			if item_set_y.issubset(i) :
				count = count + 1
	if total_count == 0 :
		print("no item set")
		return 0
	return round(decimal.Decimal((count / total_count) * 100), 2)
	#return count / total_count * 100

def GetSubset(item_set) : # get length k-1 subset
	if len(item_set) <= 1 :
		print("size of item set is less than one")
		return None

	subset = []
	for i in item_set :
		tmp = []
		tmp.append(i)
		subset.append(item_set - set(tmp))

	return subset

def RemoveDuplicated(list) :
	removed_list = []
	for i in list :
		if i not in removed_list :
			removed_list.append(i)
	return removed_list

def GenerateAprioriCandidate(previous_candidate, current_length) : # current length : previous item set C(k-1)'s length
	new_candidate = []

	for i in previous_candidate :
		for j in previous_candidate :
			new_candidate.append(list(set().union(i, j)))
	candidate = list(map(set, new_candidate))
	candidate = RemoveDuplicated(candidate)

	filtered_candidate = []
	for i in candidate :
		if len(i) == (current_length + 1) :
			filtered_candidate.append(i)
	candidate = filtered_candidate

	for i in candidate :
		subset = GetSubset(i)
		if (len(subset) != 0) or (subset is not None) :
			for j in subset :
				if j not in previous_candidate :
					candidate.remove(i)
					break
	return candidate

def GetAprioriCandidate(previous_candidate, current_length, min_support, tranx) :
	candidate = GenerateAprioriCandidate(previous_candidate, current_length)
	filtered_candidate = []
	for i in candidate :
		if GetSupport(i, tranx) >= min_support :
			filtered_candidate.append(i)
	candidate = filtered_candidate
	candidate.sort()
	return  candidate

def GetOneItemSet(tranx, min_support) :
	candidate = []
	for i in tranx :
		for j in i :
			if not j in candidate :
				candidate.append(j)
	candidate.sort()

	candidate_list = []
	for i in candidate :
		tmp = []
		tmp.append(i)
		tmp = set(tmp)
		candidate_list.append(tmp)

	candidate = []
	for i in candidate_list :
		if GetSupport(i, tranx) >= min_support :
			candidate.append(i)
	return candidate

def GenerateApriori(tranx, min_support) :
	item_set = {}
	current_length = 1
	patterns = []
	item_set[current_length] = GetOneItemSet(tranx, min_support)

	while True :
		if (not current_length in item_set) or (len(item_set[current_length]) == 0) :
			print ("no more item set")
			break

		item_set[current_length + 1] = GetAprioriCandidate(item_set[current_length], current_length, min_support, tranx)
		for i in item_set[current_length] :
			subset = []
			for j in range(current_length) :
				subset += list(itertools.combinations(i, j))

			#print(i, current_length, "subset :", list(subset))
			for j in subset :
				difference = set(i) - set(j)
				if (len(difference) < 1) or (len(j) < 1) :
					#print(difference, i, j, "continue")
					continue

				#print(i, j, difference)
				tmp1 = [set(j), difference, GetSupport(i, tranx), GetConfidence(j, difference, tranx)]
				#tmp2 = [difference, set(j), GetSupport(i, tranx), GetConfidence(difference, j, tranx)]
				patterns.append(tmp1)
				#atterns.append(tmp2)

		current_length += 1

	return patterns, item_set, current_length

def sendToOutputFile(association_list, output_file) :
	output_file.write(item_list_to_str(association_list[0]))
	output_file.write("\t")
	output_file.write(item_list_to_str(association_list[1]))
	output_file.write("\t")
	output_file.write(str(association_list[2]))
	output_file.write("\t")
	output_file.write(str(association_list[3]))
	output_file.write("\n")


def item_list_to_str(item_list) :
	count = 0
	string = "{"
	item_list = list(item_list)
	item_list.sort()
	for i in item_list :
		if count != 0 and count != len(item_list):
			string += ","
		string += str(i)
		count += 1
	string += "}"
	return string

association_list, item_set, length = GenerateApriori(transactions, minimun_support)
with open(output_filename, "w") as output_file :
	for i in association_list :
		sendToOutputFile(i, output_file)