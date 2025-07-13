import ctypes

t = (1, 2, 3)
print(t)
print(id(t))

# Get address of tuple items
addr = id(t) + (len(t) * ctypes.sizeof(ctypes.c_ssize_t))

# Access PyObject* array
array_type = ctypes.py_object * len(t)
array = array_type.from_address(addr)

# Change the first element
array[0] = 42

print(t)
print(id(t))


# Learning?
# Python stores data in mutable memory structures underneath
# Python's immutability i`s a high-level contract, not an unbreakable rule.