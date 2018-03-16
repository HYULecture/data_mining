# get minimum support, input file name, output file name
import sys
import itertools
minimun_support = float(sys.argv[1])
input_filename = sys.argv[2]
output_filename = sys.argv[3]

# read input.txt file and parsing it to data.
with open(input_filename) as input_file :
	input_data = input_file.readlines()

input_file.close()

# for rounding at second point exactly
def RoundAtSecondPoint(num) :
	number_string = str(num)
	floating_point = number_string.split(".")
	if len(floating_point[1]) > 2 :
		# in python, 5 is sometimes not ceiled.
		if int(floating_point[1][2]) == 5 :
			num += 0.001
		return round(num, 2)
	else :
		return num

# get support of item_set
def GetSupport(item_set, tranx, total):
	count = 0  # for check how many times in transaction
	item_set = set(item_set)
	for i in tranx:
		if item_set.issubset(set(i)):
			count = count + 1

	return RoundAtSecondPoint((count / total) * 100)

# get confidence of item_set
def GetConfidence(item_set_x, item_set_y, tranx):
	count = 0
	total_count = 0
	item_set_x = set(item_set_x)
	item_set_y = set(item_set_y)

	# if item_set_x is in transaction, increase total count and check item_set_y is also in transaction
	# if so, increase count ]
	for i in tranx:
		if item_set_x.issubset(i) :
			total_count = total_count + 1
			if item_set_y.issubset(i) :
				count = count + 1

	# check whether devied 0, and return rounded number or 0
	if total_count == 0 :
		print("no item set")
		return 0
	return RoundAtSecondPoint((count / total_count) * 100)

# for removing duplicated element of list
def RemoveDuplicated(list) :

	# if find not duplicated element, add to removed list
	removed_list = []
	for i in list :
		if i not in removed_list :
			removed_list.append(i)
	return removed_list

# for generating candidates of apriori algorithm
def GenerateAprioriCandidate(previous_candidate, current_length) : # current length : previous item set C(k-1)'s length
	new_candidate = []

	# union two previous candidate with minimum support and remove duplicated
	for i in previous_candidate :
		for j in previous_candidate :
			new = list(set().union(i, j))
			new_candidate.append(new)
	candidate = list(map(set, new_candidate))
	candidate = RemoveDuplicated(candidate)

	# maintain only candidate with k length
	filtered_candidate = []
	for i in candidate :
		if len(i) == (current_length + 1) :
			filtered_candidate.append(i)
	candidate = filtered_candidate

	return candidate

# filter candidates with minimum support
def GetAprioriCandidate(previous_candidate, current_length, min_support, tranx, total) :
	candidate = GenerateAprioriCandidate(previous_candidate, current_length)
	filtered_candidate = []
	for i in candidate :
		if GetSupport(i, tranx, total) >= min_support :
			filtered_candidate.append(i)
	candidate = filtered_candidate
	candidate.sort()
	return  candidate

# for getting item set with length 1
def GetOneItemSet(tranx, min_support, total) :
	# get variable item in transaction
	candidate = []
	for i in tranx :
		for j in i :
			if not j in candidate :
				candidate.append(j)
	candidate.sort()

	# change element to set
	candidate_list = []
	for i in candidate :
		tmp = []
		tmp.append(i)
		tmp = set(tmp)
		candidate_list.append(tmp)

	# filter candidates with minimum support
	candidate = []
	for i in candidate_list :
		if GetSupport(i, tranx, total) >= min_support :
			candidate.append(i)
	return candidate

# apriori master algorithm
def GenerateApriori(tranx, min_support, total) :

	# set current length 1 and create item set with length 1
	item_set = {}
	current_length = 1
	patterns = []
	item_set[current_length] = GetOneItemSet(tranx, min_support, total)

	# repeat creating candidates until no candidates generated.
	while True :

		# if no candidates generated, terminate function
		if (not current_length in item_set) or (len(item_set[current_length]) == 0) :
			print ("no more item set")
			break

		# generate candidate with kth length
		item_set[current_length + 1] = GetAprioriCandidate(item_set[current_length], current_length, min_support, tranx, total)

		# generate subsets and get support and confidence
		for i in item_set[current_length] :
			subset = []
			for j in range(current_length) :
				subset += list(itertools.combinations(i, j))

			for j in subset :
				difference = set(i) - set(j)
				if (len(difference) < 1) or (len(j) < 1) :
					continue

				tmp1 = [set(j), difference, GetSupport(i, tranx, total), GetConfidence(j, difference, tranx)]
				patterns.append(tmp1)

		current_length += 1

	return patterns, item_set, current_length

# send fixed candidates to output file with output format
def sendToOutputFile(association_list, output_file) :
	output_file.write(item_list_to_str(association_list[0]))
	output_file.write("\t")
	output_file.write(item_list_to_str(association_list[1]))
	output_file.write("\t")
	output_file.write(str(association_list[2]))
	output_file.write("\t")
	output_file.write(str(association_list[3]))
	output_file.write("\n")

# change item set list to string with output format in sorted form
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

# change total transaction to transaction list
transactions = [] # to store transaction list and items in transaction
total_transaction = 0 # for getting number of transactions
for i in input_data :
	temp = i.split()
	temp = list(map(int, temp))
	transactions.append(temp)
	total_transaction = total_transaction + 1

# apriori algorithm result to file
association_list, item_set, length = GenerateApriori(transactions, minimun_support, total_transaction)
with open(output_filename, "w") as output_file :
	for i in association_list :
		sendToOutputFile(i, output_file)