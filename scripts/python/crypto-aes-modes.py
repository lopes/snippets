#!/usr/bin/env python3
#
# Simple examples on using different block cipher modes
# of operation (NIST SP 800-38A) with AES.
#
# Warning: this script is just an example!  You must be
# very confident on your work (or insane) to implement
# this kind of code in production, because it's safer
# to use wide tested frameworks like PyNaCl.
#
#
# USAGE
# Before running this script, you must install PyCryptodome:
#
# $ python -m pip install pycryptodome
#
# Then, uncomment the appropriate line according to the
# mode you want to test (default is CBC) and run this
# script.  Start typing a (M)essage and a (P)assword and
# you'll get a (C)iphertext.  After that, copy and paste C,
# and type P again, so you should have M:
#
# C = AES.encrypt(M, P)
# M = AES.decrypt(C, P)
#
#
# Author.: José Lopes
# Date...: 2020-03-07
# License: MIT
##


from base64 import b64encode, b64decode

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


encoding = 'utf-8'
salt = b64encode(get_random_bytes(512))
key = lambda k: PBKDF2(k, salt, AES.block_size, hmac_hash_module=SHA256)


class ECB(object):
    def enc(self, m, k):
        cipher = AES.new(key(k), AES.MODE_ECB)
        return b64encode(cipher.encrypt(pad(m.encode(encoding),
            AES.block_size)))
    def dec(self, c, k):
        raw = b64decode(c)
        cipher = AES.new(key(k), AES.MODE_ECB)
        return unpad(cipher.decrypt(raw), AES.block_size)

class CBC(object):
    def enc(self, m, k):
        cipher = AES.new(key(k), AES.MODE_CBC)
        return b64encode(cipher.iv + cipher.encrypt(pad(m.encode(encoding),
            AES.block_size)))
    def dec(self, c, k):
        raw = b64decode(c)
        cipher = AES.new(key(k), AES.MODE_CBC, raw[:AES.block_size])
        return unpad(cipher.decrypt(raw[AES.block_size:]), AES.block_size)

class CTR(object):
    def enc(self, m, k):
        cipher = AES.new(key(k), AES.MODE_CTR, nonce=salt[:AES.block_size - 1])
        return b64encode(cipher.nonce + cipher.encrypt(m.encode(encoding)))
    def dec(self, c, k):
        raw = b64decode(c)
        cipher = AES.new(key(k), AES.MODE_CTR, nonce=raw[:AES.block_size - 1])
        return cipher.decrypt(raw[AES.block_size - 1:])

class CFB(object):
    def enc(self, m, k):
        cipher = AES.new(key(k), AES.MODE_CFB)
        return b64encode(cipher.iv + cipher.encrypt(m.encode(encoding)))
    def dec(self, m, k):
        raw = b64decode(c)
        cipher = AES.new(key(k), AES.MODE_CFB, iv=raw[:AES.block_size])
        return cipher.decrypt(raw[AES.block_size:])

class OFB(object):
    def enc(self, m, k):
        cipher = AES.new(key(k), AES.MODE_OFB)
        return b64encode(cipher.iv + cipher.encrypt(m.encode(encoding)))
    def dec(self, c, k):
        raw = b64decode(c)
        cipher = AES.new(key(k), AES.MODE_OFB, iv=raw[:AES.block_size])
        return cipher.decrypt(raw[AES.block_size:])


if __name__ == '__main__':
    # mode = ECB()
    mode = CBC()
    # mode = CTR()
    # mode = CFB()
    # mode = OFB()

    print('\n\nTESTING ENCRYPTION')
    m = input('Message...: ')
    k = input('Password..: ')
    print('Ciphertext:', mode.enc(m, k).decode(encoding))

    print('\nTESTING DECRYPTION')
    c = input('Ciphertext: ')
    k = input('Password..: ')
    print('Message...:', mode.dec(c, k).decode(encoding),'\n\n')
