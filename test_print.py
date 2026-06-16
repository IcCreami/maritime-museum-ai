import sys
print("TEST MODULE LOADED", file=sys.stderr, flush=True)

def test_func():
    print("TEST FUNCTION CALLED", file=sys.stderr, flush=True)
    return "result"
