import sys
while True:
	f = open(sys.argv[1], 'w')
	f.write("lorem ipsum")
	f.close()