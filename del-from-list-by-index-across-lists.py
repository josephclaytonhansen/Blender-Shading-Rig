list1 = ["a", "b", "c", "c", "c", "a", "b", "a", "c", "a"]
list2 = [0,1,2,3,4,5,6,7,8,9]
list3 = ["a", "b", "c", "c", "c", "a", "b", "a", "c", "a"]

el1 = ["a", "b", "a", "b", "a", "a"]
el2 = [0,1,5,6,7,9]

i = -1
dels = []
for entry in list1:
    i += 1
    if entry == "c":
        dels.append(i)

dels = set(dels)
print(dels)

removed1 = [ value for (j, value) in enumerate(list1) if j not in set(dels) ]
removed2 = [ value for (k, value) in enumerate(list2) if k not in set(dels) ]
removed3 = [ value for (l, value) in enumerate(list3) if l not in set(dels) ]
print(removed1, removed2, removed3)

print(el1,el2)
        