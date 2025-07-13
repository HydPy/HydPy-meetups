import hashlib

class FunnyList(list):
	def __hash__(self):
		data = str(self).encode()
		hash_value = hashlib.md5(data).hexdigest()
		ascii_chars = [str(ord(char)) for char in hash_value]
		return int("".join(ascii_chars))

	def __eq__(self, other):
		return hash(self) == hash(other)


if __name__ == "__main__":
	fl = FunnyList()
	fl.append(10)
	fl.append(20)
	fl.append(30)
	fl.append(40)

	# Hashable list that can be made key in dict.
	d = {fl: "foo"}
	print(d)