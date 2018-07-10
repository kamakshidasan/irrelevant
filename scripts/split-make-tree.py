from helper import *

tree_type = TREE_TYPE_SPLIT

file_name = (sys.argv[1]).split('.')[0]

file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))

scalars = {}
visited = {}
adjacency = {}
pairs = {}

index_map = {}
order_map = {}

birth = {}
death = {}

string = ''

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

	# add mapping to dictionary
	index_map[index] = root

	return root

def add_node(index, parent):
	node = Tree()
	node.index = index
	parent.children.append(node)
	node.parent = parent
	node.label = scalars[index]
	node.pair = pairs[index]

	# add mapping to dictionary
	index_map[index] = node

	return node


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

def add_pairs(node):
	if(node == None):
		return
	else:
		node.birth = index_map[birth[node.index]]
		node.death = index_map[death[node.index]]
		for child in node.children:
			add_pairs(child)

def postorder(node):
	# python needs a mutable object for updation
	order = {'index': 1}

	def set_order(node):
		if(node == None):
			return
		else:
			for child in node.children:
				set_order(child)

			node.order = order['index']
			order_map[order['index']] = node
			order['index'] += 1

	set_order(node)


def stringify_tree(node):
	global string
	if(node == None):
		return
	else:
		string += '{'+ str(node.order)
		for child in node.children:
			stringify_tree(child)
		string += '}'
	return string

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

			# add birth and death values of nodes to dictionaries
			birth[node1] = node1
			death[node1] = node2

			birth[node2] = node1
			death[node2] = node2


root = get_merge_tree()
get_persistent_pairs()
tree = initialize_tree(root)
traverse(root, tree)
add_pairs(tree)
postorder(tree)
print stringify_tree(tree)

save_dictionary(tree, file_name, SPLIT_TREE_SUFFIX)
