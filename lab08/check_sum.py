def compute_checksum(data: bytes) -> int:
    if len(data) % 2 == 1:
        data += b'\x00'

    checksum = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i+1]
        checksum += word
        checksum = (checksum & 0xFFFF) + (checksum >> 16) 

    checksum = ~checksum & 0xFFFF 
    return checksum


def verify_checksum(data: bytes, checksum: int) -> bool:
    if len(data) % 2 == 1:
        data += b'\x00'

    total = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i+1]
        total += word
        total = (total & 0xFFFF) + (total >> 16)

    total += checksum
    total = (total & 0xFFFF) + (total >> 16)

    return total == 0xFFFF


def run_tests():
    # Тест 1: Корректные данные
    data1 = b'hello world'
    checksum1 = compute_checksum(data1)
    print("Test 1:", "PASS" if verify_checksum(data1, checksum1) else "FAIL")

    # Тест 2: Сломанные данные
    data2 = b'hello world'
    checksum2 = compute_checksum(data2)
    data2_corrupted = b'hello worle'  # ошибка в данных
    print("Test 2:", "PASS" if not verify_checksum(data2_corrupted, checksum2) else "FAIL")

    # Тест 3: Пустые данные
    data3 = b''
    checksum3 = compute_checksum(data3)
    print("Test 3:", "PASS" if verify_checksum(data3, checksum3) else "FAIL")

if __name__ == "__main__":
    run_tests()

