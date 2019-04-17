#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 09:06:09 2019

@author: mulya
"""
import binascii
from Cryptodome.Cipher import AES
MODE = AES.MODE_CFB
BLOCK_SIZE = 16
SEGMENT_SIZE = 128
padding = '\x00'        #to match the zero padding at javascript

def encrypt(plaintext, key, iv):
    aes = AES.new(key.encode(), MODE, iv.encode(), segment_size=SEGMENT_SIZE)
    plaintext = _pad_string(plaintext)
    encrypted_text = aes.encrypt(plaintext.encode())
    return binascii.b2a_hex(encrypted_text).rstrip().decode()

def decrypt(encrypted_text, key, iv):
    aes = AES.new(key.encode(), MODE, iv.encode(), segment_size=SEGMENT_SIZE)
    encrypted_text_bytes = binascii.a2b_hex(encrypted_text)
    decrypted_text = aes.decrypt(encrypted_text_bytes)
    decrypted_text = _unpad_string(decrypted_text).decode()
    return decrypted_text

def _pad_string(value):
    length = len(value)
    pad_size = BLOCK_SIZE - (length % BLOCK_SIZE)
    return value.ljust(length + pad_size, padding)

def _unpad_string(value):
    while value[-1] == 0x00:
        value = value[:-1]
    return value