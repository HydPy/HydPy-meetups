class OrderedSet(set):
	def __init__(self, iterable=None):
		super().__init__()
		self._order = []
		if iterable:
			for item in iterable:
				self.add(item)

	def add(self, item):
		if item not in self:
			super().add(item)
			self._order.append(item)

	def remove(self, item):
		if item in self:
			super().remove(item)
			self._order.remove(item)

	def pop(self):
		if not self:
			return None

		self._order.pop()
		return super().pop()

	def __getitem__(self, index):
		return self._order[index]

	def __iter__(self):
		return iter(self._order)

	def __repr__(self):
		return f"OrderedSet({self._order})"


if __name__ == '__main__':
	oset = OrderedSet()
	oset.add("apple")
	oset.add("banana")
	oset.add("cherry")
	oset.add("mango")

	print(oset)

	# Preserved Order
	print(oset[0], oset[1], oset[2], oset[3])
	print(oset[-1])
