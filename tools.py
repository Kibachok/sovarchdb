from hashlib import sha256
from PIL import Image
from os.path import abspath
from os import mkdir, rename, listdir, remove
from werkzeug.datastructures import FileStorage
from json import load


REQ_DIRS = ('static', 'static/img', 'static/img/series', 'static/img/u_pfps')
PERM_LIST = ('insight', 'generate_keys', 'moderate_data', 'add_data', 'moderate_media', 'add_media', 'moderate_forum',
             'use_forum')  # per-bit mask 'decoder' keywords:
# integer mask of 3 (b'00000011' will be decrypted as 'access to forum and forum moderation')


def passwd_hash(passwd):
    return str(sha256(str(passwd).encode(), usedforsecurity=True).hexdigest())


def get_user_permission(mask):
    mask = mask & 255
    perms = dict()
    for _ in range(8):
        val = mask // (128 // (2 ** _))
        mask = mask % (128 // (2 ** _))
        perms[PERM_LIST[_]] = bool(val)
    return perms


def get_by_rolekey(key):
    key = passwd_hash(key)
    with open('static/accounts/rolekeys.json', mode='r', encoding='utf-8') as j:
        rks = load(j)
    for _ in rks:
        if _['keyhash'] == key:
            return _['priv_mask']


def img_validator(f: FileStorage, size_limit, endname, resize_bounds=(-1, -1), proportion_coeff=0.0, prop_fault=0.1,
                  prop_validate_only=True):
    """
    Uploaded images processor, takes the byte data and saves it as correctly formatted img
    :param f: image byte data to be parsed;
    :param size_limit: max file size (in megabytes);
    :param endname: file path-name to save it as;
    :param resize_bounds: new sizes [W; H] of the image:
        default is -1;-1, skips the resize if so;
        if one of the values is -1, saves this dimension as it is;
        if one of the values is 'r', changes this dimension relative to the other one;
        if both values are 'r' or one of the values is 'r' and the other one is -1, skips the resize;
    :param proportion_coeff: X/Y coefficient for the image proportion validation;
    :param prop_fault: the interval within the X/Y validates, default is 0.1
    (example: if the coeff is 1.25 and fault is 0.1, the X/Y counts valid if it is within 1.15 and 1.35);
    :param prop_validate_only: if the prop_coeff is within image's X/Y and validate only is False,
    the image deforms to fit the propcoeff;
    :return:
    """
    # validates the format
    filetype = f.filename.split('.')[-1].lower()
    file = f.read()
    if filetype not in ('png', 'jpg', 'jpeg', 'webp', 'gif'):
        return 'Incorrect format'
    # validates the size
    if len(file) > 1048576 * size_limit:
        return f'File is too big, max size is {size_limit} MB'
    # writes the temp data
    with open(f'static/img/tmp/tmp', 'wb+') as wd:
        wd.write(file)
    # tries to read image from tmp, returns error message on error
    try:
        img = Image.open(f'static/img/tmp/tmp', 'r',
                         formats=('png', 'jpeg', 'webp', 'gif')).convert('RGB')
    except Exception as e:
        return f'Error occured: {e}'
    x, y = img.size
    # regular resize; validation
    sizes = [0, 0]
    do_act = (resize_bounds != ('r', 'r') and resize_bounds != (-1, -1)
              and resize_bounds != (-1, 'r') and resize_bounds != ('r', -1))
    valids = []
    r_pos = None
    if type(resize_bounds[0]) == str:
        if resize_bounds[0] == 'r':
            valids += [True]
            r_pos = 0
    elif type(resize_bounds[0]) == int:
        if resize_bounds[0] > 0:
            valids += [True]
    if type(resize_bounds[1]) == str:
        if resize_bounds[1] == 'r':
            valids += [True]
            r_pos = 1
    elif type(resize_bounds[1]) == int:
        if resize_bounds[1] > 0:
            valids += [True]
    valids += [do_act]
    if all(valids):
        if type(r_pos) == int:
            resize_bounds = list(resize_bounds)
            resize_bounds[int(r_pos)] = int((x, y)[int(r_pos)]
                                            * (resize_bounds[int(not r_pos)] / (x, y)[int(not r_pos)]))
        img = img.resize(resize_bounds)
    # updates x and y
    x, y = img.size
    # proportion
    proportion_coeff = abs(proportion_coeff)
    if proportion_coeff != 0.0:
        if not(proportion_coeff - prop_fault <= x / y <= proportion_coeff + prop_fault):
            return (f"File has not enough proportion ({proportion_coeff})." +
                    " Tip: If you don't have image editing skills, " +
                    "you can just screenshot your image inside of the correct bounds")
        else:
            if not prop_validate_only:
                img = img.resize((x, int(x * proportion_coeff)))
    # saves the image
    try:
        mkdir(f'{"/".join(endname.split('/')[:-1])}/')
    except FileExistsError:
        pass
    img.save(endname + '.jpg', format='JPEG', quality=75)
    # clears tmp file
    with open(f'static/img/tmp/tmp', 'wb') as wd:
        wd.write(b'')
    return 'Success'


def required_folders_validator():
    for _ in REQ_DIRS:
        try:
            mkdir(_)
            print(f'{_} was not found, added it')
        except FileExistsError:
            print(f'{_} - OK')


def resort_folder_num(folder, fformat):
    try:
        for i, _ in enumerate(listdir(folder)):
            rename(f'{folder}/{_}', f'{folder}/{i}.temp')
        for _ in range(len(listdir(folder))):
            rename(f"{folder}/{_}.temp", f"{folder}/{_}.{fformat}")
    except FileNotFoundError:
        return


def delete_folder_content(folder):
    try:
        if folder not in ('static', 'static/img', 'static/css', '/', 'data', 'db', 'static/fonts', 'static/accounts',
                          'templates'):
            for _ in listdir(folder):
                remove(f'{folder}/{_}')
    except FileNotFoundError:
        return
