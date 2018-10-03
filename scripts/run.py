import fileinput
import re
import os
from helper import *
import inspect
from datetime import datetime

# get current file path
file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
parent_path = cwd()
data_path = get_input_path(parent_path)
file_list = os.listdir(data_path)

# custom sort for ascending order of timesteps
file_list = sorted(file_list, key=sort_files)

# insert a wildcard at the beginning
file_list.insert(0, 'adhitya.vtk')

# create a new file list for comparison files
file_list_again = os.listdir(data_path)
comparison_file_list = sorted(file_list_again, key=sort_files)
comparison_file_list.insert(0, 'aishwarya.vtk')
# for the zeroth file, compare with itself
comparison_file_list.insert(1, comparison_file_list[1])
comparison_file_list = [os.path.splitext(x)[0] for x in comparison_file_list]

#num_files = len(file_list)
num_files = 127

for i in range(1, num_files+1):

	compute_file = get_output_path(file_path, [COMPUTE_SCRIPT], folder_name = SCRIPTS_FOLDER)
	replace_wildcard(compute_file, file_list[i-1], file_list[i])

	compute_file = get_output_path(file_path, [COMPUTE_SCRIPT], folder_name = SCRIPTS_FOLDER)
	replace_wildcard(compute_file, comparison_file_list[i-1], comparison_file_list[i])

	run_paraview_script(compute_file)

	files_left = num_files - i
	print file_list[i], 'Done :)', files_left, ' files remaining'
	print file_list[i-1], comparison_file_list[i-1]


# Back to normalcy :P
replace_wildcard(compute_file, file_list[i], 'adhitya.vtk')
replace_wildcard(compute_file, comparison_file_list[i], 'aishwarya')
