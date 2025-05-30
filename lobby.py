from socket import socket, SOL_SOCKET, SO_REUSEADDR, MSG_WAITALL
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--port', dest='port', default=9999, type=int, help='Specifies port to run on')
args = parser.parse_args()

bind_ip = "0.0.0.0"
bind_port = args.port

sock = socket()
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.bind((bind_ip, bind_port))
sock.listen()

print(f"Listening on port {bind_ip} : {bind_port}")  

# TODO: return decoded
def decode_msg_in(csock, msg):
	peer = csock.getpeername()
	idx = 0
	while idx < len(msg):
		chunk_size = int.from_bytes(msg[idx:idx+2], 'big')
		chunk_id = int.from_bytes(msg[idx+2:idx+4], 'big')
		data_type = int.from_bytes(msg[idx+4:idx+5], 'big')
		print(f"{peer} Chunk: size {chunk_size:02}, chunk_id 0x{chunk_id:x}, data_type {data_type}")
		match data_type:
			# Raw bytes?
			case 0x0:
				bb = msg[idx+5:idx+chunk_size]
				print(f"{peer} Chunk value: bytes '{bb}'")
			# Byte or Char
			case 0x1:
				b = msg[idx+5:idx+6][0]
				print(f"{peer} Chunk value: byte {b}, char '{chr(b)}'")
			# Short
			case 0x2:
				i = int.from_bytes(msg[idx+5:idx+7], 'big')
				print(f"{peer} Chunk value: short {i}")
			# Integer
			case 0x3:
				i = int.from_bytes(msg[idx+5:idx+9], 'big')
				print(f"{peer} Chunk value: int {i}")
			# C string without null terminator
			case 0x6:
				str = msg[idx+5:idx+chunk_size].decode('ascii') # TODO: use utf-8?
				print(f"{peer} Chunk value: str '{str}'")
			case _:
				print(f"{peer} Unsupported data_type {data_type}")
		idx += chunk_size

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

	# Establish connection?
	dropped = csock.recv(8, MSG_WAITALL)
	assert len(dropped) == 8
	print(f"{peer} Dropping first 8 bytes: {dropped}")

	while True:
		msg_size_bytes = csock.recv(2, MSG_WAITALL)
		assert len(msg_size_bytes) == 2
		msg_size = int.from_bytes(msg_size_bytes, 'big')
		print(f"{peer} Expect message of size {msg_size}")

		msg = csock.recv(msg_size, MSG_WAITALL)
		assert len(msg) == msg_size
		print(f"{peer} Recieved message {msg}")

		# Parse incoming message
		opcode = int.from_bytes(msg[:4], 'big')
		print(f"{peer} Message in opcode 0x{opcode:x}")

		padding = int.from_bytes(msg[4:8], 'big')
		assert padding == 0

		# Skip header
		msg = msg[8:]

		match opcode:
			case 0x1205:
				action_desc = "Keep-alive"
				msg_out = b'\x00\x08\x00\x00\x21\x05\x00\x00\x00\x00'
				csock.send(msg_out)

			# case 0x1204:
			# 	action_desc = "Lobby logout??"
			# 	decode_msg_in(csock, msg)

			# 	# TODO: constuct response
			# 	# NOTE: msg size (without size itself) is appened before in send_msg_out()
			# 	msg_out = bytes([
			# 		0, 0, 33, 4, # opcode 0x2104
			# 	])
			# 	send_msg_out(csock, 0x2104, action_desc, msg_out)

			case 0x1203:
				action_desc = "Lobby login"
				decode_msg_in(csock, msg)

				# TODO: constuct response
				# NOTE: msg size (without size itself) is appened before in send_msg_out()
				msg_out = bytes([
					0, 0, 33, 3, # opcode 0x2103
					0, 0, 0, 0, #padding?
						0, 9, # size of next chunk (with size itself)
							255, 0, 3, # 0xff00 3
							0, 0, 0, 0, # (previous state? or protocol version?)
						0, 9,
							1, 13, 6, # 0x10d 6 (version)
							48, 46, 48, 48, # "0.00"
						0, 8,
							1, 14, 6, # 0x10e 6 ??
							66, 66, 49, # BB1
				])
				send_msg_out(csock, 0x2103, action_desc, msg_out)

			case 0x1206:
				action_desc = "Room join"
				decode_msg_in(csock, msg)

				# TODO: constuct response
				# NOTE: msg size (without size itself) is appened before in send_msg_out()
				msg_out = bytes([
					0, 0, 33, 6, # opcode 0x2106
					0, 0, 0, 0, #padding?
						0, 9, # size of next chunk (with size itself)
							255, 0, 3, # 0xff00 3
							0, 0, 0, 0, # (protocol version?)
						0, 17,
							0, 3, 6, # 0x3 6, Lobby IP
							49, 57, 50, 46, 49, 54, 56, 46, 49, 46, 55, 56, # str '192.168.1.78'
						0, 7,
							1, 1, 2, # 0x101 2, Lobby port
							39, 14, # short 9998
						# 0, 17,
						# 	0, 3, 6, # 0x3 6, Lobby IP
						# 	49, 57, 50, 46, 49, 54, 56, 46, 49, 46, 56, 55, # str '192.168.1.87'
						# 0, 7,
						# 	1, 1, 2, # 0x101 2, Lobby port
						# 	27, 99, # short 7011
				])
				send_msg_out(csock, 0x2106, action_desc, msg_out)

			case 0x120c:
				action_desc = "Lobby get room list by filter"
				decode_msg_in(csock, msg)

				# TODO: constuct response
				# NOTE: msg size (without size itself) is appened before in send_msg_out()
				msg_out = bytes([
					0, 0, 33, 18, # opcode 0x2112
					0, 0, 0, 0, # padding
						0, 9, # size of next chunk (with size itself)
							255, 0, 3, # 0xff00 3
							0, 0, 0, 0, # 0 (protocol version?)
						0, 12,
							2, 19, 6, # 0x213 6, room name
							84, 117, 110, 110, 101, 108, 32, # str "Tunnel "
						0, 9,
							2, 20, 3, # 0x214 3, ??
							0, 0, 0, 0, # int 0
						0, 96,
							2, 1, 0, # 0x201 0 ??
								0, 9,
									2, 2, 3, # 0x202 3, room id
									0, 0, 0, 6, # int 6
								0, 6,
									2, 16, 6, # 0x210 6 ??
									68, # str 'D'
								0, 17,
									0, 3, 6, # 0x3 6, Lobby IP
									#49, 57, 50, 46, 49, 54, 56, 46, 49, 46, 56, 55, # str '192.168.1.87'
									49, 57, 50, 46, 49, 54, 56, 46, 49, 46, 55, 56, # str '192.168.1.78'
								0, 7,
									0, 1, 2, # 0x1 2, Lobby port
									#27, 99, # short 7011
									39, 15, # short 9999
								0, 13,
									2, 3, 6, # 0x203 6, room name
									84, 117, 110, 110, 101, 108, 32, 48, # str "Tunnel 0"
								0, 6,
									2, 11, 1, # 0x20b 1, ?
									8, # byte 8
								0, 6,
									2, 12, 1, # 0x20c 1, ?
									9, # byte 9
								0, 9,
									2, 5, 3, # 0x205 3 ??
									0, 0, 0, 10, # int 10
								0, 9,
									2, 6, 3, # 0x206 3 ??
									0, 0, 0, 11, # int 11
								0, 9,
									2, 7, 3, # 0x207 3 ??
									0, 0, 0, 12, # int 12
				])
				send_msg_out(csock, 0x2112, action_desc, msg_out)

			# case 0x120a:
			# 	action_desc = "Lobby search room by name"
			# 	decode_msg_in(csock, msg)

			# 	# TODO: constuct response
			# 	# NOTE: msg size (without size itself) is appened before in send_msg_out()
			# 	msg_out = bytes([
			# 		0, 0, 33, 10, # opcode 0x210a
			# 		0, 0, 0, 0, # padding
			# 			0, 9, # size of next chunk (with size itself)
			# 				255, 0, 3, # 0xff00 3
			# 				0, 0, 0, 0, # 0 (protocol version?)
			# 			0, 13,
			# 				2, 3, 6, # 0x203 6, room name
			# 				84, 117, 110, 110, 101, 108, 32, 48, # str "Tunnel 0"
			# 			0, 6,
			# 				2, 11, 1, # 0x20b 1, ?
			# 				0, # byte 0
			# 			0, 6,
			# 				2, 12, 1, # 0x20c 1, ?
			# 				0, # byte 0
			# 			0, 9,
			# 				2, 2, 3, # 0x202 3, ?
			# 				0, 0, 0, 0, # int 0
			# 			# 0, 49,
			# 			# 	2, 14, 0, # 0x20e 0, ?
			# 			# 	0, 0, 0, 0,
			# 			# 	0, 0, 0, 0,
			# 			# 	0, 0, 0, 0,
			# 			# 	0, 0, 0, 0,
			# 			# 	0, 0, 0, 0,
			# 			# 	0, 0, 0, 0,
			# 			# 	0, 0, 0, 0,
			# 			# 	0, 0, 0, 0,
			# 			# 	0, 0, 0, 0,
			# 			# 	0, 0, 0, 0, 0, 0, 0,
			# 			# 0, 6,
			# 			# 	2, 14, #2, # 0x20e 2, ?
			# 			# 	0, 0, # short 0
			# 			# 0, 6,
			# 			# 	2, 14, 1, # 0x20e 1, ?
			# 			# 	0, # byte 0
			# 	]) + bytes([0, 17, 3, 4, 0]) + b'\x00\x06\x03\x05\x01\x00\x00\x06\x03\t\x01\x00'
			# 	send_msg_out(csock, 0x210a, action_desc, msg_out)

			case _:
				print(f"{peer} Unsupported opcode 0x{opcode:x}, closing.")
				csock.close()
				break

while True:
	client, addr = sock.accept()
	print(f"Accepted connection from: {addr[0]}:{addr[1]}")

	client_handler = threading.Thread(target=handle_client, args=(client,))
	client_handler.start()
