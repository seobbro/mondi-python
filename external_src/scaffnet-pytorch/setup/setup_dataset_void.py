import os, sys, glob
import multiprocessing as mp
import numpy as np
import cv2
sys.path.insert(0, 'src')
import data_utils


VOID_ROOT_DIRPATH       = os.path.join('data', 'void_release')
VOID_DATA_150_DIRPATH   = os.path.join(VOID_ROOT_DIRPATH, 'void_150')
VOID_DATA_500_DIRPATH   = os.path.join(VOID_ROOT_DIRPATH, 'void_500')
VOID_DATA_1500_DIRPATH  = os.path.join(VOID_ROOT_DIRPATH, 'void_1500')

VOID_OUTPUT_DIRPATH     = os.path.join('data', 'void_scaffnet')

VOID_TRAIN_IMAGE_FILENAME         = 'train_image.txt'
VOID_TRAIN_SPARSE_DEPTH_FILENAME  = 'train_sparse_depth.txt'
VOID_TRAIN_VALIDITY_MAP_FILENAME  = 'train_validity_map.txt'
VOID_TRAIN_GROUND_TRUTH_FILENAME  = 'train_ground_truth.txt'
VOID_TRAIN_INTRINSICS_FILENAME    = 'train_intrinsics.txt'
VOID_TEST_IMAGE_FILENAME          = 'test_image.txt'
VOID_TEST_SPARSE_DEPTH_FILENAME   = 'test_sparse_depth.txt'
VOID_TEST_VALIDITY_MAP_FILENAME   = 'test_validity_map.txt'
VOID_TEST_GROUND_TRUTH_FILENAME   = 'test_ground_truth.txt'
VOID_TEST_INTRINSICS_FILENAME     = 'test_intrinsics.txt'

TRAIN_REFS_DIRPATH      = os.path.join('training', 'void')
TEST_REFS_DIRPATH       = os.path.join('testing', 'void')

# VOID training set 150 density
VOID_TRAIN_IMAGE_150_FILEPATH           = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_image_150.txt')
VOID_TRAIN_SPARSE_DEPTH_150_FILEPATH    = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_sparse_depth_150.txt')
VOID_TRAIN_VALIDITY_MAP_150_FILEPATH    = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_validity_map_150.txt')
VOID_TRAIN_GROUND_TRUTH_150_FILEPATH    = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_ground_truth_150.txt')
VOID_TRAIN_INTRINSICS_150_FILEPATH      = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_intrinsics_150.txt')
# VOID training set 500 density
VOID_TRAIN_IMAGE_500_FILEPATH           = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_image_500.txt')
VOID_TRAIN_SPARSE_DEPTH_500_FILEPATH    = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_sparse_depth_500.txt')
VOID_TRAIN_VALIDITY_MAP_500_FILEPATH    = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_validity_map_500.txt')
VOID_TRAIN_GROUND_TRUTH_500_FILEPATH    = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_ground_truth_500.txt')
VOID_TRAIN_INTRINSICS_500_FILEPATH      = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_intrinsics_500.txt')
# VOID training set 1500 density
VOID_TRAIN_IMAGE_1500_FILEPATH          = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_image_1500.txt')
VOID_TRAIN_SPARSE_DEPTH_1500_FILEPATH   = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_sparse_depth_1500.txt')
VOID_TRAIN_VALIDITY_MAP_1500_FILEPATH   = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_validity_map_1500.txt')
VOID_TRAIN_GROUND_TRUTH_1500_FILEPATH   = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_ground_truth_1500.txt')
VOID_TRAIN_INTRINSICS_1500_FILEPATH     = os.path.join(TRAIN_REFS_DIRPATH, 'void_train_intrinsics_1500.txt')
# VOID testing set 150 density
VOID_TEST_IMAGE_150_FILEPATH            = os.path.join(TEST_REFS_DIRPATH, 'void_test_image_150.txt')
VOID_TEST_SPARSE_DEPTH_150_FILEPATH     = os.path.join(TEST_REFS_DIRPATH, 'void_test_sparse_depth_150.txt')
VOID_TEST_VALIDITY_MAP_150_FILEPATH     = os.path.join(TEST_REFS_DIRPATH, 'void_test_validity_map_150.txt')
VOID_TEST_GROUND_TRUTH_150_FILEPATH     = os.path.join(TEST_REFS_DIRPATH, 'void_test_ground_truth_150.txt')
VOID_TEST_INTRINSICS_150_FILEPATH       = os.path.join(TEST_REFS_DIRPATH, 'void_test_intrinsics_150.txt')
# VOID testing set 500 density
VOID_TEST_IMAGE_500_FILEPATH            = os.path.join(TEST_REFS_DIRPATH, 'void_test_image_500.txt')
VOID_TEST_SPARSE_DEPTH_500_FILEPATH     = os.path.join(TEST_REFS_DIRPATH, 'void_test_sparse_depth_500.txt')
VOID_TEST_VALIDITY_MAP_500_FILEPATH     = os.path.join(TEST_REFS_DIRPATH, 'void_test_validity_map_500.txt')
VOID_TEST_GROUND_TRUTH_500_FILEPATH     = os.path.join(TEST_REFS_DIRPATH, 'void_test_ground_truth_500.txt')
VOID_TEST_INTRINSICS_500_FILEPATH       = os.path.join(TEST_REFS_DIRPATH, 'void_test_intrinsics_500.txt')
# VOID testing set 1500 density
VOID_TEST_IMAGE_1500_FILEPATH           = os.path.join(TEST_REFS_DIRPATH, 'void_test_image_1500.txt')
VOID_TEST_SPARSE_DEPTH_1500_FILEPATH    = os.path.join(TEST_REFS_DIRPATH, 'void_test_sparse_depth_1500.txt')
VOID_TEST_VALIDITY_MAP_1500_FILEPATH    = os.path.join(TEST_REFS_DIRPATH, 'void_test_validity_map_1500.txt')
VOID_TEST_GROUND_TRUTH_1500_FILEPATH    = os.path.join(TEST_REFS_DIRPATH, 'void_test_ground_truth_1500.txt')
VOID_TEST_INTRINSICS_1500_FILEPATH      = os.path.join(TEST_REFS_DIRPATH, 'void_test_intrinsics_1500.txt')


def process_frame(inputs):
    '''
    Processes a single depth frame

    Arg(s):
        inputs : tuple
            image path at time t=0,
            image path at time t=1,
            image path at time t=-1,
            sparse depth path at time t=0,
            validity map path at time t=0,
            ground truth path at time t=0
    Returns:
        str : image reference directory path
        str : output concatenated image path at time t=0
        str : output sparse depth path at time t=0
        str : output validity map path at time t=0
        str : output ground truth path at time t=0
    '''

    image_path1, \
        image_path0, \
        image_path2, \
        sparse_depth_path, \
        validity_map_path, \
        ground_truth_path = inputs

    # Create image composite of triplets
    image1 = cv2.imread(image_path1)
    image0 = cv2.imread(image_path0)
    image2 = cv2.imread(image_path2)
    imagec = np.concatenate([image1, image0, image2], axis=1)

    image_refpath = os.path.join(*image_path0.split(os.sep)[2:])

    # Set output paths
    image_outpath = os.path.join(VOID_OUTPUT_DIRPATH, image_refpath)
    sparse_depth_outpath = sparse_depth_path
    validity_map_outpath = validity_map_path
    ground_truth_outpath = ground_truth_path

    # Verify that all filenames match
    image_out_dirpath, image_filename = os.path.split(image_outpath)
    sparse_depth_filename = os.path.basename(sparse_depth_outpath)
    validity_map_filename = os.path.basename(validity_map_outpath)
    ground_truth_filename = os.path.basename(ground_truth_outpath)

    assert image_filename == sparse_depth_filename
    assert image_filename == validity_map_filename
    assert image_filename == ground_truth_filename

    cv2.imwrite(image_outpath, imagec)

    return (image_refpath,
            image_outpath,
            sparse_depth_outpath,
            validity_map_outpath,
            ground_truth_outpath)


if not os.path.exists(TRAIN_REFS_DIRPATH):
    os.makedirs(TRAIN_REFS_DIRPATH)

if not os.path.exists(TEST_REFS_DIRPATH):
    os.makedirs(TEST_REFS_DIRPATH)


data_dirpaths = [
    VOID_DATA_150_DIRPATH,
    VOID_DATA_500_DIRPATH,
    VOID_DATA_1500_DIRPATH
]

train_output_filepaths = [
    [
        VOID_TRAIN_IMAGE_150_FILEPATH,
        VOID_TRAIN_SPARSE_DEPTH_150_FILEPATH,
        VOID_TRAIN_VALIDITY_MAP_150_FILEPATH,
        VOID_TRAIN_GROUND_TRUTH_150_FILEPATH,
        VOID_TRAIN_INTRINSICS_150_FILEPATH
    ],
    [
        VOID_TRAIN_IMAGE_500_FILEPATH,
        VOID_TRAIN_SPARSE_DEPTH_500_FILEPATH,
        VOID_TRAIN_VALIDITY_MAP_500_FILEPATH,
        VOID_TRAIN_GROUND_TRUTH_500_FILEPATH,
        VOID_TRAIN_INTRINSICS_500_FILEPATH
    ],
    [
        VOID_TRAIN_IMAGE_1500_FILEPATH,
        VOID_TRAIN_SPARSE_DEPTH_1500_FILEPATH,
        VOID_TRAIN_VALIDITY_MAP_1500_FILEPATH,
        VOID_TRAIN_GROUND_TRUTH_1500_FILEPATH,
        VOID_TRAIN_INTRINSICS_1500_FILEPATH
    ]
]
test_output_filepaths = [
    [
        VOID_TEST_IMAGE_150_FILEPATH,
        VOID_TEST_SPARSE_DEPTH_150_FILEPATH,
        VOID_TEST_VALIDITY_MAP_150_FILEPATH,
        VOID_TEST_GROUND_TRUTH_150_FILEPATH,
        VOID_TEST_INTRINSICS_150_FILEPATH
    ],
    [
        VOID_TEST_IMAGE_500_FILEPATH,
        VOID_TEST_SPARSE_DEPTH_500_FILEPATH,
        VOID_TEST_VALIDITY_MAP_500_FILEPATH,
        VOID_TEST_GROUND_TRUTH_500_FILEPATH,
        VOID_TEST_INTRINSICS_500_FILEPATH
    ],
    [
        VOID_TEST_IMAGE_1500_FILEPATH,
        VOID_TEST_SPARSE_DEPTH_1500_FILEPATH,
        VOID_TEST_VALIDITY_MAP_1500_FILEPATH,
        VOID_TEST_GROUND_TRUTH_1500_FILEPATH,
        VOID_TEST_INTRINSICS_1500_FILEPATH
    ]
]


data_filepaths = \
    zip(data_dirpaths, train_output_filepaths, test_output_filepaths)

for data_dirpath, train_filepaths, test_filepaths in data_filepaths:
    # Training set
    train_image_filepath = os.path.join(data_dirpath, VOID_TRAIN_IMAGE_FILENAME)
    train_sparse_depth_filepath = os.path.join(data_dirpath, VOID_TRAIN_SPARSE_DEPTH_FILENAME)
    train_validity_map_filepath = os.path.join(data_dirpath, VOID_TRAIN_VALIDITY_MAP_FILENAME)
    train_ground_truth_filepath = os.path.join(data_dirpath, VOID_TRAIN_GROUND_TRUTH_FILENAME)
    train_intrinsics_filepath = os.path.join(data_dirpath, VOID_TRAIN_INTRINSICS_FILENAME)

    # Read training paths
    train_image_paths = data_utils.read_paths(train_image_filepath)
    train_sparse_depth_paths = data_utils.read_paths(train_sparse_depth_filepath)
    train_validity_map_paths = data_utils.read_paths(train_validity_map_filepath)
    train_ground_truth_paths = data_utils.read_paths(train_ground_truth_filepath)
    train_intrinsics_paths = data_utils.read_paths(train_intrinsics_filepath)

    assert len(train_image_paths) == len(train_sparse_depth_paths)
    assert len(train_image_paths) == len(train_validity_map_paths)
    assert len(train_image_paths) == len(train_ground_truth_paths)
    assert len(train_image_paths) == len(train_intrinsics_paths)

    # Testing set
    test_image_filepath = os.path.join(data_dirpath, VOID_TEST_IMAGE_FILENAME)
    test_sparse_depth_filepath = os.path.join(data_dirpath, VOID_TEST_SPARSE_DEPTH_FILENAME)
    test_validity_map_filepath = os.path.join(data_dirpath, VOID_TEST_VALIDITY_MAP_FILENAME)
    test_ground_truth_filepath = os.path.join(data_dirpath, VOID_TEST_GROUND_TRUTH_FILENAME)
    test_intrinsics_filepath = os.path.join(data_dirpath, VOID_TEST_INTRINSICS_FILENAME)

    # Read testing paths
    test_image_paths = data_utils.read_paths(test_image_filepath)
    test_sparse_depth_paths = data_utils.read_paths(test_sparse_depth_filepath)
    test_validity_map_paths = data_utils.read_paths(test_validity_map_filepath)
    test_ground_truth_paths = data_utils.read_paths(test_ground_truth_filepath)
    test_intrinsics_paths = data_utils.read_paths(test_intrinsics_filepath)

    assert len(test_image_paths) == len(test_sparse_depth_paths)
    assert len(test_image_paths) == len(test_validity_map_paths)
    assert len(test_image_paths) == len(test_ground_truth_paths)
    assert len(test_image_paths) == len(test_intrinsics_paths)

    # Get test set directories
    test_seq_dirpaths = set(
        [test_image_paths[idx].split(os.sep)[-3] for idx in range(len(test_image_paths))])

    # Initialize placeholders for training output paths
    train_image_outpaths = []
    train_sparse_depth_outpaths = []
    train_validity_map_outpaths = []
    train_ground_truth_outpaths = []
    train_intrinsics_outpaths = []

    # Initialize placeholders for testing output paths
    test_image_outpaths = []
    test_sparse_depth_outpaths = []
    test_validity_map_outpaths = []
    test_ground_truth_outpaths = []
    test_intrinsics_outpaths = []

    # For each dataset density, grab the sequences
    seq_dirpaths = glob.glob(os.path.join(data_dirpath, 'data', '*'))
    n_sample = 0

    for seq_dirpath in seq_dirpaths:
        # For each sequence, grab the images, sparse depths and valid maps
        image_paths = \
            sorted(glob.glob(os.path.join(seq_dirpath, 'image', '*.png')))
        sparse_depth_paths = \
            sorted(glob.glob(os.path.join(seq_dirpath, 'sparse_depth', '*.png')))
        validity_map_paths = \
            sorted(glob.glob(os.path.join(seq_dirpath, 'validity_map', '*.png')))
        ground_truth_paths = \
            sorted(glob.glob(os.path.join(seq_dirpath, 'ground_truth', '*.png')))
        intrinsics_path = os.path.join(seq_dirpath, 'K.txt')

        assert len(image_paths) == len(sparse_depth_paths)
        assert len(image_paths) == len(validity_map_paths)

        # Load intrinsics
        kin = np.loadtxt(intrinsics_path)

        intrinsics_refpath = \
            os.path.join(*intrinsics_path.split(os.sep)[2:])
        intrinsics_outpath = \
            os.path.join(VOID_OUTPUT_DIRPATH, intrinsics_refpath[:-3] + 'npy')
        image_out_dirpath = \
            os.path.join(os.path.dirname(intrinsics_outpath), 'image')

        if not os.path.exists(image_out_dirpath):
            os.makedirs(image_out_dirpath)

        # Save intrinsics
        np.save(intrinsics_outpath, kin)

        if seq_dirpath.split(os.sep)[-1] in test_seq_dirpaths:
            start_idx = 0
            offset_idx = 0
        else:
            # Skip first stationary 30 frames (1 second) and skip every 10
            start_idx = 30
            offset_idx = 10

        pool_input = []
        for idx in range(start_idx, len(image_paths)-offset_idx-start_idx):
            pool_input.append((
                image_paths[idx-offset_idx],
                image_paths[idx],
                image_paths[idx+offset_idx],
                sparse_depth_paths[idx],
                validity_map_paths[idx],
                ground_truth_paths[idx]))

        with mp.Pool() as pool:
            pool_results = pool.map(process_frame, pool_input)

            for result in pool_results:
                image_refpath, \
                    image_outpath, \
                    sparse_depth_outpath, \
                    validity_map_outpath, \
                    ground_truth_outpath = result

                # Split into training, testing and unused testing sets
                if image_refpath in train_image_paths:
                    train_image_outpaths.append(image_outpath)
                    train_sparse_depth_outpaths.append(sparse_depth_outpath)
                    train_validity_map_outpaths.append(validity_map_outpath)
                    train_ground_truth_outpaths.append(ground_truth_outpath)
                    train_intrinsics_outpaths.append(intrinsics_outpath)
                elif image_refpath in test_image_paths:
                    test_image_outpaths.append(image_outpath)
                    test_sparse_depth_outpaths.append(sparse_depth_outpath)
                    test_validity_map_outpaths.append(validity_map_outpath)
                    test_ground_truth_outpaths.append(ground_truth_outpath)
                    test_intrinsics_outpaths.append(intrinsics_outpath)
                else:
                    raise ValueError('Path not in training or testing set.')

        n_sample = n_sample + len(pool_input)

        print('Completed processing {} examples for sequence={}'.format(
            len(pool_input), seq_dirpath))

    print('Completed processing {} examples for density={}'.format(n_sample, data_dirpath))

    void_train_image_filepath, \
        void_train_sparse_depth_filepath, \
        void_train_validity_map_filepath, \
        void_train_ground_truth_filepath, \
        void_train_intrinsics_filepath = train_filepaths

    print('Storing training image file paths into: %s' % void_train_image_filepath)
    data_utils.write_paths(
        void_train_image_filepath, train_image_outpaths)

    print('Storing training sparse depth file paths into: %s' % void_train_sparse_depth_filepath)
    data_utils.write_paths(
        void_train_sparse_depth_filepath, train_sparse_depth_outpaths)

    print('Storing training validity map file paths into: %s' % void_train_validity_map_filepath)
    data_utils.write_paths(
        void_train_validity_map_filepath, train_validity_map_outpaths)

    print('Storing training groundtruth depth file paths into: %s' % void_train_ground_truth_filepath)
    data_utils.write_paths(
        void_train_ground_truth_filepath, train_ground_truth_outpaths)

    print('Storing training camera intrinsics file paths into: %s' % void_train_intrinsics_filepath)
    data_utils.write_paths(
        void_train_intrinsics_filepath, train_intrinsics_outpaths)

    void_test_image_filepath, \
        void_test_sparse_depth_filepath, \
        void_test_validity_map_filepath, \
        void_test_ground_truth_filepath, \
        void_test_intrinsics_filepath = test_filepaths

    print('Storing testing image file paths into: %s' % void_test_image_filepath)
    data_utils.write_paths(
        void_test_image_filepath, test_image_outpaths)

    print('Storing testing sparse depth file paths into: %s' % void_test_sparse_depth_filepath)
    data_utils.write_paths(
        void_test_sparse_depth_filepath, test_sparse_depth_outpaths)

    print('Storing testing validity map file paths into: %s' % void_test_validity_map_filepath)
    data_utils.write_paths(
        void_test_validity_map_filepath, test_validity_map_outpaths)

    print('Storing testing groundtruth depth file paths into: %s' % void_test_ground_truth_filepath)
    data_utils.write_paths(
        void_test_ground_truth_filepath, test_ground_truth_outpaths)

    print('Storing testing camera intrinsics file paths into: %s' % void_test_intrinsics_filepath)
    data_utils.write_paths(
        void_test_intrinsics_filepath, test_intrinsics_outpaths)
