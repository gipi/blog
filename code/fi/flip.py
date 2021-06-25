import sys

MOV_R0_R0 = 0b0010110000000000


def dump(x):
    sys.stdout.buffer.write(bin2bytes(x))


def bin2bytes(x):
    return x.to_bytes(2, byteorder='little')


def flipbit(x, n):
    '''flip n-th bit of x'''
    mask = 1 << n
    return x ^ mask


if __name__ == '__main__':
    dump(MOV_R0_R0)
    for idx in range(16):
        dump(flipbit(MOV_R0_R0, idx))
