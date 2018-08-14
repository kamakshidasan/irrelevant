# point: segment
processed_points = {}
# triangle: segment
processed_triangles = {}

# need to have a loop over the arcs here
# reversed is not probably not necessary
# I'm just being extra careful to process from the global maximum to global minimum
for current_critical in reversed(sorted_nodes):
    # the arcs are already sorted
    # next_critical refers to the next lower critical point in the merge tree
    for next_critical in arcs[current_critical]:
        print current_critical, next_critical

        # add the current critical point to the processing list
        current_processing_points = [current_critical]

        # process all points between current_critical and next_critical
        while len(current_processing_points > 0):

            # process the first element of the processing list
            simplex_point_identifier = current_processing_points.pop(0)
            triangulationRequest.Simplexidentifier = simplex_point_identifier
            renderView1.Update()
            # ask results back from TTK
            triangulationData = servermanager.Fetch(triangulationRequest)

            # find the number of lines connected to the 1-simplex in the link
            num_link_lines = triangulationData.GetNumberOfCells()
            # process all lines in the link
        	for index in xrange(num_link_lines):
                # In VTK's indexing module, a line is identified as birectional
                # so even if one direction of a line has been processed
                # the other might not have been, so I can't have a check here

                current_line = triangulationData.GetCell(index)

                # get the coordinates of the points from the line
                previous_point = current_line.GetPoints().GetPoint(0)
                next_point = current_line.GetPoints().GetPoint(1)

                # get the identifiers of each cell in the link
                # they have been hashed earlier
                previous_point_identifier = point_coordinates[previous_point]
                next_point_identifier = point_coordinates[next_point]

                # make the above identifiers into a triangle
                # frozenset helps in making the triangle cyclic
                cell_points = frozenset([simplex_point_identifier, previous_point_identifier, next_point_identifier])

                # global triangle indices have already been hashed
                current_triangle_index = triangle_indices[cell_points]

                # check if triangle was already processed earlier
                # this check can happen thrice per triangle [one for each vertex]
                if current_triangle_index not in processed_triangles:
                    # find the scalar values for each point of the cell
                    simplex_scalar = point_scalars[simplex_point_identifier]
                    previous_scalar = point_scalars[previous_point_identifier]
                    next_scalar = point_scalars[next_point_identifier]

                    # find the lower and upper bounds of the current isoband
                    lower_scalar_bound = point_scalars[current_critical]
                    upper_scalar_bound = point_scalars[next_critical]

                    print 'lower_scalar_bound', lower_scalar_bound
                    print 'higher_scalar_bound', upper_scalar_bound

                    # find if this point is lower/equal/upper than the bounds
                    first = calculate_isoband_index(simplex_scalar, lower_scalar_bound, upper_scalar_bound)
                    second = calculate_isoband_index(previous_scalar, lower_scalar_bound, upper_scalar_bound)
                    third = calculate_isoband_index(next_scalar, lower_scalar_bound, upper_scalar_bound)

                    # concatenate above values for finding an index for the triangle
                    isoband_value = first + second + third

                    # check if the isoband passes through the triangle
                    if ((isoband_value in lower_intolerable_indices) or (isoband_value in upper_intolerable_indices)):
                        print simplex_scalar, previous_scalar, next_scalar
                        print 'The face', current_triangle, 'is not part of the segmentation', isoband_value
                    else:
                        print simplex_scalar, previous_scalar, next_scalar
                        print 'The face', current_triangle, 'is part of the segmentation', isoband_value

                    # make sure k-simplices are not processed again
                    # make sure the links for these points haven't already been computed
                    # if the triangle was processed earlier, then it's points would have been already added to the list
                    if previous_point_identifier not in processed_points:
                        current_processing_points.append(previous_point_identifier)
                    if next_point_identifier not in processed_points:
                        current_processing_points.append(next_point_identifier)
                    processed_triangles[current_triangle_index] = current_critical

            # add the current 0-simplex to the processed dataset
            processed_points[simplex_point_identifier] = current_critical

# invert the processed_triangles
# each key of this dictionary will have a list
# that will have all triangles in it's segmentation
processed_critical_points = dict((v, [k for (k, xx) in filter(lambda (key, value): value == v, processed_triangles.items())]) for v in set(processed_triangles.values()))

print 'Yes we can'
for critical_point in processed_critical_points.keys():
    print critical_point, len(processed_critical_points[critical_point])
