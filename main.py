import sys

def main():

	if (len(sys.argv) != 2):
		print ("Provide a .nes file\n")
		return

	file = open(sys.argv[1], "rb")

	byte = file.read(1).hex()

	while byte:
		print(byte)
		byte = file.read(1).hex()

if __name__ == "__main__":
    main()
