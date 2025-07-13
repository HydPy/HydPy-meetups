class FunnySet(set):
	def __getitem__(self, index):
		if index < 0:
			index += len(self)
		for i, item in enumerate(self):
			if i == index:
				return item

		raise IndexError("Index out of range")


if __name__ == '__main__':
	fset = FunnySet()
	fset.add("apple")
	fset.add("banana")
	fset.add("cherry")
	fset.add("mango")

	# Indexed, but not ordered.
	print(fset)
	print(fset[0], fset[1], fset[2], fset[3])
	print(fset[-1])

	print(fset[10])

	# print(fset[1: 3])  # slicing is not implemented in above class