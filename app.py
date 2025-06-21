import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from invoice_checker import full_invoice_check

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

if __name__ == '__main__':
    app.run(debug=True)
