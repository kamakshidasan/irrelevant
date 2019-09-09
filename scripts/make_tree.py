from helper import *

tree_type = TREE_TYPE_SPLIT

file_name = ''
file_path = ''

split_scalars = {}
visited = {}
adjacency = {}
pairs = {}

x_coordinates = {}
y_coordinates = {}
z_coordinates = {}

index_map = {}
postorder_map = {}
preorder_map = {}

birth = {}
death = {}

string = ''

ratio_threshold = 1.0

class Tree(object):
	def __init__(self):
		self.index = None
		self.children = []
		self.parent = None
		self.label = None
		self.pair = None
		self.birth = None
		self.death = None
		self.postorder = None
		self.preorder = None
		self.merged_nodes = []
		self.merged = False
		self.x = None
		self.y = None
		self.z = None

	def __str__(self):
		values = [self.preorder, self.pair.preorder, self.birth.preorder, self.death.preorder]
		return ' '.join(map(str, values))

	def is_root(self):
		return (self.parent == None)

	def is_leaf(self):
		return (len(self.children) == 0)

	def is_saddle(self):
		return ((not(self.is_root())) and (not(self.is_leaf())))

	def merge_node(self, parent):
		# sign papers for adoption
		for child in self.children:
			child.parent = parent
			child.pair = parent
			child.birth = child
			child.death = parent
		# transfer children of node to parent
		parent.children.extend(self.children)
		# transfer merged nodes of node to parent
		parent.merged_nodes.extend(self.merged_nodes)
		# remove children of current node after transfer
		self.children = []
		# make node to be merged with parent
		parent.merged_nodes.append(self)
		# remove node from children of parent
		parent.children.remove(self)
		# mark node as merged
		# the way to access other outer nodes would be using node.parent
		self.merged = True

def initialize_tree(index):
	root = Tree()
	root.index = index
	root.label = split_scalars[index]
	root.pair = pairs[index]

	# add coordinates as well
	root.x = x_coordinates[index]
	root.y = y_coordinates[index]
	root.z = z_coordinates[index]

	# add mapping to dictionary
	index_map[index] = root

	return root

def add_node(index, parent):
	node = Tree()
	node.index = index
	parent.children.append(node)
	node.parent = parent
	node.label = split_scalars[index]
	node.pair = pairs[index]

	# add coordinates as well
	node.x = x_coordinates[index]
	node.y = y_coordinates[index]
	node.z = z_coordinates[index]

	# add mapping to dictionary
	index_map[index] = node

	return node


def compare_vertices(a, b):
	# try to sort using the split_scalars
	# if they are equal, sort using index value
	if split_scalars[a] > split_scalars[b]:
		return 1
	elif split_scalars[a] == split_scalars[b]:
		if a > b:
			return 1
		else:
			return -1
	else:
		return -1

# same function as above, but this time compare the tree nodes
def compare_nodes(a, b):
	# try to sort using the split_scalars
	# if they are equal, sort using index value
	if a.label > b.label:
		return 1
	elif a.label == b.label:
		if a.index > b.index:
			return 1
		else:
			return -1
	else:
		return -1

def traverse(index, parent):
	#print index, split_scalars[index]
	visited[index] = True
	adjacency[index].sort(compare_vertices)
	for node in adjacency[index]:
		if not visited[node]:
			current = add_node(node, parent)
			traverse(node, current)

def add_pairs(node):
	if(node == None):
		return
	else:
		node.pair = index_map[pairs[node.index]]
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

			node.postorder = order['index']
			postorder_map[order['index']] = node
			order['index'] += 1

	set_order(node)

def preorder(node):
	# python needs a mutable object for updation
	order = {'index': 1}

	def set_order(node):
		if(node == None):
			return
		else:
			node.preorder = order['index']
			preorder_map[order['index']] = node
			order['index'] += 1

			for child in node.children:
				set_order(child)

	set_order(node)

# return the height for a given node
def height(node):
	if node is None:
		return 0

	max_depth = 0
	for child in node.children:
		max_depth = max(max_depth, height(child))

	return max_depth + 1

# Function to traverse level order traversal of tree
def merge_unstable_saddles(node):
	h = height(node)
	# traverse from below
	for i in range(h+1, 0, -1):
		traverse_level(node, i)
		#print ''

# find the ratio from bottom-up
def traverse_level(node, level):
	if node is None:
		return
	if level == 1:
		# do this merging only for saddles
		if node.is_saddle():
			# lets not tinker with the root
			if not node.parent.is_root():
				parent = node.parent
				ratio =  (node.label -  parent.label)

				# in this case I'm merging every saddle out there
				if ratio < ratio_threshold:
					node.merge_node(parent)
					#print round(ratio,4), node.label, parent.label, 'merge'
				else:
					print node.label, ratio, 'chill :)'
	elif level > 1:
		# traverse backwards
		for child in reversed(node.children):
			traverse_level(child, level - 1)

# sort the children at each level
def sort_tree(node):
	if node is None:
		return
	else:
		if not node.is_leaf():
			(node.children).sort(compare_nodes)
			for child in node.children:
				sort_tree(child)


def stringify_tree(node):
	global string
	if(node == None):
		return
	else:
		string += '{'
		string += str(node.postorder) + '|'
		string += str(node.index) + '|'
		string += str(node.label) + '|'
		string += str(node.birth.label) + '|'
		string += str(node.death.label)

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

			split_scalars[node1] = float(row[2])
			split_scalars[node2] = float(row[3])

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
			if (split_scalars[i] < split_scalars[adjacency[i][0]]):
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

			#if (node1 in split_scalars.keys()) and (node2 in split_scalars.keys()):
			# there will be pairs that do not exist in the merge tree
			# they will be removed/ignored subsequently

			pairs[node1] = node2
			pairs[node2] = node1

			# add birth and death values of nodes to dictionaries
			birth[node1] = node1
			death[node1] = node2

			birth[node2] = node1
			death[node2] = node2


def get_coordinates():
	coordinates_file_arguments = [tree_type, COORDINATES_INFIX, file_name, CSV_EXTENSION]
	coordinates_file_path = get_output_path(file_path, coordinates_file_arguments, folder_name = COORDINATES_FOLDER)

	with open(coordinates_file_path, 'rb') as coordinates_file:
		coordinates_file.readline()
		spamreader = csv.reader(coordinates_file, delimiter=' ')
		for r in spamreader:
			row = r[0].split(',')
			identifier = int(row[0])
			x = round(float(row[1]),3)
			y = round(float(row[2]),3)
			z = round(float(row[3]),3)

			x_coordinates[identifier] = x
			y_coordinates[identifier] = y
			z_coordinates[identifier] = z

def print_tree(node):
	if(node == None):
		return
	else:
		print node
		for child in node.children:
			print_tree(child)

def write_postorder(node):
	postorder_file_arguments = [tree_type, POSTORDER_INFIX, file_name, CSV_EXTENSION]
	postorder_file_path = get_output_path(file_path, postorder_file_arguments, folder_name = POSTORDER_FOLDER)

	postorder_file = open(postorder_file_path, 'w')
	fieldnames = ['node', 'order']

	writer = csv.writer(postorder_file, delimiter=',')
	writer.writerow(fieldnames)

	for order_index in postorder_map.keys():
		content = [postorder_map[order_index].index, order_index]
		writer.writerow(content)

	postorder_file.close()


def write_recon_file(node):
	recon_file_arguments = [file_name, TXT_EXTENSION]
	recon_file_path = get_output_path(file_path, recon_file_arguments, folder_name = RECON_FOLDER)

	recon_file = open(recon_file_path, 'w')

	writer = csv.writer(recon_file, delimiter=',')
	writer.writerow([len(postorder_map.keys())])

	def recon_print_tree(node):
		if(node == None):
			return
		else:
			if node.parent == None:
				parent_order = -1
			else:
				parent_order = node.parent.postorder

			values = [node.postorder, parent_order, node.death.postorder, -1, node.label]
			num_children = len(node.children)
			values.append(num_children)
			if num_children != 0:
				for child in node.children:
					values.append(child.postorder)

			writer.writerow(values)

			for child in node.children:
				recon_print_tree(child)

	recon_print_tree(node)
	recon_file.close()

def print_label(node):
	print str(node.preorder) + " [label=\""+ str(node.postorder) + " \\n["+ str(node.pair.postorder) + "] \\n" +str(node.label) +"\"]"

def print_edge(node):
	print str(node.parent.preorder) + "->" + str(node.preorder)

def print_tree_dot(node):
	if(node == None):
		return
	else:
		print_label(node)
		for child in node.children:
			print_edge(child)
			print_tree_dot(child)


def make_extremum_tree(name, path):
	global file_name, file_path
	file_name = name
	file_path = path
	root = get_merge_tree()
	get_persistent_pairs()
	get_coordinates()

	tree = initialize_tree(root)
	traverse(root, tree)
	add_pairs(tree)

	# merge saddles -- use the ratio_threshold at the top
	merge_unstable_saddles(tree)
	sort_tree(tree)

	# assign postorder and preorder indices after merging of saddles
	postorder(tree)
	preorder(tree)

	# write the file for unordered comparison
	write_recon_file(tree)

	# write the file for ordered comparison
	string_file_arguments = [file_name, TXT_EXTENSION]
	string_file_path = get_output_path(file_path, string_file_arguments, folder_name = STRINGS_FOLDER)
	save_string(stringify_tree(tree), string_file_path)

	# just write all the preorder indices to a file
	write_postorder(tree)

	#print_tree(tree)

	print 'digraph {'
	print_tree_dot(tree)
	print '}'
