from socket import socket, SOL_SOCKET, SO_REUSEADDR, MSG_WAITALL, SO_LINGER
import threading
import argparse
import time
import struct

parser = argparse.ArgumentParser()
parser.add_argument('--port', dest='port', default=9999, type=int, help='Specifies port to run on')
args = parser.parse_args()

bind_ip = "0.0.0.0"
bind_port = args.port

sock = socket()
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
#sock.setsockopt(SOL_SOCKET, SO_LINGER, struct.pack('ii', 1, 0))
sock.bind((bind_ip, bind_port))
sock.listen()

print(f"Listening on port {bind_ip} : {bind_port}")  

# TODO: return decoded
def decode_msg_in(csock, msg):
	peer = csock.getpeername()

def send_msg_out(csock, opcode, action_desc, msg_out):
	peer = csock.getpeername()

	print(f"{peer} Message out opcode 0x{opcode:x} '{action_desc}'")
	msg_len = len(msg_out)
	assert msg_len <= 0xff
	result = bytes([0, msg_len]) + msg_out
	assert len(result) == int.from_bytes(result[0:2], 'big') + 2
	assert opcode == int.from_bytes(result[2:6], 'big')
	csock.send(result)
	print(f"{peer} Send message {result}")

def handle_client(csock):
	peer = csock.getpeername()

	while True:
		msg_size_bytes = csock.recv(2, MSG_WAITALL)
		assert len(msg_size_bytes) == 2
		msg_size = int.from_bytes(msg_size_bytes, 'little') - 2
		print(f"{peer} Expect message of size {msg_size}")

		msg = csock.recv(msg_size, MSG_WAITALL)
		assert len(msg) == msg_size
		print(f"{peer} Recieved message {msg}")

		# Parse incoming message
		opcode = int.from_bytes(msg[:2], 'little')
		print(f"{peer} Message in opcode 0x{opcode:x}\n---")

		match opcode:
			# 0x3 -> 0x4
			# Keep-alive?
			case 0x3:
				assert msg_size+2 <= 0xff
				#csock.send(bytes([0, 8, 0, 0, 18, 5, 0, 0, 0, 0])
				#csock.send(bytes([8, 0, 3, 0, 36, 27, 68, 177])
				assert msg[1] == 0x0
				csock.send(bytes([msg_size+2, 0]) + bytes([4, 0]) + msg[2:])

			# 0x6 -> ?
			# First connection msg?
			case 0x6:
				x = bytes([
					7, 0, # opcode 0x7
						12, 0,
						49, 57, 50, 46, 49, 54, 56, 46, 49, 46, 55, 56, # str '192.168.1.78'
						14, 39, # LE short 9998
				])
				csock.send((len(x)+2).to_bytes(2, 'little') + x)

				# #  0x15c
				# x = b'\x0c\x15' + bytes([36, 27, 68, 177]) + (b'\x00' * 16)
				# csock.send(bytes([len(x)+2, 0]) + x)

			# 0x11 -> 0x12
			# Login?
			case 0x11:
				x = bytes([
					18, 0, # opcode 0x12
						1, 64, 0, 0, # 0x4001 response status or error? login OK?
						1, 0, 0, 0, # level? level 1
#						67, 79, 79, 76, 0, # 'COOL' null terminated
				])
				#x = b'\x12\x00\x03\x00abc\t\x00t-o-k-e-nA\x00\x00\x00\x0e\x00touchHLEdevice\x03\x00abc\x06\x001.0.1j\x00\x01\x00\x00\x00'
				#assert len(x)+2 <= 0xff
				csock.send((len(x)+2).to_bytes(2, 'little') + x)

			# 0x21 -> 0x22
			# Character creation?
			case 0x21:
				x = bytes([
					34, 0, # opcode 0x22
						1, 80, 0, 0, # 0x5001 response status OK?
				])
				#x = b'\x22\x00' + (b'\x00' * 100)
				#assert len(x)+2 <= 0xff
				csock.send((len(x)+2).to_bytes(2, 'little') + x)

			# case 0x4c:
			# 	x = bytes([
			# 		77, 0
			# 	])
			# 	csock.send((len(x)+2).to_bytes(2, 'little') + x)

			# case 0x52:
			# 	x = bytes([
			# 		83, 0
			# 	])
			# 	csock.send((len(x)+2).to_bytes(2, 'little') + x)

			# 0x23
			# Delete character ?

			# 0x25 -> 0x26
			# List Character?
			case 0x25:
				x = bytes([
					38, 0, # opcode 0x26
						1, 0, 0, 0, # characters count, 1
							1, 0, 0, 0, # character id, should match getusercharacter id from app.py
							1,
							1,
							1,
							1,
							3, 0, # chunk size 3
							115, 100, 102, # 'sdf' -> character name
				]) + (bytes([1, 0, 0, 0]) * 36)
				csock.send((len(x)+2).to_bytes(2, 'little') + x)

			# 0x27
			# PLAY ??
			case 0x27:
				x = bytes([
					0x28, 0, # opcode 0x28
						1, 64, 0, 0, # 0x4001 response status OK?
				]) \
				+ bytes([
						1, 0, 0, 0,
						1, 1, 1, 1,
						1, 0,
						1, 0, 0, 0,
						1, 0, 0, 0,
						1, 0, 0, 0,
				])
				# + bytes([
				# 		255, 255, 255, 255,
				# 		255, 255, 255, 255,
				# 		255, 255,
				# 		255, 255, 255, 255,
				# 		255, 255, 255, 255,
				# 		255, 255, 255, 255,
				# ])
				csock.send((len(x)+2).to_bytes(2, 'little') + x)

			case 0x912:
				x = bytes([
					0x13, 0x9, # opcode 0x913
						#1, 64, 0, 0, # 0x4001 response status OK?
						1, 0, 0, 0,
						1, 0, 0, 0,
						2, 0,
						ord('D'), ord('1'),
				]) + (bytes([1, 0, 0, 0]) * 11) \
				+ (bytes([
						2, 0,
						ord('D'), ord('2'),
						1, 0, 0, 0,
						1, 0, 0, 0,
				]) * 4) \
				+ bytes([
						1, 0, 0, 0,
						2, 0,
						ord('D'), ord('3'),
						1, 0, 0, 0, # <--- some count
						2, 0,
						ord('D'), ord('4'),
						1, 0, 0, 0,
						2, 0,
						ord('D'), ord('5'),
						0, # ??
						1, 0,
				]) \
				+ bytes([
						1, 0, 0, 0,
						1, 0, 0, 0,
						1, 0, 0, 0,
						0, # ?
						1, 0, 0, 0,
						0, 0, # ??
						1, 0, 0, 0,
				])
				#+ (bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]) * 36)
				csock.send((len(x)+2).to_bytes(2, 'little') + x)

			# case _:
			# 	print(f"{peer} Unsupported opcode 0x{opcode:x}, closing.")
			# 	csock.close()
			# 	break

		#x = b'\x11\x11\x03\x00abc\t\x00t-o-k-e-nA\x00\x00\x00\x0e\x00touchHLEdevice\x03\x00abc\x06\x001.0.1j\x00\x01\x00\x00\x00'
		#x = b'\x04\x00' #  0x4
		#if opcode != 0x6:
			
		#csock.send(bytes([0, len(x)+2]) + x)

		#csock.send(bytes([0x10, 0x04]))
		# csock.send(bytes([0, 8, 0, 0, 18, 5, 0, 0, 0, 0]))
		# csock.send(bytes([8, 0, 3, 0, 115, 129, 153, 167]))
#		csock.send((bytes([0, msg_size+2]) + msg) * 10)
		# for x in 0..256:
		# 	for y in 0..256:
		# 		csock.send(bytes([4, 0, x, y]))

		# continue

		# # padding = int.from_bytes(msg[4:8], 'big')
		# # assert padding == 0

		# # # Skip header
		# # msg = msg[8:]

		# match opcode:
		# 	# # Keep-alive?
		# 	# case 0x1205:
		# 	# 	msg_out = b'\x00\x08\x00\x00\x21\x05\x00\x00\x00\x00'
		# 	# 	csock.send(msg_out)

		# 	case _:
		# 		print(f"{peer} Unsupported opcode 0x{opcode:x}, closing.")
		# 		csock.close()
		# 		break

while True:
	client, addr = sock.accept()
	print(f"Accepted connection from: {addr[0]}:{addr[1]}")

	client_handler = threading.Thread(target=handle_client, args=(client,))
	client_handler.start()
