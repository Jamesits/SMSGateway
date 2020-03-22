# https://stackoverflow.com/a/13131694/2646069
# https://stackoverflow.com/a/2453027/2646069

import binascii

gsm = ("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
       "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà")
ext = ("````````````````````^```````````````````{}`````\\````````````[~]`"
       "|````````````````````````````````````€``````````````````````````")


def gsm_encode(plaintext: str) -> bytes:
    res = ""
    for c in plaintext:
        idx = gsm.find(c)
        if idx != -1:
            res += chr(idx)
            continue
        idx = ext.find(c)
        if idx != -1:
            res += chr(27) + chr(idx)
    return binascii.b2a_hex(res.encode('utf-8'))


def gsm_decode(raw: bytes) -> str:
    res = iter(raw)
    result = []
    for c in res:
        if c == 27:
            c = next(res)
            result.append(ext[c])
        else:
            result.append(gsm[c])
    return ''.join(result)


if __name__ == "__main__":
    # b'48656c6c6f20576f726c64'
    print(gsm_encode("Hello World"))
    # "Bush hid the facts"
    print(gsm_decode(binascii.unhexlify(b'427573682068696420746865206661637473')))
