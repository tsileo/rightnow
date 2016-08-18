# coding: utf-8
import os

import yaml

CONFIG = {}
if os.path.exists('config.yaml'):
    print 'config loaded'
    CONFIG = yaml.load(open('config.yaml', 'rb').read())
    print CONFIG
