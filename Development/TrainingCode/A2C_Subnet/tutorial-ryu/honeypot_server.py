from flask import Flask, jsonify

app = Flask(__name__)

# Misleading information to be served by the honeypot
misleading_info = {
    "important_data": "This is misleading information.",
    "fake_credentials": {
        "username": "fake_user",
        "password": "fake_password"
    },
    "decoy_files": ["decoy1.txt", "decoy2.txt"]
}

@app.route('/important_info', methods=['GET'])
def get_important_info():
    return jsonify(misleading_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15000)