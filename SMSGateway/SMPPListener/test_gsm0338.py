import pytest
import gsm0338
import binascii


def __do_not_optimize_my_imports():
    print(pytest.__all__)
    print(gsm0338.__all__)


def test_gsm0338_encode():
    assert binascii.unhexlify(b'48656c6c6f20576f726c64') == "Hello World".encode('gsm03.38')


def test_gsm0338_decode():
    assert 'Bush hid the facts' == binascii.unhexlify(b'427573682068696420746865206661637473').decode('gsm03.38')
