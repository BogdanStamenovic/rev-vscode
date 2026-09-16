"""Java-primitive spellings with no direct Python equivalent (or a
different width than Python's own `int`/`str`). These exist only so
generated/hand-written pyftc code can be explicit about which Java type the
translator should choose -- `long`, `short` and `byte` are otherwise all just
Python `int`, and `char` is a one-character `str`. They carry no runtime
behavior of their own.
"""

long = int
short = int
byte = int
char = str
float32 = float
