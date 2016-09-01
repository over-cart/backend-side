def listToNum(numList):
	num = 0
	for i in range(0,len(numList)):
		if numList[i] > 255:
			numList[i] = 255
		elif numList[i] < 0:
			numList[i] = 0
		num += numList[i] << 8*i
	return num

def numToList(num,size=16):
	l = []
	mask = 0xFF
	for i in range(0,size):
		l.append(int((num & (mask << 8*i)) >> 8*i))
	return l

s = input()
l = numToList(s)
print(l)
print(listToNum(l))
