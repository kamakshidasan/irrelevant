from helper import *

# get the list of triangles with their segmentation across all timesteps
file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
parent_path = cwd()
data_path = get_triangles_path(parent_path)
file_list = os.listdir(data_path)

# custom sort for ascending order of timesteps
file_list = sorted(file_list, key=sort_files)
num_files = len(file_list)

df = None
segmentation_counters = []
segmentation_lists = []

# make sure that hidden .DS_Store files do not exist
# read all the files and add them to a pandas dataframe
# basically create a really large table with each face having it's segmentation
# over all timesteps
for i in range(0, num_files):
    # for the first time, don't append
    if (i == 0):
        temporary_dataframe = pd.read_csv(os.path.join(data_path, file_list[i]))
        df = temporary_dataframe
    else:
        temporary_dataframe = pd.read_csv(os.path.join(data_path, file_list[i]))
        # concatenate only the 'segmentation' column to the table
        df = pd.concat([df, temporary_dataframe['segmentation']], axis=1)
    print 'Finished reading: ', i

# iterate across all rows in the dataframe
for index, row in df.iterrows():
    # convert pandas series to a list
    row_values = row.tolist()
    # first index has the triangle index
    # this is unused as it is equivalent to pandas' indexing scheme as well
    triangle_index = row_values[0]
    # get the list of segmentation identifiers across all timesteps
    segmentation_values = row_values[1:]
    # this is such a beautiful functionality
    # make a counter of all elements in the list
    # on query this returns the count of an element, if not present = 0
    segmentation_counter = Counter(segmentation_values)
    # just add this counter to a list for processing below
    segmentation_counters.append(segmentation_counter)

    # just for debugging
    if index % 1000 == 0:
        print index

# iterate across all segmentation identifiers
# currently in the von Karman datasheet
# there are 60 different segment identifiers from 0 to 56
# the enumeration range will change for different datasets

# for each segmentation identifier write a csv file
for segmentation_index in range(0, 60):
    # make a csv file for each segmentation
    tree_file_arguments = [SEGMENTATION_TRIANGLES_PREFIX, str(segmentation_index), CSV_EXTENSION]
    tree_file_path = get_output_path(file_path, tree_file_arguments, folder_name = SEGMENTATION_TRIANGLES_PREFIX)

    tree_file = open(tree_file_path, 'w')
    writer = csv.writer(tree_file, delimiter=',')
    writer.writerow(["triangle", "confidence"])

    # iterate across each face using it's segmentation counter
    for triangle_index, segmentation_counter in enumerate(segmentation_counters):
        # if segmentation_index is not found, then count is 0
        segmentation_count = segmentation_counter[segmentation_index]
        # confidence = number of times a face is mapped to a particular segment divided by total number of timesteps
        confidence = round(float(segmentation_count)/num_files, 2)
        writer.writerow([triangle_index, confidence])

        if triangle_index % 1000 == 0:
            print segmentation_index, triangle_index

    tree_file.close()
    print segmentation_index, 'done ;)'
