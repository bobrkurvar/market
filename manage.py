
import subprocess
import sys

def run(cmd: list[str]) -> int:
    print(">", " ".join(cmd))
    return subprocess.call(cmd)

def bootstrap_frontend():
    command = 'docker run -it --rm -v "${PWD}/frontend:/api" -v /api/node_modules -w /api node:22-alpine npx nuxi@latest init . --force'
    return run(command.split())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [front]")
        sys.exit(1)

    cmd = sys.argv[1]
    code = 1
    if cmd == "front":
        code = bootstrap_frontend()
    sys.exit(code)
