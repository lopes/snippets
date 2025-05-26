#!/usr/bin/python
# DATE: 2015-11-15

from Crypto.Cipher import AES
from Crypto.Util import Counter

key = bytes.fromhex('36f18357be4dbd77f050515c73fcf9f2')
ciphertext = bytes.fromhex('69dda8455c7dd4254bf353b773304eec0ec7702330098ce7f7520d1cbbb20fc388d1b0adb5054dbd7370849dbf0b88d393f252e764f1f5f7ad97ef79d59ce29f5f51eeca32eabedd9afa9329')
iv     = ciphertext[:16]  #not needed for CTR, mult. of 16
cipher = ciphertext[16:]

mode = AES.MODE_CTR#CBC
counter = Counter.new(256, prefix=iv)#, initial_value=int('69dda8455c7dd425', 16))

decryptor = AES.new(key, mode, iv, counter=counter)
plain = decryptor.decrypt(cipher)
print(plain.decode('utf-8'))
