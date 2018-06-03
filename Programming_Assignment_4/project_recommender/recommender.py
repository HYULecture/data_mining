import sys

base_file = sys.argv[1]
test_file = sys.argv[2] #[user_id]\t[item_id]\t[rating]\t[time_stamp]\n
output_file = "../u"+base_file[1]+".base_prediction.txt" #[user_id]\t[item_id]\t[rating]\n

neighbor_number = 10

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
            if count % 1000 == 0 :
                print(i, j, similarity)
            count = count + 1
            if (similarity) in list(intersection_per_user.keys()) :
                intersection_per_user[similarity].append((i, j))
            else :
                intersection_per_user[similarity] = [(i, j)]


    neighbor_list = []

    for i in users :
        user_neighbor = []
        for j in intersection_per_user.keys() :
            if j > 0 :
                for k in intersection_per_user[j] :
                    if i in k :
                        user_neighbor.append(set(k)-set([i]))
                if len(user_neighbor) > neighbor_number :
                    break

        neighbor_list.append(user_neighbor)

    return neighbor_list

def get_common_item (item_x, item_y) :
    common_item = []
    for i in item_x :
        for j in item_y :
            if get_similarity(i, j) :
                common_item.append(i)
    return common_item

def get_similarity (item_x, item_y) :
    item_x_rank = list(map(lambda x: x[1], item_x))
    item_y_rank = list(map(lambda y: y[1], item_y))
    avg_x = sum(item_x_rank) / len(item_x_rank)
    avg_y = sum(item_y_rank) / len(item_y_rank)
    x_square_root = sum(list(map(lambda x : (x - avg_x)**2, item_x_rank)))**0.5
    y_square_root = sum(list(map(lambda y : (y - avg_y)**2, item_y_rank)))**0.5
    similarity = 0
    for i in item_x :
        for j in item_y :
            if i[0] == j[0] :
                similarity += (i[1]-avg_x)*(j[1]-avg_y)
    return ((similarity) / (x_square_root * y_square_root))

neighbor = get_neighbor(data_set_per_user)
for i in neighbor :
    print(i)
    pass

# test result print
with open(test_file) as test :
    test_set = test.read().split()
    test_set = list(map(int, test_set))
    test_set = [test_set[i:i+4] for i in range(0, len(test_set), 4)]

