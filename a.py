
def is_subsequence(list, sequence):
	is_subset = False
	if sequence == []:
		is_subset = True
	elif sequence == list:
		is_subset = True
	elif len(sequence) > len(list):
		is_subset = False
	else:
		for i in range(len(list)):
			if list[i] == sequence[0]:
				n = 1
				while (n < len(sequence)) and (list[i+n] == sequence[n]):
					n += 1
				if n == len(sequence):
					indices.append(i)
	return is_subset