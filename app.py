from flask import Flask, render_template, request, jsonify
import subprocess
import os
import sys

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARM_CONVERTER_PATH = os.path.join(BASE_DIR, 'arm_converter.py')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    code = data.get('code', '')
    arch = data.get('arch', 'arm64')
    mode = data.get('mode', 'arm')

    try:
        command = [sys.executable, ARM_CONVERTER_PATH, code, '--arch', arch, '--mode', mode]
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        
        result = subprocess.run(command, capture_output=True, text=True, check=False, encoding='utf-8', startupinfo=si)

        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip() if result.stderr else "Unknown script error"}), 400

        return jsonify({"output": result.stdout.strip()})
        
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
