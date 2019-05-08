# -*- coding: utf-8 -*-

'''
620031587
Net-Centric Computing Assignment
Part A - RSA Encryption
'''

import random
import math

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

def generate_keypair(p, q):
    if not (is_prime(p) and is_prime(q)):
        raise ValueError('Both numbers must be prime.')
    elif p == q:
        raise ValueError('p and q cannot be equal')
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
        sO = str(ord(char))
        messageVal += '0' * (3 - len(sO)) + sO

    messageVal = int("1" + messageVal)

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

    messVal = str(messVal)[1:]
    for n in range(0, len(messVal), 3):
        plain += chr(int(messVal[n:n + 3]))

    #plain = [chr(pow(char, key, n)) for char in ciphertext]
    #Return the array of bytes as a string
    return plain

def generate_keypair_input():
    p = int(input("Enter a prime number: "))
    q = int(input("Enter a bigger prime number: "))

    public, private = generate_keypair(p, q)

    print("Your public key is {} and your private key is {}".format(public, private))
