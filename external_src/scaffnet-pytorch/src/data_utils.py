import numpy as np
from PIL import Image


def read_paths(filepath):
    '''
    Reads a newline delimited file containing paths

    Arg(s):
        filepath : str
            path to file to be read
    Return:
        list : list of paths
    '''

    path_list = []
    with open(filepath) as f:
        while True:
            path = f.readline().rstrip('\n')

            # If there was nothing to read
            if path == '':
                break

            path_list.append(path)

    return path_list

def write_paths(filepath, paths):
    '''
    Stores line delimited paths into file

    Arg(s):
        filepath : str
            path to file to save paths
        paths : list
            paths to write into file
    '''

    with open(filepath, 'w') as o:
        for idx in range(len(paths)):
            o.write(paths[idx] + '\n')

def load_image(path, normalize=True, data_format='HWC'):
    '''
    Loads an RGB image

    Arg(s):
        path : str
            path to RGB image
        normalize : bool
            if set, then normalize image between [0, 1]
        data_format : str
            'CHW', or 'HWC'
    Returns:
        numpy[float32] : H x W x C or C x H x W image
    '''

    # Load image
    image = Image.open(path).convert('RGB')

    # Convert to numpy
    image = np.asarray(image, np.float32)

    if data_format == 'CHW':
        image = np.transpose(image, (2, 0, 1))

    # Normalize
    image = image / 255.0 if normalize else image

    return image

def load_depth_with_validity_map(path, multiplier=256.0, data_format='HW'):
    '''
    Loads a depth map and validity map from a 16-bit PNG file

    Arg(s):
        path : str
            path to 16-bit PNG file
        multiplier : float
            multiplier for encoding float as 16/32 bit unsigned integer
        data_format : str
            HW, CHW, HWC
    Returns:
        numpy[float32] : depth map
        numpy[float32] : binary validity map for available depth measurement locations
    '''

    # Loads depth map from 16-bit PNG file
    z = np.array(Image.open(path), dtype=np.float32)

    # Assert 16-bit (not 8-bit) depth map
    z = z / multiplier
    z[z <= 0] = 0.0
    v = z.astype(np.float32)
    v[z > 0] = 1.0

    # Expand dimensions based on output format
    if data_format == 'HW':
        pass
    elif data_format == 'CHW':
        z = np.expand_dims(z, axis=0)
        v = np.expand_dims(v, axis=0)
    elif data_format == 'HWC':
        z = np.expand_dims(z, axis=-1)
        v = np.expand_dims(v, axis=-1)
    else:
        raise ValueError('Unsupported data format: {}'.format(data_format))

    return z, v

def load_depth(path, multiplier=256.0, data_format='HW'):
    '''
    Loads a depth map from a 16-bit PNG file

    Arg(s):
        path : str
            path to 16-bit PNG file
        multiplier : float
            multiplier for encoding float as 16/32 bit unsigned integer
        data_format : str
            HW, CHW, HWC
    Returns:
        numpy[float32] : depth map
    '''

    # Loads depth map from 16-bit PNG file
    z = np.array(Image.open(path), dtype=np.float32)

    # Assert 16-bit (not 8-bit) depth map
    z = z / multiplier
    z[z <= 0] = 0.0

    # Expand dimensions based on output format
    if data_format == 'HW':
        pass
    elif data_format == 'CHW':
        z = np.expand_dims(z, axis=0)
    elif data_format == 'HWC':
        z = np.expand_dims(z, axis=-1)
    else:
        raise ValueError('Unsupported data format: {}'.format(data_format))

    return z

def save_depth(z, path, multiplier=256.0):
    '''
    Saves a depth map to a 16-bit PNG file

    Arg(s):
        z : numpy[float32]
            depth map
        path : str
            path to store depth map
        multiplier : float
            multiplier for encoding float as unsigned integer
    '''

    z = np.uint32(z * multiplier)
    z = Image.fromarray(z, mode='I')
    z.save(path)

def load_validity_map(path, data_format='HW'):
    '''
    Loads a validity map from a 16-bit PNG file

    Arg(s):
        path : str
            path to 16-bit PNG file
        data_format : str
            HW, CHW, HWC
    Returns:
        numpy[float32] : binary validity map for available depth measurement locations
    '''

    # Loads validity map from 16-bit PNG file
    v = np.array(Image.open(path), dtype=np.float32)
    assert(np.all(np.unique(v) == [0, 256]))
    v[v > 0] = 1

    # Expand dimensions based on output format
    if data_format == 'HW':
        pass
    elif data_format == 'CHW':
        v = np.expand_dims(v, axis=0)
    elif data_format == 'HWC':
        v = np.expand_dims(v, axis=-1)
    else:
        raise ValueError('Unsupported data format: {}'.format(data_format))

    return v

def save_validity_map(v, path):
    '''
    Saves a validity map to a 16-bit PNG file

    Arg(s):
        v : numpy[float32]
            validity map
        path : str
            path to store validity map
    '''

    v[v <= 0] = 0.0
    v[v > 0] = 1.0
    v = np.uint32(v * 256.0)
    v = Image.fromarray(v, mode='I')
    v.save(path)


def load_uncertainty(path, multiplier=256.0, offset=128.0, data_format='HW'):
    '''
    Loads a uncertainty map from a 16-bit PNG file

    Arg(s):
        path : str
            path to 16-bit PNG file
        multiplier : float
            multiplier for encoding float as 16/32 bit unsigned integer
        offset : float
            offset for negative values in uncertainty map
        data_format : str
            HW, CHW, HWC
    Returns:
        numpy[float32] : uncertainty map corresponding to estimates
    '''

    # Loads uncertainty map from 16-bit PNG file
    uncertainty = np.array(Image.open(path), dtype=np.float32)

    # Assert 16-bit (not 8-bit) depth map
    uncertainty = uncertainty / multiplier - offset

    # Expand dimensions based on output format
    if data_format == 'HW':
        pass
    elif data_format == 'CHW':
        uncertainty = np.expand_dims(uncertainty, axis=0)
    elif data_format == 'HWC':
        uncertainty = np.expand_dims(uncertainty, axis=-1)
    else:
        raise ValueError('Unsupported data format: {}'.format(data_format))

    return uncertainty

def save_uncertainty(uncertainty, path, multiplier=256.0, offset=128.0):
    '''
    Saves a uncertainty map to a 16-bit PNG file

    Arg(s):
        uncertainty : numpy[float32]
            H x W uncertainty map
        path : str
            path to store validity map
        multiplier : float
            multiplier for encoding float as 16/32 bit unsigned integer
        offset : float
            offset for negative values in uncertainty map
    '''

    uncertainty = np.uint32(uncertainty + offset * multiplier)
    uncertainty = Image.fromarray(uncertainty, mode='I')
    uncertainty.save(path)

def load_calibration(path):
    '''
    Loads the calibration matrices for each camera (KITTI) and stores it as map

    Args:
        path : str
            path to file to be read
    Returns:
        dict : map containing camera intrinsics keyed by camera id
    '''

    float_chars = set("0123456789.e+- ")
    data = {}

    with open(path, 'r') as f:
        for line in f.readlines():
            key, value = line.split(':', 1)
            value = value.strip()
            data[key] = value
            if float_chars.issuperset(value):
                try:
                    data[key] = np.asarray(
                        [float(x) for x in value.split(' ')])
                except ValueError:
                    pass
    return data
