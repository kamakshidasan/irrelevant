from paraview.simple import *
import csv, os
from datetime import datetime
from helper import *
from sets import Set
from collections import defaultdict

paraview.simple._DisableFirstRenderCameraReset()

# start timer
startTime = datetime.now()

# initialize Path variables
# create a new 'Legacy VTK Reader'
full_file_name = 'tv_1.vtk'
parent_path = cwd()
data_path = get_input_path(parent_path)
file_path = join_file_path(data_path, full_file_name)
file_name = get_file_name(full_file_name)

# create a new 'Legacy VTK Reader'
inputFile = LegacyVTKReader(FileNames=[file_path])
simplification_percentage = 0.1

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
inputFileDisplay = Show(inputFile, renderView1)
inputFileDisplay.Representation = 'Surface'

# reset view to fit data
renderView1.ResetCamera()
renderView1.InteractionMode = '2D'
renderView1.CameraPosition = [199.5, 24.5, 10000.0]
renderView1.CameraFocalPoint = [199.5, 24.5, 0.0]
inputFileDisplay.SetScalarBarVisibility(renderView1, False)
renderView1.Update()

# get color transfer function/color map for 'magnitude'
magnitudeLUT = GetColorTransferFunction('magnitude')

# create a new 'Extract Surface'
extractSurface1 = ExtractSurface(Input=inputFile)
extractSurface1Display = Show(extractSurface1, renderView1)
extractSurface1Display.Representation = 'Surface'
Hide(inputFile, renderView1)
extractSurface1Display.SetScalarBarVisibility(renderView1, False)
renderView1.Update()

# create a new 'Triangulate'
triangulate1 = Triangulate(Input=extractSurface1)
triangulate1Display = Show(triangulate1, renderView1)
triangulate1Display.Representation = 'Surface'
Hide(extractSurface1, renderView1)
triangulate1Display.SetScalarBarVisibility(renderView1, False)
renderView1.Update()

# create a new 'Loop Subdivision'
loopSubdivision1 = LoopSubdivision(Input=triangulate1)
loopSubdivision1.NumberofSubdivisions = 2
loopSubdivision1Display = Show(loopSubdivision1, renderView1)
loopSubdivision1Display.Representation = 'Surface'
Hide(triangulate1, renderView1)
loopSubdivision1Display.SetScalarBarVisibility(renderView1, False)
renderView1.Update()

# create a new 'Clean to Grid'
vtkFile = CleantoGrid(Input=loopSubdivision1)
vtkFileDisplay = Show(vtkFile, renderView1)
vtkFileDisplay.Representation = 'Surface'
Hide(loopSubdivision1, renderView1)
vtkFileDisplay.SetScalarBarVisibility(renderView1, False)
renderView1.Update()

# create a new 'Extract Subset'
#vtkFile = ExtractSubset(Input=inputFile)
#vtkFile.VOI = [0, 399, 0, 49, 0, 0]
#vtkFileDisplay = Show(vtkFile, renderView1)
#vtkFileDisplay.Representation = 'Slice'
#vtkFileDisplay.SetScalarBarVisibility(renderView1, True)
#renderView1.Update()
#Hide(inputFile, renderView1)

# get layout
layout1 = GetLayout()
layout1.SplitHorizontal(0, 0.5)
SetActiveView(None)

# Create a new 'Render View'
renderView2 = CreateView('RenderView')
renderView2.ViewSize = [1038, 1179]
renderView2.AxesGrid = 'GridAxes3DActor'
renderView2.StereoType = 0
renderView2.Background = [0.32, 0.34, 0.43]

# init the 'GridAxes3DActor' selected for 'AxesGrid'
renderView2.AxesGrid.XTitleFontFile = ''
renderView2.AxesGrid.YTitleFontFile = ''
renderView2.AxesGrid.ZTitleFontFile = ''
renderView2.AxesGrid.XLabelFontFile = ''
renderView2.AxesGrid.YLabelFontFile = ''
renderView2.AxesGrid.ZLabelFontFile = ''

# place view in the layout
layout1.AssignView(2, renderView2)

# create a new 'TTK PersistenceDiagram'
persistenceDiagram = TTKPersistenceDiagram(Input=vtkFile)
#persistenceDiagram.UseInputOffsetField = 1
#persistenceDiagram.InputOffsetField = ''
persistenceDiagramDisplay = Show(persistenceDiagram, renderView2)
persistenceDiagramDisplay.Representation = 'Surface'

# reset view to fit data
renderView2.ResetCamera()
renderView2.InteractionMode = '2D'
renderView2.CameraPosition = [0.6912000179290771, 0.710545003414154, 10000.0]
renderView2.CameraFocalPoint = [0.6912000179290771, 0.710545003414154, 0.0]
renderView2.Update()

# create a new 'Threshold'
persistencePairsThreshold = Threshold(Input=persistenceDiagram)
persistencePairsThreshold.Scalars = ['CELLS', 'PairType']
persistencePairsThreshold.ThresholdRange = [-1, 1]

# show data in view
persistencePairsThresholdDisplay = Show(persistencePairsThreshold, renderView2)
persistencePairsThresholdDisplay.Representation = 'Surface'
Hide(persistenceDiagram, renderView2)
renderView2.Update()

# find max persistence by iterating across the diagram!
persistence_data = servermanager.Fetch(persistencePairsThreshold)

# Get the number of persistent points and arcs
num_persistent_points = persistencePairsThreshold.GetDataInformation().GetNumberOfPoints()
num_persistent_cells = persistencePairsThreshold.GetDataInformation().GetNumberOfCells()

max_persistence = 0
for index in range(num_persistent_cells):
	current_persistence = persistence_data.GetCellData().GetArray('Persistence').GetValue(index)
	max_persistence = max(current_persistence, max_persistence)

# filter all persistent pairs above minimum persistence threshold
min_persistence = (simplification_percentage *  max_persistence) / 100.0

# create a new 'Threshold'
persistenceThreshold = Threshold(Input=persistencePairsThreshold)
persistenceThreshold.Scalars = ['CELLS', 'Persistence']
persistenceThreshold.ThresholdRange = [min_persistence, max_persistence]
persistenceThresholdDisplay = Show(persistenceThreshold, renderView2)
persistenceThresholdDisplay.Representation = 'Surface'
Hide(persistencePairsThreshold, renderView2)
renderView2.Update()

# set active view
SetActiveView(renderView1)

# create a new 'TTK TopologicalSimplification'
topologicalSimplification = TTKTopologicalSimplification(Domain=vtkFile,
    Constraints=persistenceThreshold)
#topologicalSimplification.UseInputOffsetField = 1
#topologicalSimplification.InputOffsetField = ''
topologicalSimplificationDisplay = Show(topologicalSimplification, renderView1)
topologicalSimplificationDisplay.Representation = 'Surface'
Hide(vtkFile, renderView1)
topologicalSimplificationDisplay.SetScalarBarVisibility(renderView1, False)
renderView1.Update()

# create a new 'TTK Merge and Contour Tree (FTM)'
contourTree = TTKMergeandContourTreeFTM(Input=topologicalSimplification)
#contourTree.UseInputOffsetScalarField = 1
contourTree.TreeType = 'Split Tree'
contourTreeDisplay = Show(contourTree, renderView1)
contourTreeDisplay.Representation = 'Surface'
Hide(topologicalSimplification, renderView1)
contourTreeDisplay.SetScalarBarVisibility(renderView1, False)
contourTreeDisplay_1 = Show(OutputPort(contourTree, 1), renderView1)
contourTreeDisplay_1.Representation = 'Surface'
Hide(topologicalSimplification, renderView1)
contourTreeDisplay_1.SetScalarBarVisibility(renderView1, False)
contourTreeDisplay_2 = Show(OutputPort(contourTree, 2), renderView1)
contourTreeDisplay_2.Representation = 'Surface'
Hide(topologicalSimplification, renderView1)
contourTreeDisplay_2.SetScalarBarVisibility(renderView1, False)
renderView1.Update()

# create a new 'Threshold'
segmentationThreshold = Threshold(Input=OutputPort(contourTree, 2))
segmentationThreshold.Scalars = ['POINTS', 'RegionType']
segmentationThreshold.ThresholdRange = [3, 4]
segmentationThresholdDisplay = Show(segmentationThreshold, renderView1)
segmentationThresholdDisplay.Representation = 'Surface'
#Hide(vtkFile, renderView1)
renderView1.Update()

# create a new 'Threshold'
segmentationThreshold2 = Threshold(Input=OutputPort(contourTree, 2))
segmentationThreshold2.Scalars = ['POINTS', 'RegionType']
segmentationThreshold2.ThresholdRange = [1, 1]
segmentationThresholdDisplay2 = Show(segmentationThreshold2, renderView1)
segmentationThresholdDisplay2.Representation = 'Surface'
#Hide(vtkFile, renderView1)
Hide(segmentationThreshold2, renderView1)
renderView1.Update()


# trying something new here
#a = [None]
#b = [None]
#a[0] = Threshold(Input=OutputPort(contourTree, 2))
#a[0].Scalars = ['POINTS', 'RegionType']
#a[0].ThresholdRange = [2, 2]
#b[0] = Show(a[0], renderView1)
#b[0].Representation = 'Surface'
#Hide(vtkFile, renderView1)
#renderView1.Update()

#********** have extract cells ************
# 1) find the coordinates of the split/split-join nodes of the contour tree
# 2) find a way to have an array of filters in paraview

# get type for usage below
tree_type = get_tree_type(contourTree.TreeType)

# get color transfer function/color map for 'NodeType'
nodeTypeLUT = GetColorTransferFunction('NodeType')

# hide data in view
Hide(OutputPort(contourTree, 2), renderView1)
SetActiveSource(vtkFile)
#vtkFileDisplay = Show(vtkFile, renderView1)
#vtkFileDisplay.SetScalarBarVisibility(renderView1, False)

# set active source
SetActiveSource(contourTree)
contourTreeDisplay_1.ScaleTransferFunction.RescaleTransferFunction(0.0, 1.17578133675e-38)
contourTreeDisplay_1.OpacityTransferFunction.RescaleTransferFunction(0.0, 1.17578133675e-38)
segmentationIdLUT = GetColorTransferFunction('RegionSize')

# create a new 'Extract Surface'
extractSurface = ExtractSurface(Input=OutputPort(contourTree, 1))
extractSurfaceDisplay = Show(extractSurface, renderView1)
extractSurfaceDisplay.Representation = 'Surface'
Hide(OutputPort(contourTree, 1), renderView1)
extractSurfaceDisplay.SetScalarBarVisibility(renderView1, False)
renderView1.Update()

# create a new 'Tube'
tube = Tube(Input=extractSurface)
tube.Vectors = [None, '']
tube.Radius = 1.7
tubeDisplay = Show(tube, renderView1)
tubeDisplay.Representation = 'Surface'
Hide(extractSurface, renderView1)
tubeDisplay.SetScalarBarVisibility(renderView1, False)
HideScalarBarIfNotNeeded(segmentationIdLUT, renderView1)
tubeDisplay.DiffuseColor = [1.0, 1.0, 0.0]
renderView1.Update()

SetActiveSource(contourTree)

# create a new 'TTK SphereFromPoint'
tTKSphereFromPoint = TTKSphereFromPoint(Input=contourTree)
tTKSphereFromPoint.Radius = 2.0
tTKSphereFromPointDisplay = Show(tTKSphereFromPoint, renderView1)
tTKSphereFromPointDisplay.Representation = 'Surface'
Hide(contourTree, renderView1)
tTKSphereFromPointDisplay.SetScalarBarVisibility(renderView1, False)
renderView1.Update()

# create a new 'Threshold'
tTKSphereFromPointThreshold = Threshold(Input=tTKSphereFromPoint)
tTKSphereFromPointThreshold.Scalars = ['POINTS', 'NodeType']
tTKSphereFromPointThreshold.ThresholdRange = [0, 4]
tTKSphereFromPointThresholdDisplay = Show(tTKSphereFromPointThreshold, renderView1)
tTKSphereFromPointThresholdDisplay.Representation = 'Surface'
Hide(tTKSphereFromPoint, renderView1)
renderView1.Update()

# split cell
layout1.SplitVertical(1, 0.5)
SetActiveView(None)

# Create a new 'SpreadSheet View'
spreadSheetView1 = CreateView('SpreadSheetView')
spreadSheetView1.ColumnToSort = ''
spreadSheetView1.BlockSize = 1024L

# place view in the layout
layout1.AssignView(4, spreadSheetView1)

# show data in view
contourForestDisplayArcs = Show(OutputPort(contourTree, 1), spreadSheetView1)
contourForestDisplayArcs.FieldAssociation = 'Cell Data'
arcs_file_arguments = [tree_type, ARCS_INFIX, file_name, CSV_EXTENSION]
arcs_file_path = get_output_path(file_path, arcs_file_arguments, folder_name = INTERMEDIATE_FOLDER)
ExportView(arcs_file_path, view=spreadSheetView1, FilterColumnsByVisibility=0)

# Write node of contour tree to file
contourForestDisplayNodes = Show(contourTree, spreadSheetView1)
contourForestDisplayNodes.FieldAssociation = 'Point Data'
nodes_file_arguments = [tree_type, NODES_INFIX, file_name, CSV_EXTENSION]
nodes_file_path = get_output_path(file_path, nodes_file_arguments, folder_name = INTERMEDIATE_FOLDER)
ExportView(nodes_file_path, view=spreadSheetView1, FilterColumnsByVisibility=1)

SetActiveView(renderView2)
layout1.SplitVertical(2, 0.5)
SetActiveView(None)

# Create a new 'SpreadSheet View'
spreadSheetView2 = CreateView('SpreadSheetView')
spreadSheetView2.ColumnToSort = ''
spreadSheetView2.BlockSize = 1024L
layout1.AssignView(6, spreadSheetView2)

# show data in view
contourTreeDisplay_4 = Show(contourTree, spreadSheetView2)
SetActiveView(renderView1)
SetActiveSource(contourTree)
SetActiveSource(topologicalSimplification)
SetActiveView(renderView2)
Hide(persistenceThreshold, renderView2)

# create a new 'TTK PersistenceDiagram'
simplififedPersistenceDiagram = TTKPersistenceDiagram(Input=topologicalSimplification)
#simplififedPersistenceDiagram.UseInputOffsetField = 1
simplififedPersistenceDiagramDisplay = Show(simplififedPersistenceDiagram, renderView2)
simplififedPersistenceDiagramDisplay.Representation = 'Surface'

SetActiveView(renderView1)
Hide(tTKSphereFromPointThreshold, renderView1)
Hide(tube, renderView1)

SetActiveSource(topologicalSimplification)
triangulationRequest = TTKTriangulationRequest(Input=topologicalSimplification)
triangulationRequest.Simplexidentifier = 281569
triangulationRequest.Requesttype = 'Link'
triangulationRequestDisplay = Show(triangulationRequest, renderView1)
triangulationRequestDisplay.Representation = 'Surface'
Hide(topologicalSimplification, renderView1)
renderView1.Update()

# initialize dictionaries
scalars = {}
nodes = {}
birth_pairs = {}
arcs = defaultdict(list)

with open(nodes_file_path, 'rb') as csvfile:
	csvfile.readline()
	spamreader = csv.reader(csvfile, delimiter=' ')
	for r in spamreader:
		row = r[0].split(',')
		node_id = int(row[0])
		scalar_value = float(row[1])
		vertex_index = int(row[2])

		# store above values to dictionaries
		nodes[node_id] = vertex_index
		scalars[vertex_index] = scalar_value

# Write the Merge Tree to file
tree_file_arguments = [tree_type, TREE_INFIX, file_name, CSV_EXTENSION]
tree_file_path = get_output_path(file_path, tree_file_arguments, folder_name = TREES_FOLDER)

tree_file = open(tree_file_path, 'w')
fieldnames = ['Node:0', 'Node:1', 'Scalar:0', 'Scalar:1']
writer = csv.writer(tree_file, delimiter=',')
writer.writerow(fieldnames)

# Read the intermediate arcs file
with open(arcs_file_path, 'rb') as csvfile:
	csvfile.readline()
	spamreader = csv.reader(csvfile, delimiter=' ')
	for index, r in enumerate(spamreader):
		row = r[0].split(',')
		upNodeId = int(row[1])
		downNodeId = int(row[2])

		up_vertex_index = nodes[upNodeId]
		down_vertex_index = nodes[downNodeId]

		#print up_vertex_index, down_vertex_index

		# store arcs in a dictionary
		arcs[up_vertex_index].append(down_vertex_index)
		arcs[down_vertex_index].append(up_vertex_index)

		content = [up_vertex_index, down_vertex_index, scalars[up_vertex_index], scalars[down_vertex_index]]
		writer.writerow(content)

tree_file.close()

# Write persistent pairs after thresholding to file
pairs_file_arguments = [tree_type, PAIRS_INFIX, file_name, CSV_EXTENSION]
pairs_file_path = get_output_path(file_path, pairs_file_arguments, folder_name = PAIRS_FOLDER)

pairs_file = open(pairs_file_path, 'w')
fieldnames = ['Birth', 'Death']
writer = csv.writer(pairs_file, delimiter=',')
writer.writerow(fieldnames)
birth_vertex = None

# The persistent pairs are one after the other
# First comes birth; immediately followed by death [Adhitya getting philosophical :P]

# Iterate over all the points in the persistent diagram
persistence_threshold_data = servermanager.Fetch(simplififedPersistenceDiagram)
# Get the number of persistent points and arcs
num_persistent_threshold_points = simplififedPersistenceDiagram.GetDataInformation().GetNumberOfPoints()

for index in range(num_persistent_threshold_points):
	vertex_id = persistence_threshold_data.GetPointData().GetArray('VertexIdentifier').GetValue(index)

	# If index is even, we are processing death; else just store attributes of birth
	# When death occurs, find persistence and moksha.
	if index & 1:
		death_vertex = vertex_id
		content = [birth_vertex, death_vertex]
		writer.writerow(content)

		# add to pairs dictionary
		# I store only one instance and not the death
		if (birth_vertex in scalars.keys()) and (death_vertex in scalars.keys()):
			birth_pairs[birth_vertex] = death_vertex

	else:
		birth_vertex = vertex_id

pairs_file.close()

# Write the persistence diagram after thresholding of only the super/sub level-set [for usage by TDA]
pairs_file_arguments = [tree_type, PAIRS_INFIX, file_name, CSV_EXTENSION]
pairs_file_path = get_output_path(file_path, pairs_file_arguments, folder_name = PERSISTENCE_FOLDER)

pairs_file = open(pairs_file_path, 'w')
fieldnames = ['dimension', 'Death', 'Birth']
writer = csv.writer(pairs_file, delimiter=',')
writer.writerow(fieldnames)
birth_vertex = None
birth_scalar = None
write_row = True

# The persistent pairs are one after the other
# First comes birth; immediately followed by death [Adhitya getting philosophical :P]

# Iterate over all the points in the persistent diagram
persistence_threshold_data = servermanager.Fetch(simplififedPersistenceDiagram)
# Get the number of persistent points and arcs
num_persistent_threshold_points = simplififedPersistenceDiagram.GetDataInformation().GetNumberOfPoints()

# Iterate across all points in diagram and write persistent pairs
for index in range(num_persistent_threshold_points):
	vertex_id = persistence_threshold_data.GetPointData().GetArray('VertexIdentifier').GetValue(index)
	try:
		vertex_scalar = scalars[vertex_id]
		if index & 1:
			death_vertex = vertex_id
			death_scalar = vertex_scalar
			# There exist values which are not present in the merge-tree
			if write_row:
				content = [0, round(death_scalar,4), round(birth_scalar,4)]
				writer.writerow(content)
			write_row = True
		else:
			birth_vertex = vertex_id
			birth_scalar = vertex_scalar
			write_row = True
	except:
		# This row contains a value not present in the merge-tree
		write_row = False
		pass

pairs_file.close()

# take screenshot of scalar field
screen_file_arguments = [tree_type, SCREENSHOT_INFIX, file_name, PNG_EXTENSION]
screen_file_path = get_output_path(file_path, screen_file_arguments, folder_name = SCREENSHOT_FOLDER)
SaveScreenshot(screen_file_path, magnification=1, quality=100, view=renderView1)

print datetime.now() - startTime, 'Done! :)'


# Start marching! :)

# simulation of simplices for nodes in the tree
sorted_nodes = list(reversed([v[0] for v in sorted(scalars.iteritems(), key=lambda(k, v): (-v, -k))]))

# sort the nodes associated with each arc node
# the sorting is based on simulation of simplices
for node in sorted_nodes:
	arcs[node] = list(reversed(sorted(arcs[node], key= lambda x: -sorted_nodes.index(x))))
	#print node, arcs[node]

# retain only super-arcs
# only retain the nodes that are indiced higher in the above ordering
for node in sorted_nodes:
	arcs[node][:] = [arc_node for arc_node in arcs[node] if sorted_nodes.index(arc_node) > sorted_nodes.index(node)]

for node in sorted_nodes:
	if arcs[node]:
		print node, arcs[node]

# fetch the list of vertices and cells from the Domain
# use them for hashing
simplificationData = servermanager.Fetch(topologicalSimplification)
numTriangles = simplificationData.GetNumberOfCells()
numPoints = simplificationData.GetNumberOfPoints()

cell_indices = {}
point_coordinates = {}
point_scalars = {}

for cell_index in xrange(numTriangles):
	# process every cell and get the identifiers of each point
	cell = simplificationData.GetCell(cell_index)
	point1 = cell.GetPointId(0)
	point2 = cell.GetPointId(1)
	point3 = cell.GetPointId(2)

	# get the coordinates of each point of the cell
	coordinate1 = simplificationData.GetPoint(point1)
	coordinate2 = simplificationData.GetPoint(point2)
	coordinate3 = simplificationData.GetPoint(point3)

	# hash the cell points together for comparison later
	cell_points = frozenset([point1, point2, point3])
	cell_indices[cell_points] = cell_index

	# hash the coordinates to PointID
	point_coordinates[coordinate1] = point1
	point_coordinates[coordinate2] = point2
	point_coordinates[coordinate3] = point3

# similarly iterate over all points in the surface and store their scalar values
for point_index in xrange(numPoints):
	point_scalar = simplificationData.GetPointData().GetArray('magnitude').GetValue(point_index)
	point_scalars[point_index] = point_scalar


# process the link
triangulationData = servermanager.Fetch(triangulationRequest)
numTriangulationPoints = triangulationData.GetNumberOfPoints()
for index in xrange(1, numTriangulationPoints):

	# each triangle is connected as simplex - previous - current
	# NO, it is not connected so!! Instead of using points, use the cells instead
	previous_point = triangulationData.GetPoint(index-1)
	current_point = triangulationData.GetPoint(index)

	# get the identifiers of each cell in the link
	simplex_point_identifier = triangulationRequest.Simplexidentifier
	previous_point_identifier = point_coordinates[previous_point]
	current_point_identifier = point_coordinates[current_point]

	# map all the indices to a cell
	cell_points = frozenset([simplex_point_identifier, previous_point_identifier, current_point_identifier])

	# find the scalar values for each point of the cell
	simplex_scalar = point_scalars[simplex_point_identifier]
	previous_scalar = point_scalars[previous_point_identifier]
	current_scalar = point_scalars[current_point_identifier]

	# add the vertex of the other connected component here

	print cell_indices[cell_points], simplex_scalar, previous_scalar, current_scalar

#os._exit(0)
