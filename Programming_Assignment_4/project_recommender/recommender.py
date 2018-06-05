import sys
import collections

base_file = sys.argv[1]
test_file = sys.argv[2] #[user_id]\t[item_id]\t[rating]\t[time_stamp]\n
output_file = "../u"+base_file[-6]+".base_prediction.txt" #[user_id]\t[item_id]\t[rating]\n

neighbor_number = 15

with open(base_file) as base :
    data_set = base.read().split()
    data_set = list(map(int, data_set))
    data_set = [data_set[i:i+4] for i in range(0, len(data_set), 4)]

data_set_per_user = {}
for i in data_set :
    if i[0] in data_set_per_user.keys() :
        data_set_per_user[i[0]].append(([i[1], i[2], i[3]]))
    else :
        data_set_per_user[i[0]] = [([i[1], i[2], i[3]])]

rate_average = {}
for i in data_set_per_user.keys() :
    rate_average[i] = sum([x[1] for x in data_set_per_user[i]]) / len(data_set_per_user[i])

def get_neighbor (data_per_user) :
    intersection_per_user = {} # common # : user pair

    users = list(data_per_user.keys())

    count = 0
    for i in users :
        for j in users :
            if users.index(i) >= users.index(j) :
                continue

            """
            common = get_common_item(data_per_user[i], data_per_user[j])

            if len(common) in list(intersection_per_user.keys()) :
                intersection_per_user[len(common)].append((i, j))
            else :
                intersection_per_user[len(common)] = [(i, j)]
            """
            similarity = get_similarity(data_per_user[i], data_per_user[j])
            if count % 10000 == 0 :
                print(i, j, similarity)
            count = count + 1
            if (similarity) in list(intersection_per_user.keys()) and similarity > 0.009:
                intersection_per_user[similarity].append((i, j))
            else :
                intersection_per_user[similarity] = [(i, j)]

    intersection_per_user = collections.OrderedDict(sorted(intersection_per_user.items(), reverse=True))
    neighbor_dict = {}
    neighbor_list = []

    for i in users :
        user_neighbor = []
        for j in intersection_per_user.keys() :
            if j > 0 :
                for k in intersection_per_user[j] :
                    if i in k :
                        user_neighbor.append([j, list(set(k)-set([i]))[0]])

                if len(user_neighbor) > neighbor_number :
                    break

        neighbor_list.append(user_neighbor)
        neighbor_dict[i] = neighbor_list

    return neighbor_dict

def get_similarity (item_x, item_y) :
    item_x_rank = list(map(lambda x: x[1], item_x))
    item_y_rank = list(map(lambda y: y[1], item_y))
    avg_x = sum(item_x_rank) / len(item_x_rank)
    avg_y = sum(item_y_rank) / len(item_y_rank)
    x_square_root = sum(map(lambda x : (x - avg_x)**2, item_x_rank))**0.5
    y_square_root = sum(map(lambda y : (y - avg_y)**2, item_y_rank))**0.5
    similarity = sum([(ix[1]-avg_x)*(iy[1]-avg_y) for ix, iy in zip(item_x, item_y) if ix[0] == iy[0]])
    return ((similarity) / (x_square_root * y_square_root))

def predict(neighbor, data_per_user, rate_avg, test_set):
    neighbor_rank = []

    for i in neighbor[test_set[0]]:
        for j in i:
            for k in data_per_user[j[1]]:
                if k[0] == test_set[1]:
                    new_val = (k[1]-rate_avg[j[1]])
                    neighbor_rank.append([new_val, j[0], k[2]])

    if len(neighbor_rank) > 0:
        new_val = round(rate_avg[test_set[0]] + sum(map(lambda x: x[0] * (x[1] * x[2]), neighbor_rank)) / sum(map(lambda x: (x[1] * x[2]), neighbor_rank)))
        if new_val < 1 :
            return 1
        elif new_val > 5 :
            return 5
        else :
            return new_val
    else:
        rank_list = [x[1] for x in data_per_user[test_set[0]]]
        #rank_list = list(map(lambda x: x[1], data_per_user[test_set[0]]))
        return max(set(rank_list), key=rank_list.count)

neighbor = get_neighbor(data_set_per_user)

# test result print

with open(test_file) as test :
    test_set = test.read().split()
    test_set = list(map(int, test_set))
    test_set = [test_set[i:i+4] for i in range(0, len(test_set), 4)]
test_set = list(map(lambda x : [x[0], x[1]], test_set))

count = 0
with open(output_file, "w") as prediction :
    for i in test_set :
        if count % 100 == 0 :
            print(count)
        count = count+1
        prediction.write("{}\t{}\t{}\n".format(i[0], i[1], str(predict(neighbor, data_set_per_user, rate_average, i))))
