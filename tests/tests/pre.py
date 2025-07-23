from slash.core import Elem
from slash.html import Div


def test_pre() -> Elem:
    return Div(
        Elem(
            "pre",
            Elem(
                "code",
                """def fibonacci(n):
    a = 0
    b = 1
    
    # Check if n is less than 0
    if n < 0:
        print("Incorrect input")
        
    # Check if n is equal to 0
    elif n == 0:
        return 0
      
    # Check if n is equal to 1
    elif n == 1:
        return b
    else:
        for i in range(1, n):
            c = a + b
            a = b
            b = c
        return b""",
            ),
        ),
    )
