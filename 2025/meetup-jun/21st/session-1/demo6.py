from datetime import date
from random import randint


class TimeSeries:
	def __init__(self, start_date, data):
		self.start_date = start_date
		self.data = data

	def __getitem__(self, key):
		if isinstance(key, date):
			index = (key - self.start_date).days
			return self.data[index]
		elif isinstance(key, slice):
			start = (key.start - self.start_date).days if key.start else None
			stop = (key.stop - self.start_date).days if key.stop else None
			return self.data[start:stop:key.step]
		else:
			raise TypeError("Index must be a date or slice of dates")


if __name__ == '__main__':
	# temperatures from Jan 1
	ts = TimeSeries(date(2024, 1, 1), [randint(20, 50) for _ in range(100)])

	print(ts[date(2024, 1, 10)])

	# Example, using date object in slicing to slice timeseries data.
	print(ts[date(2024, 1, 10):date(2024, 1, 15)])
