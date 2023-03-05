import helpers
from flask import request, Flask
from flask import jsonify, render_template
import os

app = Flask(__name__)

@app.route("/write_ip", methods=["GET"])
def write_my_ip():
    dsn = os.getenv('DB_CREDS')
    try:
        helpers.insert_ip(dsn, request.remote_addr)
        return render_template('index.html')
    except Exception as e:
        print(e)
        return render_template('error.html')    

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8000)