def compute_checksum(data: bytes) -> int:
    if len(data) % 2 == 1:
        data += b'\x00'  # дополнение до четной длины
    checksum = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i+1]
        checksum += word
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    return ~checksum & 0xFFFF

def add_checksum(data: bytes) -> bytes:
    checksum = compute_checksum(data)
    return checksum.to_bytes(2, byteorder='big') + data

def verify_checksum(data: bytes):
    if len(data) < 2:
        return False, b''
    received_checksum = int.from_bytes(data[:2], byteorder='big')
    payload = data[2:]
    computed_checksum = compute_checksum(payload)
    return received_checksum == computed_checksum, payload
