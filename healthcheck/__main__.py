import sys
import socket


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.settimeout(10)  # seconds
            sock.connect(("127.0.0.1", 8008))
            data = sock.recv(1024)
        except:
            data = None

    if data == b"healthy":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
