class FunnySet(set):
	def __getitem__(self, index):
		if isinstance(index, int):
			if index < 0:
				index += len(self)
			for i, item in enumerate(self):
				if i == index:
					return item
			raise IndexError("Index out of range")

		elif isinstance(index, slice):
			items = []
			for i, item in enumerate(self):
				if i >= (index.start or 0) and (index.stop is None or i < index.stop):
					if index.step is None or (i - (index.start or 0)) % index.step == 0:
						items.append(item)
			return items
		else:
			raise TypeError("Invalid index type")


if __name__ == '__main__':
	fset = FunnySet()
	fset.add("apple")
	fset.add("banana")
	fset.add("cherry")
	fset.add("mango")

	print(fset)
	print(fset[0], fset[1], fset[2], fset[3])
	print(fset[-1])

	# print(fset[10])

	# Slicing
	print(fset[1: 3])  # Slicing implemented.
