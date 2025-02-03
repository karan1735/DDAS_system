from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/receive-url', methods=['POST'])
def receive_url():
    data = request.json
    url = data.get('url')
    
    # Run the GUI script with the received URL
    subprocess.Popen(["python", "gui.py", url])
    
    return jsonify({
        "message": f"URL received : {url}\nDownload redirected to application..."
    })

if __name__ == '__main__':
    app.run(port=5003)
