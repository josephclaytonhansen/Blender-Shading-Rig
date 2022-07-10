    #experimental - delete once the better way works
    working_empty_pos_array = []
    working_light_rot_array = []
    
    for entry in g.light_rot_array:
        
        #experimental
        #This clears, in a sense- if you set eframes for EditA, and select EditA, editA will move on the corresponding eframes.
        #It works on an individual basis, just not for all edits at once. 
        if bpy.data.scenes["Scene"].empty_objects == g.eframe_to_edit[i]:
            working_empty_pos_array.append(g.empty_pos_array[i])
            working_light_rot_array.append(g.light_rot_array[i])
            
        
        i +=1
        
        #experimental
        if bpy.data.scenes["Scene"].empty_objects == g.eframe_to_edit[i]:
        #get distances from active point to other points:
            g.distances[i] = round(distance(g.active_point, entry),6)
            
            #invert distances:
            try:
                g.inverse_distances[i] = round((1/distance(g.active_point, entry)),6)
            except:
                g.inverse_distances[i] = 0
        
        #calculate sum of total inverse distances:
        g.total_inverse_distances = sum(g.inverse_distances)
        #divide 100 by that, and multiply each distance by the result:
        g.working_multiplier = 100 / g.total_inverse_distances
        g.multiplied_distances[i] = g.inverse_distances[i] * g.working_multiplier
    
    
    #LERP testing
    final_pos = [0,0,0]

    entry_index = -1

    for entry in working_empty_pos_array:
        entry_index += 1
        axis_index = -1

        for axis in entry:
            axis_index += 1
            final_pos[axis_index] += round((round((g.multiplied_distances[entry_index] /100),2) * axis),6)
    g.final_pos = final_pos

    print("Placeable: ", g.placeable, "\nFinal pos: ", g.final_pos)
    
    if not g.placeable and g.final_pos != [0,0,0]:
        bpy.data.objects[bpy.data.scenes["Scene"].empty_objects.name].location = g.final_pos
    #end LERP
    
    #save globals to a custom property
    
    #This no longer works!!! 
    
#    bpy.data.objects["EditA"]["light_rot"] = str(json.loads(str(g.light_rot_array)))
#    bpy.data.objects["EditA"]["empty_pos"] = str(json.loads(str(g.empty_pos_array)))