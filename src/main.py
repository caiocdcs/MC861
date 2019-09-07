import sys
from cpu import CPU

def main():

	# Check if there's a parameter
	if (len(sys.argv) != 2):
		print ("Provide a .nes file\n")
		return

	c = CPU(sys.argv[1])
	c.run()

if __name__ == "__main__":
    main()
