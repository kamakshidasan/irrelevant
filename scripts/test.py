import os
import sys
from helper import *
from random import randint

try:
	cores = int(sys.argv[1])
	start = int(sys.argv[2])
except:
	print '***** Usage: python test.py <cores> <start> *****'
	exit()

count = start
highest = 230

# reusing a syringe and a results file has the same impact
# throw away the earlier used results file
try:
	file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
	results_path = get_output_path(file_path, [EDIT_DISTANCE_RESULT, CSV_EXTENSION], folder_name = RESULTS_FOLDER)
	os.remove(results_path)
except OSError:
	pass

def print_statement():
	global count
	statement = ""
	for j in range(0, 230):
		if count <= highest:
			#statement += 'python edit-distance.py tv_'+str(count) + ' tv_1'+ '\n'
			#statement += 'python edit-distance-gaps.py tv_'+str(count) + ' tv_'+str(count-1) + '\n'
			#statement += 'python print-gaps.py tv_'+str(count) + ' tv_'+str(count-1) + '\n'
			#statement += 'python contour-distance.py tv_'+str(count) + ' tv_'+str(count-1) + '\n'
			statement += 'java -jar apted-time.jar -f '
			statement += '../strings/tv_'+str(count) + '.txt ../strings/tv_0.txt' + '\n'
			count+=1

	# Delete script after execution [Please be nice :)]
	statement += 'rm -- \"$0\"'
	return statement

# Basically print Trump's speeches
def print_random_statements():
	statement = ""
	for i in range(0,9):
		random_first = randint(1,highest-1)
		random_second = randint(1,highest-1)
		statement += 'python edit-distance-gaps.py tv_'+str(random_first) + ' tv_'+str(random_second) + '\n'
		statement += 'python print-gaps.py tv_'+str(random_first) + ' tv_'+str(random_second) + '\n'
	# Delete script after execution [Please be nice :)]
	statement += 'rm -- \"$0\"'
	return statement

for i in range(0, cores):
	statement = print_statement()
	#statement = print_random_statements()
	f = open('script'+str(i)+'.sh', 'w')
	f.write(statement)
	f.close()
	#print statement
	os.system('chmod +x script'+str(i)+'.sh')
	if count > highest:
		break

command = ""
for i in range(0, cores):
	command += "./script"+str(i)+".sh & "

print 'Started!'

os.system(command)

print 'next start at ', count
