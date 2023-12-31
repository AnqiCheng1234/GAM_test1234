# Copyright Niantic 2019. Patent Pending. All rights reserved.
#
# This software is licensed under the terms of the Monodepth2 licence
# which allows for non-commercial use only, the full terms of which are made
# available in the LICENSE file.

from __future__ import absolute_import, division, print_function

import os
import argparse

class GAMDepthOptions:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="GAMDepth options")

        # PATHS
        self.parser.add_argument("--data_path",
                                 type=str,
                                 help="path to the training data",
                                 required=True)
        self.parser.add_argument("--train_split",
                                 type=str,
                                 help="path to the train split",
                                 default='splits/nyu_train.txt')
        self.parser.add_argument("--val_split",
                                 type=str,
                                 help="path to the val split",
                                 default='./splits/nyu_test.txt')
        self.parser.add_argument("--vps_path",
                                 type=str,
                                 help="path to the vps",
                                 required=True)
        self.parser.add_argument("--seg_path",
                                 type=str,
                                 help="path to the seg",
                                 required=True)
        self.parser.add_argument("--val_path",
                                 type=str,
                                 help="path to the testing set",
                                 required=True)
        self.parser.add_argument("--log_dir",
                                 type=str,
                                 help="log directory",
                                 required=True)

        # TRAINING options
        self.parser.add_argument("--model_name",
                                 type=str,
                                 help="the name of the folder to save the model in path (logs/model_name/)",
                                 default="TEST",
                                 required=True)
        self.parser.add_argument("--num_layers",
                                 type=int,
                                 help="number of resnet layers",
                                 default=18)
        self.parser.add_argument("--train_dataset",
                                 type=str,
                                 help="dataset to train on",
                                 default="nyu")
        self.parser.add_argument("--eval_dataset",
                                 type=str,
                                 help="dataset to train on",
                                 default="nyu",
                                 choices=["nyu", "scannet", 'interior'])

        # data                        
        self.parser.add_argument("--height",
                                 type=int,
                                 help="input image height(nyu/kitti)=288/192",
                                 default=288)
        self.parser.add_argument("--width",
                                 type=int,
                                 help="input image width(nyu/kitti)=384/640",
                                 default=384)
        self.parser.add_argument("-d2n_nei",
                                 type=int,
                                 help="depth2normal neighborhood(3 denotes 7x7)",
                                 default=3)
        self.parser.add_argument("--scales",
                                 nargs="+",
                                 type=int,
                                 help="scales used in the loss",
                                 default=[0])
        self.parser.add_argument("--min_depth",
                                 type=float,
                                 help="minimum depth for both nyu and kitti",
                                 default=0.1)
        self.parser.add_argument("--max_depth",
                                 type=float,
                                 help="max depth(nyu/kitti)=10.0/100.0",
                                 default=10.0)
        # self.parser.add_argument("--split",
        #                          type=str,
        #                          default='eigen')
        self.parser.add_argument("--frame_ids",
                                 nargs="+",
                                 type=int,
                                 default= [0, -4,-3, -2, -1, 1, 2, 3, 4])
        self.parser.add_argument("--frame_ids_to_train",                       
                                 nargs="+",
                                 type=int,
                                 default=[0, -2, -1, 1, 2])

        # OPTIMIZATION options
        self.parser.add_argument("--batch_size",
                                 type=int,
                                 help="batch size",
                                 default=16,
                                 required=True)
        self.parser.add_argument("--learning_rate",
                                 type=float,
                                 help="learning rate",
                                 default=1e-4)
        self.parser.add_argument("--num_epochs",
                                 type=int,
                                 help="number of epochs(nyu/kitti)=50/20",
                                 default=50,
                                 required=True)
        self.parser.add_argument("--start_epoch",
                                 type=int,
                                 help="if load model weights_1, want to start trainning from 2, set start_epoch=2",
                                 default=0,
                                 required=True)
        self.parser.add_argument("--scheduler_step_size",
                                 nargs="+",
                                 type=int,
                                 help="step size of the scheduler(nyu/kitti)=[26,36]/[15]",
                                 default=[26, 36])

        # ABLATION options
        self.parser.add_argument("--using_GAM",
                                 help="Using disp2seg planar loss",
                                 default="GAM",
                                 choices=["GAM", "keypoints", "averaging"])
        self.parser.add_argument("--using_seg",
                                 help="Using norm and vps to compute cos loss",
                                 default=True,
                                 action="store_true")

        # SYSTEM options
        self.parser.add_argument("--num_workers",
                                 type=int,
                                 help="number of dataloader workers",
                                 default=6)

        # LOADING options
        self.parser.add_argument("--load_weights_folder",
                                 type=str,
                                 help="name of model to load",
                                 required=True)
        self.parser.add_argument("--models_to_load",
                                 nargs="+",
                                 type=str,
                                 help="models to load",
                                 default=["encoder", "depth", "pose_encoder", "pose"])
        self.parser.add_argument("--weights_init",
                                 nargs="+",
                                 type=str,
                                 default='pretrained')

        # LOGGING options
        self.parser.add_argument("--log_frequency",
                                 type=int,
                                 help="number of batches between each tensorboard log",
                                 default=2000)
        self.parser.add_argument("--save_frequency",
                                 type=int,
                                 help="number of epochs between each save",
                                 default=1)

        # EVALUATION options
        self.parser.add_argument("--pred_depth_scale_factor",
                                 help="if set multiplies predictions by this number",
                                 type=float,
                                 default=1)
        self.parser.add_argument("--post_process",
                                 help="if set will perform the flipping post processing "
                                      "from the original monodepth paper",
                                action="store_true")
        self.parser.add_argument("--disable_median_scaling",
                                 help="if set disables median scaling in evaluation",
                                 action="store_true")

        # LAMBDA losses factor
        self.parser.add_argument("--lambda_seg",
                                 help="weights for semantic constraints when train depth",
                                 type=float,
                                 default=0.1)
        self.parser.add_argument("--lamda_disparity_smoothness",
                                 type=float,
                                 help="disparity smoothness weight",
                                 default=1e-3)
        self.parser.add_argument("--lambda_norm_reg",                                      
                                  help="weights for cos(norm,vps) consistency when train depth",
                                  type=float,
                                  default=0.05)
        self.parser.add_argument("--lambda_planar_reg",
                                 help="weights for planar consistency when train depth",
                                 type=float,
                                 default=0.1)
        self.parser.add_argument("--planar_thresh",                                      
                                 help="thresh of planar area mask",
                                 type=float,
                                 default=200)

        # GAM factor
        self.parser.add_argument("--beta_GAM",
                                 help="balance the weights between textureless and texture-rich regions",
                                 type=float,
                                 default=0.1)
        self.parser.add_argument("--gamma1_GAM",
                                 type=float,
                                 default=0.1)
        self.parser.add_argument("--gamma2_GAM",
                                 type=float,
                                 default=40)


    def parse(self):
        self.options = self.parser.parse_args()
        return self.options
