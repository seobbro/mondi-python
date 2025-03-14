'''
Authors:
Tian Yu Liu <tianyu@cs.ucla.edu>
Parth Agrawal <parthagrawal24@ucla.edu>
Allison Chen <allisonchen2@ucla.edu>
Alex Wong <alex.wong@yale.edu>

If you use this code, please cite the following paper:
T.Y. Liu, P. Agrawal, A. Chen, B.W. Hong, and A. Wong. Monitored Distillation for Positive Congruent Depth Completion.
https://arxiv.org/abs/2203.16034

@inproceedings{liu2022monitored,
  title={Monitored distillation for positive congruent depth completion},
  author={Liu, Tian Yu and Agrawal, Parth and Chen, Allison and Hong, Byung-Woo and Wong, Alex},
  booktitle={European Conference on Computer Vision},
  year={2022},
  organization={Springer}
}
'''

import torch

def activation_func(activation_fn):
    '''
    Select activation function

    Arg(s):
        activation_fn : str
            name of activation function
    '''

    if 'linear' in activation_fn:
        return None
    elif 'leaky_relu' in activation_fn:
        return torch.nn.LeakyReLU(negative_slope=0.20, inplace=True)
    elif 'relu' in activation_fn:
        return torch.nn.ReLU()
    elif 'elu' in activation_fn:
        return torch.nn.ELU()
    elif 'sigmoid' in activation_fn:
        return torch.nn.Sigmoid()
    else:
        raise ValueError('Unsupported activation function: {}'.format(activation_fn))


'''
Network layers
'''
class Conv2d(torch.nn.Module):
    '''
    2D convolution class

    Arg(s):
        in_channels : int
            number of input channels
        out_channels : int
            number of output channels
        kernel_size : int
            size of kernel
        stride : int
            stride of convolution
        weight_initializer : str
            kaiming_normal, kaiming_uniform, xavier_normal, xavier_uniform
        activation_func : func
            activation function after convolution
        use_batch_norm : bool
            if set, then applied batch normalization
    '''

    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size=3,
                 stride=1,
                 weight_initializer='kaiming_uniform',
                 activation_func=torch.nn.LeakyReLU(negative_slope=0.10, inplace=True),
                 use_batch_norm=False):
        super(Conv2d, self).__init__()

        self.use_batch_norm = use_batch_norm
        padding = kernel_size // 2

        self.conv = torch.nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            bias=False)

        # Select the type of weight initialization, by default kaiming_uniform
        if weight_initializer == 'kaiming_normal':
            torch.nn.init.kaiming_normal_(self.conv.weight)
        elif weight_initializer == 'xavier_normal':
            torch.nn.init.xavier_normal_(self.conv.weight)
        elif weight_initializer == 'xavier_uniform':
            torch.nn.init.xavier_uniform_(self.conv.weight)

        self.activation_func = activation_func

        if self.use_batch_norm:
            self.batch_norm = torch.nn.BatchNorm2d(out_channels)

    def forward(self, x):
        conv = self.conv(x)
        conv = self.batch_norm(conv) if self.use_batch_norm else conv

        if self.activation_func is not None:
            return self.activation_func(conv)
        else:
            return conv


class DepthwiseSeparableConv2d(torch.nn.Module):
    '''
    Depthwise separable convolution class
    Performs
    1. separate k x k convolution per channel (depth-wise)
    2. 1 x 1 convolution across all channels (point-wise)

    Arg(s):
        in_channels : int
            number of input channels
        out_channels : int
            number of output channels
        kernel_size : int
            size of kernel (k x k)
        stride : int
            stride of convolution
        weight_initializer : str
            kaiming_normal, kaiming_uniform, xavier_normal, xavier_uniform
        activation_func : func
            activation function after convolution
        use_batch_norm : bool
            if set, then applied batch normalization
    '''

    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size=3,
                 stride=1,
                 weight_initializer='kaiming_uniform',
                 activation_func=torch.nn.LeakyReLU(negative_slope=0.10, inplace=True),
                 use_batch_norm=False):
        super(DepthwiseSeparableConv2d, self).__init__()

        padding = kernel_size // 2

        self.use_batch_norm = use_batch_norm

        self.conv_depthwise = torch.nn.Conv2d(
            in_channels,
            in_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            bias=False,
            groups=in_channels)

        self.conv_pointwise = torch.nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=1,
            stride=1,
            padding=0,
            bias=False)

        # Select the type of weight initialization, by default kaiming_uniform
        if weight_initializer == 'kaiming_normal':
            torch.nn.init.kaiming_normal_(self.conv_depthwise.weight)
            torch.nn.init.kaiming_normal_(self.conv_pointwise.weight)
        elif weight_initializer == 'xavier_normal':
            torch.nn.init.xavier_normal_(self.conv_depthwise.weight)
            torch.nn.init.xavier_normal_(self.conv_pointwise.weight)
        elif weight_initializer == 'xavier_uniform':
            torch.nn.init.xavier_uniform_(self.conv_depthwise.weight)
            torch.nn.init.xavier_uniform_(self.conv_pointwise.weight)
        elif weight_initializer == 'kaiming_uniform':
            pass

        self.conv = torch.nn.Sequential(
            self.conv_depthwise,
            self.conv_pointwise)

        if self.use_batch_norm:
            self.batch_norm = torch.nn.BatchNorm2d(out_channels)

        self.activation_func = activation_func

    def forward(self, x):
        conv = self.conv(x)
        conv = self.batch_norm(conv) if self.use_batch_norm else conv

        if self.activation_func is not None:
            return self.activation_func(conv)
        else:
            return conv


class TransposeConv2d(torch.nn.Module):
    '''
    Transpose convolution class

    Arg(s):
        in_channels : int
            number of input channels
        out_channels : int
            number of output channels
        kernel_size : int
            size of kernel (k x k)
        weight_initializer : str
            kaiming_normal, kaiming_uniform, xavier_normal, xavier_uniform
        activation_func : func
            activation function after convolution
        use_batch_norm : bool
            if set, then applied batch normalization
    '''

    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size=3,
                 weight_initializer='kaiming_uniform',
                 activation_func=torch.nn.LeakyReLU(negative_slope=0.10, inplace=True),
                 use_batch_norm=False):
        super(TransposeConv2d, self).__init__()

        self.use_batch_norm = use_batch_norm
        padding = kernel_size // 2

        self.deconv = torch.nn.ConvTranspose2d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            stride=2,
            padding=padding,
            output_padding=1,
            bias=False)

        # Select the type of weight initialization, by default kaiming_uniform
        if weight_initializer == 'kaiming_normal':
            torch.nn.init.kaiming_normal_(self.conv.weight)
        elif weight_initializer == 'xavier_normal':
            torch.nn.init.xavier_normal_(self.conv.weight)
        elif weight_initializer == 'xavier_uniform':
            torch.nn.init.xavier_uniform_(self.conv.weight)

        self.activation_func = activation_func

        if self.use_batch_norm:
            self.batch_norm = torch.nn.BatchNorm2d(out_channels)

    def forward(self, x):
        deconv = self.deconv(x)
        deconv = self.batch_norm(deconv) if self.use_batch_norm else deconv
        if self.activation_func is not None:
            return self.activation_func(deconv)
        else:
            return deconv


class UpConv2d(torch.nn.Module):
    '''
    Up-convolution (upsample + convolution) block class

    Arg(s):
        in_channels : int
            number of input channels
        out_channels : int
            number of output channels
        shape : list[int]
            two element tuple of ints (height, width)
        kernel_size : int
            size of kernel (k x k)
        weight_initializer : str
            kaiming_normal, kaiming_uniform, xavier_normal, xavier_uniform
        activation_func : func
            activation function after convolution
        use_batch_norm : bool
            if set, then applied batch normalization
    '''

    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size=3,
                 weight_initializer='kaiming_uniform',
                 activation_func=torch.nn.LeakyReLU(negative_slope=0.10, inplace=True),
                 use_batch_norm=False):
        super(UpConv2d, self).__init__()

        self.conv = Conv2d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            stride=1,
            weight_initializer=weight_initializer,
            activation_func=activation_func,
            use_batch_norm=use_batch_norm)

    def forward(self, x, shape):
        upsample = torch.nn.functional.interpolate(x, size=shape)
        conv = self.conv(upsample)
        return conv


'''
Network encoder blocks
'''
class ResNetBlock(torch.nn.Module):
    '''
    Basic ResNet block class

    Arg(s):
        in_channels : int
            number of input channels
        out_channels : int
            number of output channels
        stride : int
            stride of convolution
        weight_initializer : str
            kaiming_normal, kaiming_uniform, xavier_normal, xavier_uniform
        activation_func : func
            activation function after convolution
        use_batch_norm : bool
            if set, then applied batch normalization
    '''

    def __init__(self,
                 in_channels,
                 out_channels,
                 stride=1,
                 weight_initializer='kaiming_uniform',
                 activation_func=torch.nn.LeakyReLU(negative_slope=0.10, inplace=True),
                 use_batch_norm=False):
        super(ResNetBlock, self).__init__()

        self.activation_func = activation_func

        self.conv1 = Conv2d(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            weight_initializer=weight_initializer,
            activation_func=activation_func,
            use_batch_norm=use_batch_norm)

        self.conv2 = Conv2d(
            out_channels,
            out_channels,
            kernel_size=3,
            stride=1,
            weight_initializer=weight_initializer,
            activation_func=activation_func,
            use_batch_norm=use_batch_norm)

        self.projection = Conv2d(
            in_channels,
            out_channels,
            kernel_size=1,
            stride=stride,
            weight_initializer=weight_initializer,
            activation_func=None,
            use_batch_norm=False)

    def forward(self, x):
        # Perform 2 convolutions
        conv1 = self.conv1(x)
        conv2 = self.conv2(conv1)

        # Perform projection if (1) shape does not match (2) channels do not match
        in_shape = list(x.shape)
        out_shape = list(conv2.shape)
        if in_shape[2:4] != out_shape[2:4] or in_shape[1] != out_shape[1]:
            X = self.projection(x)
        else:
            X = x

        # f(x) + x
        return self.activation_func(conv2 + X)


class ResNetBottleneckBlock(torch.nn.Module):
    '''
    ResNet bottleneck block class

    Arg(s):
        in_channels : int
            number of input channels
        out_channels : int
            number of output channels
        stride : int
            stride of convolution
        weight_initializer : str
            kaiming_normal, kaiming_uniform, xavier_normal, xavier_uniform
        activation_func : func
            activation function after convolution
        use_batch_norm : bool
            if set, then applied batch normalization
    '''

    def __init__(self,
                 in_channels,
                 out_channels,
                 stride=1,
                 weight_initializer='kaiming_uniform',
                 activation_func=torch.nn.LeakyReLU(negative_slope=0.10, inplace=True),
                 use_batch_norm=False):
        super(ResNetBottleneckBlock, self).__init__()

        self.activation_func = activation_func

        self.conv1 = Conv2d(
            in_channels,
            out_channels,
            kernel_size=1,
            stride=1,
            weight_initializer=weight_initializer,
            activation_func=activation_func,
            use_batch_norm=use_batch_norm)

        self.conv2 = Conv2d(
            out_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            weight_initializer=weight_initializer,
            activation_func=activation_func,
            use_batch_norm=use_batch_norm)

        self.conv3 = Conv2d(
            out_channels,
            4 * out_channels,
            kernel_size=1,
            stride=1,
            weight_initializer=weight_initializer,
            activation_func=activation_func,
            use_batch_norm=use_batch_norm)

        self.projection = Conv2d(
            in_channels,
            4 * out_channels,
            kernel_size=1,
            stride=stride,
            weight_initializer=weight_initializer,
            activation_func=None,
            use_batch_norm=False)

    def forward(self, x):
        # Perform 2 convolutions
        conv1 = self.conv1(x)
        conv2 = self.conv2(conv1)
        conv3 = self.conv3(conv2)

        # Perform projection if (1) shape does not match (2) channels do not match
        in_shape = list(x.shape)
        out_shape = list(conv2.shape)
        if in_shape[2:4] != out_shape[2:4] or in_shape[1] != out_shape[1]:
            X = self.projection(x)
        else:
            X = x

        # f(x) + x
        return self.activation_func(conv3 + X)


class VGGNetBlock(torch.nn.Module):
    '''
    VGGNet block class

    Arg(s):
        in_channels : int
            number of input channels
        out_channels : int
            number of output channels
        n_conv : int
            number of convolution layers
        stride : int
            stride of convolution
        weight_initializer : str
            kaiming_normal, kaiming_uniform, xavier_normal, xavier_uniform
        activation_func : func
            activation function after convolution
        use_batch_norm : bool
            if set, then applied batch normalization
        use_depthwise_separable : bool
            if set, then use depthwise separable convolutions instead of convolutions
    '''

    def __init__(self,
                 in_channels,
                 out_channels,
                 n_conv=1,
                 stride=1,
                 weight_initializer='kaiming_uniform',
                 activation_func=torch.nn.LeakyReLU(negative_slope=0.10, inplace=True),
                 use_batch_norm=False,
                 use_depthwise_separable=False):
        super(VGGNetBlock, self).__init__()

        if use_depthwise_separable:
            conv2d = DepthwiseSeparableConv2d
        else:
            conv2d = Conv2d

        layers = []
        for n in range(n_conv - 1):
            conv = conv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                stride=1,
                weight_initializer=weight_initializer,
                activation_func=activation_func,
                use_batch_norm=use_batch_norm)
            layers.append(conv)
            in_channels = out_channels

        conv = conv2d(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            weight_initializer=weight_initializer,
            activation_func=activation_func,
            use_batch_norm=use_batch_norm)
        layers.append(conv)

        self.conv_block = torch.nn.Sequential(*layers)

    def forward(self, x):
        return self.conv_block(x)


class CalibratedBackprojectionBlock(torch.nn.Module):
    '''
    Calibrated backprojection (KB) layer class

    Arg(s):
        in_channels_image : int
            number of input channels for image (RGB) branch
        in_channels_depth : int
            number of input channels for depth branch
        in_channels_fused : int
            number of input channels for RGB 3D fusion branch
        n_filter_image : int
            number of filters for image (RGB) branch
        n_filter_depth : int
            number of filters for depth branch
        n_filter_fused : int
            number of filters for RGB 3D fusion branch
        n_convolution_image : int
            number of convolution layers in image branch
        n_convolution_depth : int
            number of convolution layers in depth branch
        n_convolution_fused : int
            number of convolution layers in RGB 3D fusion branch
        weight_initializer : str
            kaiming_normal, kaiming_uniform, xavier_normal, xavier_uniform
        activation_func : func
            activation function after convolution
        use_depthwise_separable : bool
            if set, then use depthwise separable convolutions instead of convolutions
    '''
    def __init__(self,
                 in_channels_image,
                 in_channels_depth,
                 in_channels_fused,
                 n_filter_image=48,
                 n_filter_depth=16,
                 n_filter_fused=48,
                 n_convolution_image=1,
                 n_convolution_depth=1,
                 n_convolution_fused=1,
                 weight_initializer='kaiming_uniform',
                 activation_func=torch.nn.LeakyReLU(negative_slope=0.10, inplace=True),
                 use_depthwise_separable=False):
        super(CalibratedBackprojectionBlock, self).__init__()

        self.conv_image = VGGNetBlock(
            in_channels=in_channels_image,
            out_channels=n_filter_image,
            n_conv=n_convolution_image,
            stride=2,
            weight_initializer=weight_initializer,
            activation_func=activation_func,
            use_depthwise_separable=use_depthwise_separable)

        self.conv_depth = VGGNetBlock(
            in_channels=in_channels_depth + 3,
            out_channels=n_filter_depth,
            n_conv=n_convolution_depth,
            stride=2,
            weight_initializer=weight_initializer,
            activation_func=activation_func,
            use_depthwise_separable=use_depthwise_separable)

        self.proj_depth = Conv2d(
            in_channels=in_channels_depth,
            out_channels=1,
            kernel_size=1,
            stride=1,
            weight_initializer=weight_initializer,
            activation_func=activation_func)

        self.conv_fused = Conv2d(
            in_channels=in_channels_fused + 3,
            out_channels=n_filter_fused,
            kernel_size=1,
            stride=2,
            weight_initializer=weight_initializer,
            activation_func=activation_func)

    def forward(self, image, depth, coordinates, fused=None):

        layers_fused = []

        # Obtain image (RGB) features
        conv_image = self.conv_image(image)

        # Obtain depth (Z) features
        conv_depth = self.conv_depth(torch.cat([depth, coordinates], dim=1))

        # Include image (RGB) features
        layers_fused.append(image)

        # Project depth features to 1 dimension
        z = self.proj_depth(depth)

        # Include backprojected 3D positional (XYZ) encoding: K^-1 [x y 1] z
        xyz = coordinates * z
        layers_fused.append(xyz)

        # Include previous RGBXYZ representation
        if fused is not None:
            layers_fused.append(fused)

        # Obtain fused (RGBXYZ) representation
        layers_fused = torch.cat(layers_fused, dim=1)
        conv_fused = self.conv_fused(layers_fused)

        return conv_image, conv_depth, conv_fused


'''
Network decoder blocks
'''
class DecoderBlock(torch.nn.Module):
    '''
    Decoder block with skip connections (U-Net)

    Arg(s):
        in_channels : int
            number of input channels
        skip_channels : int
            number of skip connection channels
        out_channels : int
            number of output channels
        weight_initializer : str
            kaiming_normal, kaiming_uniform, xavier_normal, xavier_uniform
        activation_func : func
            activation function after convolution
        use_batch_norm : bool
            if set, then applied batch normalization
        deconv_type : str
            deconvolution types: transpose, up
        use_depthwise_separable : bool
            if set, then use depthwise separable convolutions instead of convolutions
    '''

    def __init__(self,
                 in_channels,
                 skip_channels,
                 out_channels,
                 weight_initializer='kaiming_uniform',
                 activation_func=torch.nn.LeakyReLU(negative_slope=0.10, inplace=True),
                 use_batch_norm=False,
                 deconv_type='transpose',
                 use_depthwise_separable=False):
        super(DecoderBlock, self).__init__()

        self.skip_channels = skip_channels
        self.deconv_type = deconv_type

        if deconv_type == 'transpose':
            self.deconv = TransposeConv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                weight_initializer=weight_initializer,
                activation_func=activation_func,
                use_batch_norm=use_batch_norm)
        elif deconv_type == 'up':
            self.deconv = UpConv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                weight_initializer=weight_initializer,
                activation_func=activation_func,
                use_batch_norm=use_batch_norm)

        concat_channels = skip_channels + out_channels

        if use_depthwise_separable:
            conv2d = DepthwiseSeparableConv2d
        else:
            conv2d = Conv2d

        self.conv = conv2d(
            concat_channels,
            out_channels,
            kernel_size=3,
            stride=1,
            weight_initializer=weight_initializer,
            activation_func=activation_func,
            use_batch_norm=use_batch_norm)

    def forward(self, x, skip=None, shape=None):

        if self.deconv_type == 'transpose':
            deconv = self.deconv(x)
        elif self.deconv_type == 'up':

            if skip is not None:
                shape = skip.shape[2:4]
            elif shape is not None:
                pass
            else:
                n_height, n_width = x.shape[2:4]
                shape = (int(2 * n_height), int(2 * n_width))

            deconv = self.deconv(x, shape=shape)

        if self.skip_channels > 0:
            concat = torch.cat([deconv, skip], dim=1)
        else:
            concat = deconv

        return self.conv(concat)


'''
Utility function to pre-process sparse depth
'''
class OutlierRemoval(object):
    '''
    Class to perform outlier removal based on depth difference in local neighborhood

    Arg(s):
        kernel_size : int
            local neighborhood to consider
        threshold : float
            depth difference threshold
    '''

    def __init__(self, kernel_size=7, threshold=1.5):

        self.kernel_size = kernel_size
        self.threshold = threshold

    def remove_outliers(self, sparse_depth, validity_map):
        '''
        Removes erroneous measurements from sparse depth and validity map

        Arg(s):
            sparse_depth : torch.Tensor[float32]
                N x 1 x H x W tensor sparse depth
            validity_map : torch.Tensor[float32]
                N x 1 x H x W tensor validity map
        Returns:
            torch.Tensor[float32] : N x 1 x H x W sparse depth
            torch.Tensor[float32] : N x 1 x H x W validity map
        '''

        # Replace all zeros with large values
        max_value = 10 * torch.max(sparse_depth)
        sparse_depth_max_filled = torch.where(
            validity_map <= 0,
            torch.full_like(sparse_depth, fill_value=max_value),
            sparse_depth)

        # For each neighborhood find the smallest value
        padding = self.kernel_size // 2
        sparse_depth_max_filled = torch.nn.functional.pad(
            input=sparse_depth_max_filled,
            pad=(padding, padding, padding, padding),
            mode='constant',
            value=max_value)

        min_values = -torch.nn.functional.max_pool2d(
            input=-sparse_depth_max_filled,
            kernel_size=self.kernel_size,
            stride=1,
            padding=0)

        # If measurement differs a lot from minimum value then remove
        validity_map_clean = torch.where(
            min_values < sparse_depth - self.threshold,
            torch.zeros_like(validity_map),
            torch.ones_like(validity_map))

        # Update sparse depth and validity map
        validity_map_clean = validity_map * validity_map_clean
        sparse_depth_clean = sparse_depth * validity_map_clean

        return sparse_depth_clean, validity_map_clean


'''
Pose regression layer
'''
def pose_matrix(v, rotation_parameterization='axis'):
    '''
    Convert 6 DoF parameters to transformation matrix

    Arg(s):
        v : torch.Tensor[float32]
            N x 6 vector in the order of tx, ty, tz, rx, ry, rz
        rotation_parameterization : str
            axis
    Returns:
        torch.Tensor[float32] : N x 4 x 4 homogeneous transformation matrix
    '''

    # Select N x 3 element rotation vector
    r = v[..., :3]
    # Select N x 3 element translation vector
    t = v[..., 3:]

    if rotation_parameterization == 'axis':
        Rt = transformation_from_parameters(torch.unsqueeze(r, dim=1), t)
    else:
        raise ValueError('Unsupported rotation parameterization: {}'.format(rotation_parameterization))

    return Rt


'''
Utility functions for rotation
'''
def transformation_from_parameters(axisangle, translation, invert=False):
    """Convert the network's (axisangle, translation) output into a 4x4 matrix
    """
    R = rot_from_axisangle(axisangle)
    t = translation.clone()

    if invert:
        R = R.transpose(1, 2)
        t *= -1

    T = get_translation_matrix(t)

    if invert:
        M = torch.matmul(R, T)
    else:
        M = torch.matmul(T, R)

    return M

def rot_from_axisangle(vec):
    """Convert an axisangle rotation into a 4x4 transformation matrix
    (adapted from https://github.com/Wallacoloo/printipi)
    Input 'vec' has to be Bx1x3
    """
    angle = torch.norm(vec, 2, 2, True)
    axis = vec / (angle + 1e-7)

    ca = torch.cos(angle)
    sa = torch.sin(angle)
    C = 1 - ca

    x = axis[..., 0].unsqueeze(1)
    y = axis[..., 1].unsqueeze(1)
    z = axis[..., 2].unsqueeze(1)

    xs = x * sa
    ys = y * sa
    zs = z * sa
    xC = x * C
    yC = y * C
    zC = z * C
    xyC = x * yC
    yzC = y * zC
    zxC = z * xC

    rot = torch.zeros((vec.shape[0], 4, 4)).to(device=vec.device)

    rot[:, 0, 0] = torch.squeeze(x * xC + ca)
    rot[:, 0, 1] = torch.squeeze(xyC - zs)
    rot[:, 0, 2] = torch.squeeze(zxC + ys)
    rot[:, 1, 0] = torch.squeeze(xyC + zs)
    rot[:, 1, 1] = torch.squeeze(y * yC + ca)
    rot[:, 1, 2] = torch.squeeze(yzC - xs)
    rot[:, 2, 0] = torch.squeeze(zxC - ys)
    rot[:, 2, 1] = torch.squeeze(yzC + xs)
    rot[:, 2, 2] = torch.squeeze(z * zC + ca)
    rot[:, 3, 3] = 1

    return rot

def get_translation_matrix(translation_vector):
    """Convert a translation vector into a 4x4 transformation matrix
    """
    T = torch.zeros(translation_vector.shape[0], 4, 4).to(device=translation_vector.device)

    t = translation_vector.contiguous().view(-1, 3, 1)

    T[:, 0, 0] = 1
    T[:, 1, 1] = 1
    T[:, 2, 2] = 1
    T[:, 3, 3] = 1
    T[:, :3, 3, None] = t

    return T

def meshgrid(n_batch, n_height, n_width, device, homogeneous=True):
    '''
    Creates N x 2 x H x W meshgrid in x, y directions

    Arg(s):
        n_batch : int
            batch size
        n_height : int
            height of tensor
        n_width : int
            width of tensor
        device : torch.device
            device on which to create meshgrid
        homoegenous : bool
            if set, then add homogeneous coordinates (N x H x W x 3)
    Return:
        torch.Tensor[float32]: N x 2 x H x W meshgrid of x, y and 1 (if homogeneous)
    '''

    x = torch.linspace(start=0.0, end=n_width-1, steps=n_width, device=device)
    y = torch.linspace(start=0.0, end=n_height-1, steps=n_height, device=device)

    # Create H x W grids
    grid_y, grid_x = torch.meshgrid(y, x)

    if homogeneous:
        # Create 3 x H x W grid (x, y, 1)
        grid_xy = torch.stack([grid_x, grid_y, torch.ones_like(grid_x)], dim=0)
    else:
        # Create 2 x H x W grid (x, y)
        grid_xy = torch.stack([grid_x, grid_y], dim=0)

    grid_xy = torch.unsqueeze(grid_xy, dim=0) \
        .repeat(n_batch, 1, 1, 1)

    return grid_xy

def load_state_dict(model, state_dict):
    '''
    Load in the state dict, handle the case if the model was saved with nn.DataParallel

    Arg(s):
        model : torch model
            Model to load restore weights to
        state_dict : dictionary of weights
            from saved checkpoint
    Returns:
        torch model with restored weights
    '''

    try:
        model.load_state_dict(state_dict)

    # Exception thrown when keys unexpectedly have 'module.' at the front
    except Exception:
        cleaned_state_dict = {}
        # Create a new dictionary removing 'module.'
        for key, weights in state_dict.items():
            cleaned_state_dict[key[7:]] = weights
        model.load_state_dict(cleaned_state_dict)

    return model
