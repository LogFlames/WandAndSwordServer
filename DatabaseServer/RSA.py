# -*- coding: utf-8 -*-

'''
620031587
Net-Centric Computing Assignment
Part A - RSA Encryption
'''

import random
import math

lettersAlowed = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!#€%&/()[]{}<>.,:;-_+?@*|=£$êîéèôç^' ")

def small_ord(char):
    for index, ch in enumerate(lettersAlowed):
        if char == ch:
            return index + 1
    return 1

def small_chr(inex):
    inex -= 1
    if inex < 0 or inex >= len(lettersAlowed):
        return lettersAlowed[0]
    return lettersAlowed[inex]

'''
Euclid's extended algorithm for finding the multiplicative inverse of two numbers
'''
def multiplicative_inverse(a, b):
    """Returns a tuple (r, i, j) such that r = math.gcd(a, b) = ia + jb
    """
    # r = math.gcd(a,b) i = multiplicitive inverse of a mod b
    #      or      j = multiplicitive inverse of b mod a
    # Neg return values for i or j are made positive mod b or a respectively
    # Iterateive Version is faster and uses much less stack space
    x = 0
    y = 1
    lx = 1
    ly = 0
    oa = a  # Remember original a/b to remove
    ob = b  # negative values from return results
    while b != 0:
        q = a // b
        (a, b) = (b, a % b)
        (x, lx) = ((lx - (q * x)), x)
        (y, ly) = ((ly - (q * y)), y)
    if lx < 0:
        lx += ob  # If neg wrap modulo orignal b
    if ly < 0:
        ly += oa  # If neg wrap modulo orignal a
    # return a , lx, ly  # Return only positive values
    return lx
'''
Tests to see if a number is prime.
'''
def is_prime(num):
    if num == 2:
        return True
    if num < 2 or num % 2 == 0:
        return False
    for n in range(3, int(math.sqrt(num)) + 2, 2):
        if num % n == 0:
            return False
    return True

def get_smallest_div(num):
    if num < 2:
        return 1
    if num % 2 == 0:
        return 2
    for n in range(3, int(math.sqrt(num) + 1), 2):
        if num % n == 0:
            return n
    return 1

def generate_keypair(length=1024, k=128):
    a = -1
    b = -1
    while a == b:
        a = generate_prime_number(length, k)
        b = generate_prime_number(length, k)

    p = min(a, b)
    q = max(a, b)
    #n = pq
    n = p * q

    #Phi is the totient of n
    phi = (p - 1) * (q - 1)

    #Choose an integer e such that e and phi(n) are coprime
    e = random.randrange(1, phi)

    #Use Euclid's Algorithm to verify that e and phi(n) are comprime
    g = math.gcd(e, phi)
    while g != 1:
        e = random.randrange(1, phi)
        g = math.gcd(e, phi)

    #Use Extended Euclid's Algorithm to generate the private key
    d = multiplicative_inverse(e, phi)

    #Return public and private keypair
    #Public key is (e, n) and private key is (d, n)
    return ((e, n), (d, n))

def encrypt(pk, plaintext):
    #Unpack the key into it's components
    key, n = pk

    messageVal = ''

    for char in plaintext:
        sO = str(small_ord(char))
        messageVal += '0' * (2 - len(sO)) + sO

    messageVal = int(messageVal)

    cipher = pow(messageVal, key, n)

    #Convert each letter in the plaintext to numbers based on the character using a^b mod m
    #cipher = [pow(ord(char), key, n) for char in plaintext]
    #Return the array of bytes
    return cipher

def decrypt(pk, messVal):
    #Unpack the key into its components
    key, n = pk
    #Generate the plaintext based on the ciphertext and key using a^b mod m

    messVal = str(pow(messVal, key, n))

    plain = ''

    startInd = 0
    if len(messVal) % 2 == 1:
        plain += small_chr(int(messVal[0]))
        startInd = 1

    for n in range(startInd, len(messVal), 2):
        plain += small_chr(int(messVal[n:n + 2]))

    #plain = [chr(pow(char, key, n)) for char in ciphertext]
    #Return the array of bytes as a string
    return plain

def is_prime_aprox(n, k=128):
    """ Test if a number is prime
        Args:
            n -- int -- the number to test
            k -- int -- the number of tests to do
        return True if n is prime
    """
    # Test if n is not even.
    # But care, 2 is prime !
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    # find r and s
    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2
    # do k tests
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, r, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = pow(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True

def generate_prime_candidate(length):
    """ Generate an odd integer randomly
        Args:
            length -- int -- the length of the number to generate, in bits
        return a integer
    """
    # generate random bits
    p = random.getrandbits(length)
    # apply a mask to set MSB and LSB to 1
    p |= (1 << length - 1) | 1
    return p

def generate_prime_number(length=1024, k=128):
    """ Generate a prime
        Args:
            length -- int -- length of the prime to generate, in          bits
        return a prime
    """
    p = 4
    # keep generating while the primality test fail
    while not is_prime_aprox(p, k):
        p = generate_prime_candidate(length)
    return p

# Only used for testing when in terminal
# puk, prk = generate_keypair(512)
