# Copyright Niantic 2019. Patent Pending. All rights reserved.
#
# This software is licensed under the terms of the Monodepth2 licence
# which allows for non-commercial use only, the full terms of which are made
# available in the LICENSE file.

from __future__ import absolute_import, division, print_function

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from collections import OrderedDict
from layers import *


class SegDecoder(nn.Module):
    def __init__(self, num_ch_enc, scales=range(4), num_output_channels=40, use_skips=True, pred_normal=False, upsample_mode='nearest'):
        super(SegDecoder, self).__init__()

        self.num_output_channels = num_output_channels
        self.use_skips = use_skips
        self.upsample_mode = upsample_mode
        self.scales = scales

        self.num_ch_enc = num_ch_enc
        self.num_ch_dec = np.array([16, 32, 64, 128, 256])

        self.pred_normal = pred_normal
        # decoder
        self.convs = OrderedDict()
        for i in range(4, -1, -1):
            # upconv_0
            num_ch_in = self.num_ch_enc[-1] if i == 4 else self.num_ch_dec[i + 1]
            num_ch_out = self.num_ch_dec[i]
            self.convs[("upconv", i, 0)] = ConvBlock(num_ch_in, num_ch_out)

            # upconv_1
            num_ch_in = self.num_ch_dec[i]
            if self.use_skips and i > 0:
                num_ch_in += self.num_ch_enc[i - 1]
            num_ch_out = self.num_ch_dec[i]
            self.convs[("upconv", i, 1)] = ConvBlock(num_ch_in, num_ch_out)

        self.normal_convs = {}
        for s in self.scales:
            self.convs[("dispconv", s)] = Conv3x3(self.num_ch_dec[s], self.num_output_channels)
            if self.pred_normal:
                self.normal_convs[("normalconv", s)] = Conv3x3(self.num_ch_dec[s], 3)

        self.decoder = nn.ModuleList(list(self.convs.values()))
        if self.pred_normal:
            self.normal_decoder = nn.ModuleList(list(self.normal_convs.values()))

        # self.sigmoid = nn.Sigmoid()
        self.softmax = nn.Softmax2d()

    def forward(self, input_features):
        self.outputs = {}

        # decoder
        x = input_features[-1]
        for i in range(4, -1, -1):
            x = self.convs[("upconv", i, 0)](x)
            x = [upsample(x, self.upsample_mode)]
            if self.use_skips and i > 0:
                x += [input_features[i - 1]]
            x = torch.cat(x, 1)
            x = self.convs[("upconv", i, 1)](x)
            if i in self.scales:
                self.outputs[("seg_pred", i)] = self.softmax(self.convs[("dispconv", i)](x))
                if self.pred_normal:
                    normal = self.normal_convs[("normalconv", i)](x)
                    self.outputs[("normal", i)] = F.normalize(normal, dim=1, p=2)

        return self.outputs
