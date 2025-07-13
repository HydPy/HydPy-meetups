def rolling_avg():
	total = 0
	count = 0
	avg = 0
	while True:
		num = yield avg
		total += num or 0
		count += 1
		avg = total / count
		print(f"count - {count}, number - {num}, Total - {total}, avg - {avg}")


acc = rolling_avg()
print(next(acc))
for i in range(1, 10):
	print(acc.send(i))
