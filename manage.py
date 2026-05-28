
import subprocess
import sys

def run(cmd: list[str]) -> int:
    print(">", " ".join(cmd))
    return subprocess.call(cmd)

def bootstrap_frontend():
    command = 'docker run -it --rm -v "${PWD}/frontend:/app" -w /app node:22-alpine npx nuxi@latest init . --force --packageManager npm --gitInit false'
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
