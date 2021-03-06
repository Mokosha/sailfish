import unittest
from dummy import *

from sailfish.backend_dummy import DummyBackend
from sailfish.config import LBConfig
from sailfish.lb_base import LBSim

class TestCase2D(unittest.TestCase):
    lattice_size = 64, 64

    def setUp(self):
        config = LBConfig()
        config.init_iters = 0
        config.seed = 0
        config.precision = 'single'
        config.block_size = 8
        config.mem_alignment = 8
        config.lat_nx, config.lat_ny = self.lattice_size
        config.logger = DummyLogger()
        config.grid = 'D2Q9'
        self.sim = LBSim(config)
        self.config = config
        self.backend = DummyBackend()


class TestCase3D(unittest.TestCase):
    lattice_size = 32, 32, 16

    def setUp(self):
        config = LBConfig()
        config.init_iters = 0
        config.seed = 0
        config.precision = 'single'
        config.block_size = 8
        config.mem_alignment = 8
        config.lat_nx, config.lat_ny, config.lat_nz = self.lattice_size
        config.logger = DummyLogger()
        config.grid = 'D3Q19'
        self.sim = LBSim(config)
        self.backend = DummyBackend()
