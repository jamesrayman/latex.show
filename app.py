from flask import Flask, Response
from pathlib import Path
from hashlib import blake2b
import subprocess
import shutil

app = Flask(__name__)
hash_acc = blake2b(digest_size=12)


def get_hash(data):
    hash_acc.update(data.encode())
    return hash_acc.hexdigest()


def decode(data):
    tr = {
        ';;': ';',
        ';(': '{',
        ';)': '}',
        ';/': '/',
        '//': '\\',
    }

    i = 0
    res = ''

    while i < len(data):
        if i+2 <= len(data) and data[i:i+2] in tr:
            res += tr[data[i:i+2]]
            i += 2
        else:
            res += data[i]
            i += 1

    return res


@app.route('/')
def help():
    return 'Help text'


@app.route('/<path:query>')
def render(query):
    name = get_hash(query)
    data_dir = Path(f'data/{name}')
    data_dir.mkdir(exist_ok=True, parents=True)

    query = decode(query)

    with open(data_dir/'pic.asy', 'w') as f:
        f.write(f'settings.outformat = "svg"; label("${query}$");')

    subprocess.run(['asy', 'pic.asy'], cwd=data_dir)

    with open(data_dir/'pic.svg', 'rb') as f:
        svg = f.read()

    shutil.rmtree(data_dir)

    return Response(svg, mimetype='image/svg+xml')
