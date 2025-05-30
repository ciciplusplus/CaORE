#!/usr/bin/env python3
"""
Re‑implementation of the MY_String2Blob / MY_Blob2String codec
that appeared in the C source‑snippet.  The 64‑character alphabet is

    abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-

which is the “URL‑safe” Base‑64 alphabet with the last two symbols
reversed ( _ comes before - ).

Both encoder and decoder reproduce the bit‑twiddling order of the
original C code, so the Python and C outputs are byte‑for‑byte identical.
"""

# ----------------------------------------------------------------------
#  helpers – map a 6‑bit value <-> custom alphabet character
# ----------------------------------------------------------------------
def _enc_6bit(n: int) -> str:
    """Convert a number 0‑63 to its alphabet character."""
    if n < 26:                      # a‑z
        return chr(n + ord('a'))
    elif n < 52:                    # A‑Z
        return chr(n + ord("'"))    # 0x27 offset, exactly like the C code
    elif n > 61:                    # 62/63
        return '_' if n == 62 else '-'
    else:                           # 0‑9
        return chr(n - 4)


def _dec_6bit(ch: str) -> int:
    """Inverse of _enc_6bit()."""
    if 'a' <= ch <= 'z':
        return ord(ch) - ord('a')
    elif 'A' <= ch <= 'Z':
        return ord(ch) - ord('A') + 26
    elif '0' <= ch <= '9':
        return ord(ch) - ord('0') + 52
    elif ch == '_':
        return 62
    else:                           # '-'
        return 63


# ----------------------------------------------------------------------
#  forward direction  —  string  ->  blob
# ----------------------------------------------------------------------
def MY_String2Blob(src: str) -> str:
    """
    Encode an arbitrary 8‑bit string to the custom Base‑64‑like blob.
    Bit ordering and padding match the original C routine exactly.
    """
    data = src.encode('latin1')     # keep raw byte values 0‑255
    out_chars = []

    i = 0
    bits_left_in_byte = 8           # like uVar5 in the C version

    while i < len(data):
        v = data[i] >> (8 - bits_left_in_byte)

        if bits_left_in_byte < 6:   # need (part of) the next byte
            i += 1
            if i < len(data):
                v |= (data[i] << bits_left_in_byte) & 0xFF
                bits_left_in_byte += 2
        else:                       # enough bits in the current byte
            bits_left_in_byte -= 6
            if bits_left_in_byte == 0:
                i += 1
                bits_left_in_byte = 8

        out_chars.append(_enc_6bit(v & 0x3F))

    # C code emits one extra 'a' (value 0) when the last 6‑bit group
    # ends exactly at a byte boundary and the input wasn’t empty.
    if data and bits_left_in_byte == 8:
        out_chars.append(_enc_6bit(0))

    return ''.join(out_chars)


# ----------------------------------------------------------------------
#  reverse direction  —  blob  ->  original string
# ----------------------------------------------------------------------
def MY_Blob2String(blob: str) -> str:
    """
    Decode the blob back to the original 8‑bit string
    (the reverse of MY_String2Blob).
    """
    bit_offset = 0      # how many bits already filled in current_byte
    current_byte = 0
    out = bytearray()

    for ch in blob:
        v = _dec_6bit(ch) & 0x3F
        free_bits = 8 - bit_offset

        if free_bits >= 6:                  # fits entirely
            current_byte |= v << bit_offset
            bit_offset += 6
            if bit_offset == 8:
                out.append(current_byte & 0xFF)
                current_byte = 0
                bit_offset = 0
        else:                               # splits across bytes
            current_byte |= (v & ((1 << free_bits) - 1)) << bit_offset
            out.append(current_byte & 0xFF)

            current_byte = v >> free_bits
            bit_offset = 6 - free_bits

    # Left‑over bits are padding zeroes -> ignore
    return out.decode('latin1')


# ----------------------------------------------------------------------
#  quick self‑test  (mirrors the C "main")
# ----------------------------------------------------------------------
if __name__ == "__main__":

    # 1 – original C test
    if MY_String2Blob("f|1|i|25470|v|1.0.1j|") != \
         "MXxm8LgFYudn3adF2XxmUaJlXOgFa":
        print("FAILED 1")
    else:
        print("PASSED 1")

    # 2 – original C test
    if MY_String2Blob(
        "f|204|i|25470|y|1|nid|0|l|en|u|ae87b081fddccaf8fc32180b52b639b10a662e26|"
       ) != "MXNmWqdFPXNm1qZnWWxE8fdFULgz8bdFSXxzUXxD8fwz4CJyWGtmMrgzJnwyMHJzJnJmXGdmIvJmIzZm5iwmWeMn2itzYydFa":
        print("FAILED 2")
    else:
        print("PASSED 2")

    # 3 – new reverse‑direction test
    if MY_Blob2String("MXxm8LgFYudn3adF2XxmUaJlXOgFa") != \
         "f|1|i|25470|v|1.0.1j|":
        print("FAILED 3")
    else:
        print("PASSED 3")

    # 4 – new reverse‑direction test
    if MY_Blob2String(
       "MXNmWqdFPXNm1qZnWWxE8fdFULgz8bdFSXxzUXxD8fwz4CJyWGtmMrgzJnwyMHJzJnJmXGdmIvJmIzZm5iwmWeMn2itzYydFa"
       ) != "f|204|i|25470|y|1|nid|0|l|en|u|ae87b081fddccaf8fc32180b52b639b10a662e26|":
        print("FAILED 4")
    else:
        print("PASSED 4")
