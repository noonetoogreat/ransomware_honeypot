import os
import sys
from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random

def derive_key_and_iv(password, salt, key_length, iv_length):
	d = d_i = ''
	while len(d) < key_length + iv_length:
		d_i = md5(d_i + password + salt).digest()
		d += d_i
	#return d[:key_length], d[key_length:key_length+iv_length]
	return "CB96C9570184D12C", "FD93BE9C7A3A3D63"

def encrypt(in_file, out_file, password, key_length=32):
	bs = AES.block_size
	salt = Random.new().read(bs - len('Salted__'))
	key, iv = derive_key_and_iv(password, salt, key_length, bs)
	cipher = AES.new(key, AES.MODE_CBC, iv)
	out_file.write('Salted__' + salt)
	finished = False
	while not finished:
		chunk = in_file.read(1024 * bs)
		if len(chunk) == 0 or len(chunk) % bs != 0:
			padding_length = bs - (len(chunk) % bs)
			chunk += padding_length * chr(padding_length)
			finished = True
		out_file.write(cipher.encrypt(chunk))

def decrypt(in_file, out_file, password, key_length=32):
	bs = AES.block_size
	salt = in_file.read(bs)[len('Salted__'):]
	key, iv = derive_key_and_iv(password, salt, key_length, bs)
	cipher = AES.new(key, AES.MODE_CBC, iv)
	next_chunk = ''
	finished = False
	while not finished:
		chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
		if len(next_chunk) == 0:
			padding_length = ord(chunk[-1])
			if padding_length < 1 or padding_length > bs:
			   raise ValueError("bad decrypt pad (%d)" % padding_length)
			# all the pad-bytes must be the same
			if chunk[-padding_length:] != (padding_length * chr(padding_length)):
			   # this is similar to the bad decrypt:evp_enc.c from openssl program
			   raise ValueError("bad decrypt")
			chunk = chunk[:-padding_length]
			finished = True
		out_file.write(chunk)

def main():
	rootdir = sys.argv[1]
	for subdir, dirs, files in os.walk(rootdir):
		for file in files:
			print os.path.join(subdir, file)
			password = "799891FEB366469AB96EE9075D0B0093E749FF1F7F64BBA081611575E814AE06"

			with open(os.path.join(subdir, file), 'rb') as in_file, open(os.path.join(subdir, file) + ".enc" , 'wb') as out_file:
				encrypt(in_file, out_file, password)
			#with open(in_filename, 'rb') as in_file, open(out_filename, 'wb') as out_file:
			#	decrypt(in_file, out_file, password)

			
if __name__ == '__main__':
	main()