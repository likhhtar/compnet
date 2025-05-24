import random

def str_to_bits(s):
    return ''.join(f'{ord(c):08b}' for c in s)

def bits_to_str(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(b, 2)) for b in chars)

def xor(a, b):
    result = []
    for bit1, bit2 in zip(a, b):
        result.append('0' if bit1 == bit2 else '1')
    return ''.join(result)

def crc_remainder(data_bits, generator):
    n = len(generator)
    padded_data = data_bits + '0' * (n - 1)
    remainder = padded_data[:n]

    for i in range(n, len(padded_data)):
        if remainder[0] == '1':
            remainder = xor(remainder, generator) + padded_data[i]
        else:
            remainder = xor(remainder, '0' * n) + padded_data[i]
        remainder = remainder[1:]

    if remainder[0] == '1':
        remainder = xor(remainder, generator)[1:]
    else:
        remainder = remainder[1:]
    return remainder

def crc_encode(data_bits, generator):
    checksum = crc_remainder(data_bits, generator)
    return data_bits + checksum, checksum

def crc_check(encoded_bits, generator):
    remainder = crc_remainder(encoded_bits, generator)
    return all(bit == '0' for bit in remainder)

def introduce_error(bits, num_errors=1):
    bits = list(bits)
    positions = random.sample(range(len(bits)), num_errors)
    for pos in positions:
        bits[pos] = '1' if bits[pos] == '0' else '0'
    return ''.join(bits), positions

def main():
    generator = '10011'  # CRC-4-ITU
    text = input("Введите текст: ")
    data_bytes = [text[i:i+5] for i in range(0, len(text), 5)]

    print("\n=== Результаты проверки пакетов ===\n")
    for i, packet in enumerate(data_bytes):
        data_bits = str_to_bits(packet)
        encoded_bits, checksum = crc_encode(data_bits, generator)

        # Вносим ошибку в каждый 2-й пакет
        if i % 2 == 1:
            corrupted_bits, error_pos = introduce_error(encoded_bits, num_errors=1)
            is_valid = crc_check(corrupted_bits, generator)
            print(f"[Пакет {i+1}]")
            print(f"  Данные: '{packet}'")
            print(f"  Закодировано: {corrupted_bits}")
            print(f"  Контрольная сумма: {checksum}")
            print(f"  Ошибка на позиции(ях): {error_pos}")
            print(f"  Статус: ❌ Ошибка обнаружена\n" if not is_valid else "  Статус: ✅ Ошибка НЕ обнаружена (ОШИБКА в проверке!)\n")
        else:
            is_valid = crc_check(encoded_bits, generator)
            print(f"[Пакет {i+1}]")
            print(f"  Данные: '{packet}'")
            print(f"  Закодировано: {encoded_bits}")
            print(f"  Контрольная сумма: {checksum}")
            print(f"  Статус: ❌ Ошибка обнаружена (ОШИБКА в проверке!)\n" if not is_valid else "  Статус: ✅ Ошибка НЕ обнаружена\n")

if __name__ == '__main__':
    main()
