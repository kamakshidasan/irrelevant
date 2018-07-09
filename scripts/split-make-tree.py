from helper import *

tree_type = TREE_TYPE_SPLIT

file_name = (sys.argv[1]).split('.')[0]

file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))

scalars = {}
visited = {}
adjacency = {}
pairs = {}

index_map = {}
inverse_index_map = {}

birth = {}
death = {}

order = 1

class Tree(object):
	def __init__(self):
		self.index = None
		self.children = []
		self.parent = None
		self.label = None
		self.pair = None
		self.birth = None
		self.death = None
		self.order = None

def initialize_tree(index):
	root = Tree()
	root.index = index
	root.label = scalars[index]
	root.pair = pairs[index]
	return root

def add_node(index, parent):
	current = Tree()
	current.index = index
	parent.children.append(current)
	current.parent = parent
	current.label = scalars[index]
	current.pair = pairs[index]
	return current


def compare_nodes(a, b):
	# try to sort using the scalars
	# if they are equal, sort using index value
	if scalars[a] > scalars[b]:
		return 1
	elif scalars[a] == scalars[b]:
		if a > b:
			return 1
		else:
			return -1
	else:
		return -1

def traverse(index, parent):
	#print index, scalars[index]
	visited[index] = True
	adjacency[index].sort(compare_nodes)
	for node in adjacency[index]:
		if not visited[node]:
			current = add_node(node, parent)
			traverse(node, current)

def postorder(node):
	global order
	if(node == None):
		return
	else:
		#node.birth = scalars[birth[node.value]]
		#node.death = scalars[death[node.value]]

		for child in node.children:
			postorder(child)

		node.order = order
		print node.order, node.index, node.label, node.pair
		order += 1

def get_merge_tree():
	# Get merge tree path
	tree_file_arguments = [tree_type, TREE_INFIX, file_name, CSV_EXTENSION]
	tree_file_path = get_output_path(file_path, tree_file_arguments, folder_name = TREES_FOLDER)

	# Read merge tree file
	with open(tree_file_path, 'rb') as csvfile:
		csvfile.readline()
		spamreader = csv.reader(csvfile, delimiter=' ')
		for r in spamreader:
			row = r[0].split(',')
			node1 = int(row[0])
			node2 = int(row[1])

			scalars[node1] = float(row[2])
			scalars[node2] = float(row[3])

			visited[node1] = False
			visited[node2] = False

			if node1 not in adjacency.keys():
				adjacency[node1] = []

			if node2 not in adjacency.keys():
				adjacency[node2] = []

			adjacency[node1].append(node2)
			adjacency[node2].append(node1)

	for i in adjacency.keys():
		if len(adjacency[i]) == 1:
			if (scalars[i] < scalars[adjacency[i][0]]):
				root = i

	return root

def get_persistent_pairs():
	# Get persistence pairs
	pairs_file_arguments = [tree_type, PAIRS_INFIX, file_name, CSV_EXTENSION]
	pairs_file_path = get_output_path(file_path, pairs_file_arguments, folder_name = PAIRS_FOLDER)

	with open(pairs_file_path, 'rb') as persistence_pairs:
		persistence_pairs.readline()
		spamreader = csv.reader(persistence_pairs, delimiter=' ')
		for r in spamreader:
			row = r[0].split(',')
			node1 = int(row[0])
			node2 = int(row[1])

			#if (node1 in scalars.keys()) and (node2 in scalars.keys()):
			# there will be pairs that do not exist in the merge tree
			# they will be removed/ignored subsequently
			pairs[node1] = node2
			pairs[node2] = node1


root = get_merge_tree()
get_persistent_pairs()
tree = initialize_tree(root)
traverse(root, tree)
postorder(tree)

save_dictionary(tree, file_name, CONTOUR_TREE_SUFFIX)
