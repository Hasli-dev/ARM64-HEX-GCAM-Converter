from flask import Flask, render_template, request, jsonify
import subprocess
import sys
import os

app = Flask(__name__)

# Путь к скрипту arm_converter.py
ARM_CONVERTER_PATH = os.path.join(os.path.dirname(__file__), 'arm_converter.py')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    code = data.get('code', '')
    arch = data.get('arch', 'arm64')
    mode = data.get('mode', 'arm')
    action = data.get('action', 'assemble') # Получаем действие

    try:
        # Передаем действие в скрипт
        command = [sys.executable, ARM_CONVERTER_PATH, code, '--arch', arch, '--mode', mode, '--action', action]
        
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            startupinfo=startupinfo
        )
        return jsonify({'output': result.stdout.strip()})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.stderr.strip()})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
