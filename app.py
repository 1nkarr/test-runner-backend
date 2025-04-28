# app.py
from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import uuid
from pathlib import Path

app = Flask(__name__)

@app.post('/run_tests')
def run_tests():
    data = request.get_json()
    code = data.get('code', '')
    tests = data.get('tests', [])

    # создаём временный файл с кодом
    tmp_dir = tempfile.gettempdir()
    filename = Path(tmp_dir) / f'{uuid.uuid4().hex}.py'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code + '\n')

    results = []
    for t in tests:
        input_expr = t.get('input', '')
        expected = str(t.get('expected', '')).strip()
        # запустим интерпретатор: передаём код + print(expression)
        runner_code = (
            code + '\n'
            f"print({input_expr})\n"
        )
        out = subprocess.run(
            ['python3'], input=runner_code.encode('utf-8'),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        actual = out.stdout.decode('utf-8').strip()
        passed = (actual == expected)
        results.append({
            'input': input_expr,
            'expected': expected,
            'actual': actual,
            'passed': passed,
        })

    # удалить файл
    try:
        os.remove(filename)
    except:
        pass

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
