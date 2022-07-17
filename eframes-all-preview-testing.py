import math, json

object_array = ["Sphere", "Cube", "Cube", "Cube", "Cube", "Cube", "Sphere", "Sphere"]
list1 = ["EditC", "EditB", "EditA", "EditA", "EditC", "EditB", "EditB", "EditC"]
holding_empty_pos = [[85, 85, 50], [32, 54, 81], [88, 62, 82], [81, 30, 12], [43, 66, 72], [66, 6, 32], [13, 50, 72], [61, 20, 89]]
holding_light_rot = [[143, 2, 150], [49, 71, 166], [44, 136, 74], [172, 77, 11], [66, 102, 53], [36, 161, 62], [43, 69, 54], [42, 69, 97]]
potentials = ["EditA", "EditB", "EditC", "EditD", "EditE", "EditF", "EditG", "EditH"]

active_point = [75, 151, 55]

class Globals():
    all_light_rot_arrays = {}
    all_empty_pos_arrays = {}
    all_eframe_edit_names = {}
    all_objects = ["Cube", "Sphere"]
    
g = Globals()

def distance(p1, p2):
    #calculate 3D distance
    d = math.sqrt(
        (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2
        )
    return d

def convert_full_eframes_array_to_edit_seperated_array(edits, light_rot, eframes, all_edits, all_objects, objects):
    #this has object filtering now, but it is NASTY performance-wise. (Hence why this only runs when
    #adding a new eframe or clearing e-frames). The resulting array is 4D at the deepest point-
    #for example, c[0]["Cube"]["EditB"][0] is a perfectly reasonable query.
    
    #This has NOT been implemented into main.py, but it clears on its own

    used_potentials = []
    splits_array_empty_pos = {}
    splits_array_light_rot = {}

    for j in range(0, len(all_objects)):
        for l in range(0, len(objects)):
            if objects[l] == all_objects[j]:
                for x in range(0, len(all_edits)):
                    for y in range(0, len(edits)):
                        if all_edits[x] == edits[y]:
                            if l == y:
                                if objects[l] not in splits_array_empty_pos:
                                    splits_array_empty_pos[objects[l]] = {}
                                if all_edits[x] not in splits_array_empty_pos[objects[l]]:
                                    splits_array_empty_pos[objects[l]][all_edits[x]] = []
                                splits_array_empty_pos[objects[l]][all_edits[x]].append(eframes[y])
                                
                                if objects[l] not in splits_array_light_rot:
                                    splits_array_light_rot[objects[l]] = {}
                                if all_edits[x] not in splits_array_light_rot[objects[l]]:
                                    splits_array_light_rot[objects[l]][all_edits[x]] = []
                                splits_array_light_rot[objects[l]][all_edits[x]].append(light_rot[y])

                                if all_edits[x] not in used_potentials:
                                    used_potentials.append(all_edits[x])
        
    #How does this work? I don't know. Please let me know if you figure it out. 
    c = [splits_array_empty_pos, splits_array_light_rot, used_potentials]
    return c

c = convert_full_eframes_array_to_edit_seperated_array(list1, holding_light_rot, holding_empty_pos, potentials, g.all_objects, object_array)
g.all_empty_pos_arrays, g.all_light_rot_arrays, used_potentials = c[0], c[1], c[2]


