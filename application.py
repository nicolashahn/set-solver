import os
from flask import Flask, flash, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
from SetGame import SetGame


UPLOAD_FOLDER = 'flask-upload'
SOLVED_FOLDER = 'flask-solved'
ALLOWED_EXTENSIONS = [
  'jpg',
  'jpeg'
]

application = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def solve_set(filename):
  filepath = os.path.join(UPLOAD_FOLDER, filename)
  game = SetGame(filepath)
  game.solve()
  game.draw_sets()
  game.write_im(filename,
                out_dir=SOLVED_FOLDER)
  return os.path.join(SOLVED_FOLDER, filename)


@application.route('/solve', methods=['POST', 'GET'])
def solve():
  if request.method == 'POST':
    # check if the post request has the file part
    if 'file' not in request.files:
      flash('No file part')
      return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
      flash('No selected file')
      return redirect(request.url)
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      filepath = os.path.join(UPLOAD_FOLDER, filename)
      file.save(filepath)
      solve_set(filename)
      return send_from_directory(SOLVED_FOLDER, filename)
      # return redirect(url_for('solve',
                              # filename=filename))
  return '''
  <!doctype html>
  <title>Upload SET game image</title>
  <h1>Upload new File</h1>
  <form method=post enctype=multipart/form-data>
    <input type=file name=file>
    <input type=submit value=Upload>
  </form>
  '''

def main():
  for directory in (UPLOAD_FOLDER, SOLVED_FOLDER):
    if not os.path.exists(directory):
      os.mkdir(directory)
  # Setting debug to True enables debug output. This line should be
  # removed before deploying a production app.
  application.debug = True
  application.run()

# run the app.
if __name__ == "__main__":
  main()
