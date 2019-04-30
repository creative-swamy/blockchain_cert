import binascii
x = b'QmU6SXLad4498YhvynvvJmSfvvfZhLcFg8Jn9VdttXvhJw'
x = binascii.hexlify(x)
y = str(x, 'ascii')
print(y)
