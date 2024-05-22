# content of test_sample.py
def sayHelloWorld():
    return "Hello World!"


def test_sayHelloWorld():
    assert sayHelloWorld() ==  "Hello World!"

if __name__ == "__main__":
    import pytest
    pytest.main(["-vv", __file__])