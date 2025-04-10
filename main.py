from collections import Counter
import heapq
from decimal import Decimal, getcontext
import math


def read_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


file_path = 'testfile.txt'
text = read_text_from_file(file_path)

getcontext().prec = int(len(text) * 1.2) + 100


class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(text):
    freq = Counter(text)
    heap = [Node(ch, fr) for ch, fr in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        l = heapq.heappop(heap)
        r = heapq.heappop(heap)
        merged = Node(None, l.freq + r.freq)
        merged.left = l
        merged.right = r
        heapq.heappush(heap, merged)

    return heap[0]


def generate_huffman_codes(root):
    codes = {}

    def helper(node, code):
        if node:
            if node.char is not None:
                codes[node.char] = code
            helper(node.left, code + "0")
            helper(node.right, code + "1")

    helper(root, "")
    return codes


def huffman_encode(text, codes):
    return ''.join(codes[ch] for ch in text)


def huffman_decode(encoded, root):
    result = ''
    node = root

    for bit in encoded:
        node = node.left if bit == '0' else node.right
        if node.char is not None:
            result += node.char
            node = root  # Reset to root after finding a character

    return result


# --- АРИФМЕТИКА ---
def get_frequencies(text):
    freq = Counter(text)
    total = sum(freq.values())
    symbols = sorted(freq.items())
    return [(ch, Decimal(count) / Decimal(total)) for ch, count in symbols]


def build_intervals(frequencies):
    probs = {}
    low = Decimal('0.0')

    for ch, prob in frequencies:
        probs[ch] = (low, low + prob)
        low += prob

    return probs


def arithmetic_encode(text, intervals):
    low = Decimal('0.0')
    high = Decimal('1.0')

    for ch in text:
        ch_low, ch_high = intervals[ch]
        range_ = high - low
        high = low + range_ * ch_high
        low = low + range_ * ch_low

    return (low + high) / 2, low, high


def arithmetic_decode(code, intervals, length):
    inverse = sorted(intervals.items(), key=lambda x: x[1][0])
    result = ''

    for _ in range(length):
        for ch, (low, high) in inverse:
            if low <= code < high:
                result += ch
                code = (code - low) / (high - low)
                break

    return result


def calculate_arithmetic_bits(low, high):
    """Calculate the minimum number of bits needed to represent a number in [low, high]"""
    # The precision we need is enough to distinguish between low and high
    diff = high - low
    # Convert to binary and count significant bits
    # We need -log2(diff) bits to represent this range
    return math.ceil(-math.log2(float(diff)))


# --- ВИКОНАННЯ ---
# Хаффман
root = build_huffman_tree(text)
codes = generate_huffman_codes(root)
encoded_huff = huffman_encode(text, codes)
decoded_huff = huffman_decode(encoded_huff, root)

# Арифметика
frequencies = get_frequencies(text)
intervals = build_intervals(frequencies)
code, low_bound, high_bound = arithmetic_encode(text, intervals)
decoded = arithmetic_decode(code, intervals, len(text))

# Оцінка розмірів
original_bits = len(text) * 8
huffman_bits = len(encoded_huff)
arithm_bits = calculate_arithmetic_bits(low_bound, high_bound)

# --- ВИВІД ---
print("Початковий текст:", text)
print("\n--- ХАФФМАН ---")
print("Закодований:", encoded_huff)
print("Декодований:", decoded_huff)
print("Коефіцієнт стиснення:", round(original_bits / huffman_bits, 2))

print("\n--- АРИФМЕТИКА ---")
print("Кодоване число:", code)
print("Декодований:", decoded)
print("Коефіцієнт стиснення:", round(original_bits / arithm_bits, 2))