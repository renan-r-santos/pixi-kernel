import sys

from .fallback import start_fallback_kernel

if __name__ == "__main__":
    start_fallback_kernel(message=sys.argv[-1], connection_file=sys.argv[-2])
