import sys

input_filename = sys.argv[1]
num_of_cluster = int(sys.argv[2])
eps = float(sys.argv[3])
min_points = int(sys.argv[4])

with open(input_filename) as file :
    objects = file.read().split()
objects = [objects[i : i + 3] for i in range(0, len(objects), 3)] #objects = [object id, x coordinate, y coordinate]
for i in objects :
    i[0] = int(i[0])
    i[1] = float(i[1])
    i[2] = float(i[2])
    i.append(None)

def db_scan(objects):
  count = 0
  for i in objects:
    if i[3] != None:
      continue

    neighbor = range_query(objects, i)

    if len(neighbor) <= min_points :
      i[3] = -1  # noise
      continue


    i[3] = count

    # Seed set S = N \ {p} neighbors to extend
    neighbor.remove(i)

    for j in neighbor:
      if j[3] == -1:
        j[3] = count

      if j[3] != None:
        continue

      j[3] = count
      neighbor2 = range_query(objects, j)

      if len(neighbor2) >= min_points:
        neighbor.extend(neighbor2)

    count = count + 1
    if count > num_of_cluster :
        break

def range_query (objects, clustered_objects) :
  neighbor = []
  for i in objects :
    if get_distance(i, clustered_objects) <= eps :
      neighbor.append(i)
  return neighbor

def get_distance (new_object, clustered_object) :
  return (((clustered_object[1]-new_object[1])**2+(clustered_object[2]-new_object[2])**2)**0.5)

db_scan(objects)

for i in range(num_of_cluster) :
  with open("input"+input_filename[-5]+"_cluster_"+str(i)+".txt", "w") as fo:
    for j in objects :
      print("j")
      if j[3] == i :
        fo.write(str(j[0])+"\n")

for i in objects :
    print("id : {} label : {}".format(i[0], i[3]))