from helper import *

tree_type = TREE_TYPE_SPLIT

# get current file path
file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
parent_path = cwd()
comparison_folder_path = get_folder(file_path, folder_name=COMPARISON_APTED_FOLDER)
file_list = os.listdir(comparison_folder_path)

# custom sort for ascending order of timesteps
# remove ds_store if it exists
file_list = sorted(file_list, key=sort_comparison_files)
remove_ds_store(file_list)

def get_postorder_mapping(timestep):
	postorder_mapping = {}

	# get a postorder file
	postorder_file_arguments = [tree_type, POSTORDER_INFIX, TIMESTEP_PREFIX, timestep, CSV_EXTENSION]
	postorder_file_path = get_output_path(file_path, postorder_file_arguments, folder_name = POSTORDER_FOLDER)

	# read the postorder mapping file
	with open(postorder_file_path, 'rb') as csvfile:
	    csvfile.readline()
	    spamreader = csv.reader(csvfile, delimiter=' ')
	    for r in spamreader:
	        row = r[0].split(',')
	        node_id = int(row[0])
	        order = int(row[1])
	        postorder_mapping[order] = node_id

	return postorder_mapping

def get_coordinate_mapping(timestep):
	coordinate_mapping = {}

	coordinates_file_arguments = [tree_type, COORDINATES_INFIX, TIMESTEP_PREFIX, timestep, CSV_EXTENSION]
	coordinates_file_path = get_output_path(file_path, coordinates_file_arguments, folder_name = COORDINATES_FOLDER)

	# read the postorder mapping file
	with open(coordinates_file_path, 'rb') as csvfile:
	    csvfile.readline()
	    spamreader = csv.reader(csvfile, delimiter=' ')
	    for r in spamreader:
			row = r[0].split(',')
			node_id = int(row[0])
			x = float(row[1])
			y = float(row[2])
			z = float(row[3])
			coordinate_mapping[node_id] = [x, y, z]

	return coordinate_mapping

def get_apted_mapping(file_name):
	apted_mapping = defaultdict(list)

	apted_file_path = os.path.join(comparison_folder_path, file_name)
	# Read the comparison files
	with open(apted_file_path, 'rb') as csvfile:
		csvfile.readline()
		spamreader = csv.reader(csvfile, delimiter=' ')
		for r in spamreader:
			row = r[0].split(',')
			timestep_index = int(row[0])
			current_node = int(row[1])
			comparison_node = int(row[2])

			apted_mapping[current_node].append(comparison_node)

	return apted_mapping

def get_euclidean_distance(a, b):
	return distance.euclidean(a, b)

tracks = []
previous_track = {}
current_track = {}

# iterate through all of the files
for file_name in file_list:
	#print file_name
	[current_timestep, comparison_timestep] = get_comparison_indices(file_name)

	current_postorder_mapping = get_postorder_mapping(current_timestep)
	comparison_postorder_mapping = get_postorder_mapping(comparison_timestep)

	current_coordinate_mapping = get_coordinate_mapping(current_timestep)
	comparison_coordinate_mapping = get_coordinate_mapping(comparison_timestep)

	apted_mapping = get_apted_mapping(file_name)

	for current_node in apted_mapping.keys():
		#print apted_mapping[current_node]
		# derive information from the other files
		if current_node != 0:
			comparison_node = apted_mapping[current_node][0]

			if comparison_node != 0:
				current_vertex_identifier = current_postorder_mapping[current_node]
				current_vertex_coordinates = current_coordinate_mapping[current_vertex_identifier]

				comparison_vertex_identifier = comparison_postorder_mapping[comparison_node]
				comparison_vertex_coordinates = comparison_coordinate_mapping[comparison_vertex_identifier]

				if comparison_node in previous_track.keys():
					(tracks[previous_track[comparison_node]]).append([current_node, current_vertex_coordinates, current_timestep])
					current_track[current_node] = previous_track[comparison_node]
				else:
					tracks.append([
						[comparison_node, comparison_vertex_coordinates, comparison_timestep],
						[current_node, current_vertex_coordinates, current_timestep]
					])

					current_track[current_node] = len(tracks) - 1

				#euclidean_distance = get_euclidean_distance(comparison_vertex_coordinates, current_vertex_coordinates)

				#print current_node, comparison_node, euclidean_distance
		else:
			# do something important here
			pass
	previous_track = {}
	previous_track = current_track
	current_track = {}

tracks.sort(key=len)

for index, track in enumerate(tracks):
	sum = 0
	for timestep in range(1, len(track)):
		a = (track[timestep-1])[1]
		b = (track[timestep])[1]
		a_timestep = (track[timestep-1])[2]
		b_timestep = (track[timestep])[2]
		sum += get_euclidean_distance(a, b)
	print "**", index, len(track), sum/len(track)
