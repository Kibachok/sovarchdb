from hashlib import sha256
from PIL import Image
from os.path import abspath
from os import mkdir
from werkzeug.datastructures import FileStorage


def passwd_hash(passwd):
    return str(sha256(str(passwd).encode(), usedforsecurity=True).hexdigest())


def img_validator(f: FileStorage, size_limit, endname, resize_bounds=(-1, -1), do_square=False):
    # validates the format
    filetype = f.filename.split('.')[-1].lower()
    file = f.read()
    if filetype not in ('png', 'jpg', 'jpeg', 'webp', 'gif'):
        return 'Incorrect format'
    # validates the size
    if len(file) > 1048576 * size_limit:
        return f'File is too big, max size is {size_limit} MB'
    # writes the temp data
    with open(f'static/img/tmp/tmp.{filetype}', 'wb+') as wd:
        wd.write(file)
    # tries to read image from tmp, returns error message on error
    try:
        img = Image.open(f'static/img/tmp/tmp.{filetype}', 'r',
                         formats=('png', 'jpeg', 'webp', 'gif'))
    except Exception as e:
        return f'Error occured: {e}'
    x, y = img.size
    if do_square:
        if x * 0.9 > y or x * 1.2 < y:
            return ("File is not square enough." +
                    " Tip: If you don't have image editing skills, " +
                    "you can just screenshot your image inside of the square-ish bounds")
        else:
            if resize_bounds != (-1, -1):
                img = img.resize(resize_bounds)
            else:
                mm = min(x, y)
                img = img.resize((mm, mm))
            img.save(endname + '.jpg')
            return 'Success'
    if resize_bounds != (-1, -1):
        img = img.resize(resize_bounds)
    try:
        mkdir(f'{"/".join(endname.split('/')[:-1])}/')
    except FileExistsError:
        pass
    img.save(endname + '.jpg')
    return 'Success'
