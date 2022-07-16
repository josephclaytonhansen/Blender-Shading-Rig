import math

object_array = ["Cube", "Cube", "Cube", "Cube", "Cube", "Cube", "Sphere", "Sphere"]
list1 = ["a", "b", "a", "b", "c", "b", "b", "c"]
holding_empty_pos = [[85, 85, 50], [32, 54, 81], [88, 62, 82], [81, 30, 12], [43, 66, 72], [66, 6, 32], [13, 50, 72], [61, 20, 89]]
holding_light_rot = [[143, 2, 150], [49, 71, 166], [44, 136, 74], [172, 77, 11], [66, 102, 53], [36, 161, 62], [43, 69, 54], [42, 69, 97]]
potentials = ["a", "b", "c", "d", "e", "f", "g", "h"]

active_point = [75, 151, 55]

def distance(p1, p2):
    #calculate 3D distance
    d = math.sqrt(
        (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2
        )
    return d

def convert_full_eframes_array_to_edit_seperated_array(edits, light_rot, eframes, all_edits):
    splits_array_empty_pos = {}
    splits_array_light_rot = {}
    used_potentials = []
    
    for x in range(0, len(all_edits)):

        working_saep = []
        working_salr = []

        for y in range(0, len(edits)):
            if all_edits[x] == edits[y]:
                working_saep.append(eframes[y])
                working_salr.append(light_rot[y])
                if all_edits[x] not in used_potentials:
                    used_potentials.append(all_edits[x])
        
            if working_saep != []:
                splits_array_empty_pos[all_edits[x]] = working_saep
            if working_salr != []:
                splits_array_light_rot[all_edits[x]] = working_salr

    c = [splits_array_empty_pos, splits_array_light_rot, used_potentials]
    return c

c = convert_full_eframes_array_to_edit_seperated_array(list1, holding_light_rot, holding_empty_pos, potentials)
all_empty_pos, all_light_rot, used_potentials = c[0], c[1], c[2]
print(all_empty_pos, all_light_rot, used_potentials)

for edit in used_potentials:
    
    l = len(all_light_rot[edit])
    distances = [0] * l
    inverse_distances = [0] * l
    multiplied_distances = [0] * l
    
    i = -1
    
    for point in all_light_rot[edit]:
        i += 1

        distances[i] = distance(active_point, point)
        inverse_distances[i] = round((1/distances[i]),6)
    
    y = -1
    for point in all_light_rot[edit]:
        y += 1
        total_inverse_distances = sum(inverse_distances)
        working_multiplier = 100 / total_inverse_distances
        
        multiplied_distances[y] = inverse_distances[y] * working_multiplier
        print(multiplied_distances)
    
    #LERP testing
    final_pos = [0,0,0]

    entry_index = -1

    for entry in all_empty_pos[edit]:
        entry_index += 1
        axis_index = -1

        for axis in entry:
            axis_index += 1
            final_pos[axis_index] += round((round((multiplied_distances[entry_index] /100),2) * axis),6)


    print(edit, final_pos)

