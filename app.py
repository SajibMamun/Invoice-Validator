import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from invoice_checker import full_invoice_check

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------- Web Route ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    ela_image = None
    image_path = None

    if request.method == 'POST':
        file = request.files['invoice']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(image_path)

            result, ela_image = full_invoice_check(image_path)

    return render_template('index.html', result=result, image=image_path, ela_image=ela_image)


# ---------- API Route ----------
@app.route('/api/check_invoice', methods=['POST'])
def check_invoice_api():
    if 'invoice' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['invoice']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    result_text, ela_image_path = full_invoice_check(filepath)

    status = "authentic" if "passed all checks" in result_text.lower() else "altered"

    return jsonify({
        "status": status,
        "message": result_text,
        "invoice_image": filepath,
        "ela_image": ela_image_path
    })


if __name__ == '__main__':
    app.run(debug=True)
