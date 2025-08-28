from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
	x: int
	y: int


if __name__ == "__main__":
	p = Point(1, 2)
	print(p)

	# p.x = 10  # Error
	#
	# p.__setattr__("x", 2)  # Error

	# Updating the value of Frozen Instance of Point, p
	object.__setattr__(p, "x", 42)
	print(p)
