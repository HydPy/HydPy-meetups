def my_generator():
	print("Generator started...")
	i = 0
	while True:
		yield i
		i += 1


def generator_with_message():
	print("Generator started... Awaiting message...")
	i = 0
	while True:
		message = yield i
		print(f"Message received: {message}")
		i += 1


if __name__ == "__main__":
	# demo to show message sending in generator.
	gen1 = my_generator()
	print(next(gen1))
	print(next(gen1))
	print(next(gen1))
	print(next(gen1))

	gen2 = generator_with_message()
	print(next(gen2))
	gen2.send("Hello")
	# print(next(gen2))
	gen2.send("How are you?")
	# print(next(gen2))
	gen2.send("Goodbye")

	gen1.close()
	gen2.close()
