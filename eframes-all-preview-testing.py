
from itertools import groupby

list1 = ["a", "b", "a", "b", "a", "b", "b", "a", "c"]
holding_empty_pos = [0, 0, 1, 1, 2, 2, 3, 3, 4]
holding_light_rot = [45, 60, 90, 30, 20, 70, 110, 50, 60]
potentials = ["a", "b", "c", "d", "e", "f", "g", "h"]


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
                splits_array_empty_pos[edits[y]] = working_saep
            if working_salr != []:
                splits_array_light_rot[edits[y]] = working_salr

    
    c = [splits_array_empty_pos, splits_array_light_rot]
    return c

c = convert_full_eframes_array_to_edit_seperated_array(list1, holding_light_rot, holding_empty_pos, potentials)
all_empty_pos, all_light_rot = c[0], c[1]
