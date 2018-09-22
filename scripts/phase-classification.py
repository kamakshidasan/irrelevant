from helper import *
from numpy import linalg as LA
import numpy as np

# get current file path
file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
parent_path = cwd()

coordinates = defaultdict(dict)
distances = defaultdict(dict)

num_timesteps = 275
maximum_distance = float("-inf")
minimum_distance = float("inf")

def euclidean_distance(a, b):
    dist = LA.norm(a - b)
    return round(dist, 3)


# read associated data for each timestep
for index in range(0, num_timesteps):
    file_name = 'tv_' + str(index)

    tuple_file_arguments = [file_name, TXT_EXTENSION]
    tuple_file_path = get_output_path(file_path, tuple_file_arguments, folder_name=TUPLES_FOLDER)

    # Read the file line by line
    with open(tuple_file_path, 'rb') as csvfile:
        csvfile.readline()
        spamreader = csv.reader(csvfile, delimiter=' ')
        for r in spamreader:
            row = r[0].split(',')
            timestep = int(row[0])
            order = int(row[1])
            value = float(row[2])
            birth = float(row[3])
            death = float(row[4])
            x = float(row[5])
            y = float(row[6])

            # add the coordinates to a dictionary of dictionaries
            coordinates[timestep][order] = np.asarray([x, y])

# run APTED for all timesteps
for current_timestep in range(0, num_timesteps):
    for comparison_timestep in range(0, num_timesteps):
        print current_timestep, comparison_timestep

        comparison_distance = 0

        current_file_name = 'tv_' + str(current_timestep)
        comparison_file_name = 'tv_' + str(comparison_timestep)

        current_file_arguments = [current_file_name, TXT_EXTENSION]
        current_file_path = get_output_path(file_path, current_file_arguments, folder_name=STRINGS_FOLDER)

        # if you have to compare with another tree, this should be the place to change it
        comparison_file_arguments = [comparison_file_name, TXT_EXTENSION]
        comparison_file_path = get_output_path(file_path, comparison_file_arguments, folder_name=STRINGS_FOLDER)

        #print current_file_path, comparison_file_path

        # find the mapping from APTED
        (value, output) = run_jar('apted-mapping.jar', ['-m -f', current_file_path, comparison_file_path])

        # parse the output from APTED and store it in a dictionary
        output = output.split('\n')

        for mapping in output:
            # each mapping is seperated by an arrow mark
            [current_tree_node, comparison_tree_node] = mapping.split('->')

            # convert the strings to integers
            current_tree_node = int(current_tree_node)
            comparison_tree_node = int(comparison_tree_node)

            # in case the nodes have a null mapping, they are represented with 0
            if current_tree_node != 0 and comparison_tree_node != 0:
                # print current_timestep, current_tree_node, "->" , comparison_timestep, comparison_tree_node
                coordinate1 = coordinates[current_timestep][current_tree_node]
                coordinate2 = coordinates[comparison_timestep][comparison_tree_node]
                distance = euclidean_distance(coordinate1, coordinate2)
                comparison_distance += distance

        distances[current_timestep][comparison_timestep] = comparison_distance
        maximum_distance = max(maximum_distance, comparison_distance)
        minimum_distance = min(minimum_distance, comparison_distance)

# write the normalized results to a file
heatmap_file = open('heatmap-'+str(num_timesteps)+'-normalized.csv', 'w')
writer = csv.writer(heatmap_file, delimiter=',')
# append a useless name to the column
# column names are from 0 to number of timesteps
fieldnames = ['timestep']
for current_timestep in range(0, num_timesteps):
    fieldnames.append(current_timestep)
writer.writerow(fieldnames)

# iterate through every pair of timesteps
for current_timestep in range(0, num_timesteps):
    content = [current_timestep]
    for comparison_timestep in range(0, num_timesteps):
        comparison_distance = distances[current_timestep][comparison_timestep]
        numerator = (comparison_distance - minimum_distance)
        denominator = (maximum_distance - minimum_distance)
        normalised_comparison_distance = round((numerator/denominator), 3)
        content.append(normalised_comparison_distance)
    writer.writerow(content)
heatmap_file.close()

# write the results to a file without normalization
heatmap_file = open('heatmap-'+str(num_timesteps)+'.csv', 'w')
writer = csv.writer(heatmap_file, delimiter=',')
# append a useless name to the column
# column names are from 0 to number of timesteps
fieldnames = ['timestep']
for current_timestep in range(0, num_timesteps):
    fieldnames.append(current_timestep)
writer.writerow(fieldnames)

# iterate through every pair of timesteps
for current_timestep in range(0, num_timesteps):
    content = [current_timestep]
    for comparison_timestep in range(0, num_timesteps):
        comparison_distance = distances[current_timestep][comparison_timestep]
        content.append(round(comparison_distance, 3))
    writer.writerow(content)
heatmap_file.close()

print 'done :)'
