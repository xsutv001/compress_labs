import struct


class LZ77:
    def __init__(self, window_size=4096, lookahead_buffer_size=16):
        self.window_size = window_size
        self.lookahead_buffer_size = lookahead_buffer_size

    def find_longest_match(self, data, current_pos):
        if current_pos >= len(data):
            return 0, 0

        start_pos = max(0, current_pos - self.window_size)

        end_buffer_pos = min(current_pos + self.lookahead_buffer_size, len(data))

        if current_pos >= end_buffer_pos:
            return 0, 0

        best_match_distance = 0
        best_match_length = 0

        # Пошук найкращої відповідності у вікні
        for i in range(start_pos, current_pos):
            current_match_length = 0

            while (current_pos + current_match_length < end_buffer_pos and
                   data[i + current_match_length] == data[current_pos + current_match_length]):
                current_match_length += 1

                if i + current_match_length >= current_pos or i + current_match_length >= len(data):
                    break

            if current_match_length > best_match_length:
                best_match_distance = current_pos - i
                best_match_length = current_match_length

        return best_match_distance, best_match_length

    #Компресія даних
    def compress(self, data):
        if not data:
            return []

        result = []
        pos = 0

        while pos < len(data):
            distance, length = self.find_longest_match(data, pos)

            if length == 0:
                result.append((0, 0, data[pos]))
                pos += 1
            else:
                if pos + length < len(data):
                    result.append((distance, length, data[pos + length]))
                    pos += length + 1
                else:
                    result.append((distance, length, 0))
                    pos += length

        return result


    #Декомпресія даних
    def decompress(self, compressed_data):
        result = bytearray()

        for i, (distance, length, next_byte) in enumerate(compressed_data):
            if distance > 0 and length > 0:
                for j in range(length):
                    if len(result) >= distance:
                        result.append(result[-distance])

            if next_byte != 0 or i < len(compressed_data) - 1:
                result.append(next_byte)

        return bytes(result)

    #Конвертація стиснених даних у бінарний формат
    def compress_to_binary(self, data):
        compressed = self.compress(data)
        binary_data = bytearray()

        for offset, length, next_byte in compressed:
            binary_data.extend(struct.pack(">HBB", offset, length, next_byte))

        return bytes(binary_data)

    #Декомпресія даних з бінарного формату
    def decompress_from_binary(self, binary_data):
        compressed = []
        for i in range(0, len(binary_data), 4):
            if i + 4 <= len(binary_data):
                offset, length, next_byte = struct.unpack(">HBB", binary_data[i:i + 4])
                compressed.append((offset, length, next_byte))

        return self.decompress(compressed)

    def compress_file(self, input_path, output_path):
        try:
            with open(input_path, 'rb') as f:
                data = f.read()


            compressed_data = self.compress_to_binary(data)

            with open(output_path, 'wb') as f:
                f.write(compressed_data)


            # Обчислення коефіцієнту стиснення
            if len(compressed_data) > 0:
                compression_ratio = len(data) / len(compressed_data)
            else:
                compression_ratio = float('inf')

            return {
                'original_size': len(data),
                'compressed_size': len(compressed_data),
                'compression_ratio': compression_ratio
            }
        except Exception as e:
            print(f"Помилка при стисненні файлу: {e}")
            return None

    def decompress_file(self, input_path, output_path):
        try:
            with open(input_path, 'rb') as f:
                compressed_data = f.read()

            decompressed_data = self.decompress_from_binary(compressed_data)

            with open(output_path, 'wb') as f:
                f.write(decompressed_data)


            return len(decompressed_data)
        except Exception as e:
            print(f"Помилка при декомпресії файлу: {e}")
            return 0

    # Перевірка ідентичності оригінального та декомпресованого файлів
    def verify_files(self, original_path, decompressed_path):
        try:
            with open(original_path, 'rb') as f1:
                original_data = f1.read()

            with open(decompressed_path, 'rb') as f2:
                decompressed_data = f2.read()

            identical = original_data == decompressed_data
            return identical
        except Exception as e:
            return False


def main():

    lz77 = LZ77(window_size=1024, lookahead_buffer_size=16)

    # Шляхи до файлів
    text_file = "sample_text.txt"
    binary_file = "sample_binary.bin"

    text_compressed = "text_compressed.bin"
    text_decompressed = "text_decompressed.txt"

    text_stats = None
    binary_stats = None
    text_identical = False
    binary_identical = False

    try:
        text_stats = lz77.compress_file(text_file, text_compressed)
        if text_stats:
            lz77.decompress_file(text_compressed, text_decompressed)
            text_identical = lz77.verify_files(text_file, text_decompressed)
    except Exception as e:
        print(f"Помилка при обробці текстового файлу: {e}")

    binary_compressed = "binary_compressed.bin"
    binary_decompressed = "binary_decompressed.bin"

    try:
        binary_stats = lz77.compress_file(binary_file, binary_compressed)
        if binary_stats:
            lz77.decompress_file(binary_compressed, binary_decompressed)
            binary_identical = lz77.verify_files(binary_file, binary_decompressed)
    except Exception as e:
        print(f"Помилка при обробці бінарного файлу: {e}")

    print("\n Результати")
    if text_stats:
        print(f"Текстовий файл:")
        print(f"  - Початковий розмір: {text_stats['original_size']} байт")
        print(f"  - Стиснений розмір: {text_stats['compressed_size']} байт")
        print(f"  - Коефіцієнт стиснення: {text_stats['compression_ratio']:.2f}")
        print(f"  - Чи ідентичні файли: {'Так' if text_identical else 'Ні'}")

    if binary_stats:
        print(f"\nБінарний файл:")
        print(f"  - Початковий розмір: {binary_stats['original_size']} байт")
        print(f"  - Стиснений розмір: {binary_stats['compressed_size']} байт")
        print(f"  - Коефіцієнт стиснення: {binary_stats['compression_ratio']:.2f}")
        print(f"  - Чи ідентичні файли: {'Так' if binary_identical else 'Ні'}")


if __name__ == "__main__":
    main()