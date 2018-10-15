import secrets
import os
from PIL import Image
from flaskblog import app


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)  # extracting file extension
    picture_fn = random_hex + f_ext  # picture full name
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)  # picture full path
    output_size = (125, 125)  # set output file size to specific size
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn
