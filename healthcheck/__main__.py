import sys
import socket


def check():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(10)  # seconds
        sock.connect(("127.0.0.1", 8008))
        data = sock.recv(1024)
    except Exception:
        data = None
    finally:
        sock.close()

    if data == b"healthy":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    check()
