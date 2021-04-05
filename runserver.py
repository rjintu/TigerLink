from sys import argv, exit, stderr
from server.tigerlink import app

def main(argv):
    try:
        port = int(argv[1])
    except Exception:
        print('Invalid port argument.', file=stderr)
        exit(1)

    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    main(argv)
