#!/usr/bin/env python -u

import numpy as np
from sailfish.geo import EqualSubdomainsGeometry3D
from sailfish.subdomain import Subdomain3D
from sailfish.node_type import NTFullBBWall
from sailfish.node_type import NTEquilibriumVelocity
from sailfish.controller import LBSimulationController
from sailfish.lb_single import LBFluidSim
from sailfish.lb_base import LBForcedSim

from vtk import *

class FibrinBlock(Subdomain3D):

    vel = 0.2

    def boundary_conditions(self, hx, hy, hz):
        print "Establishing boundary conditions..."
        lor = np.logical_or
        land = np.logical_and
        lnot = np.logical_not

        print "Defining wall boundaries..."
        wall_bc = NTFullBBWall
        wall_map = np.logical_or(
                        np.logical_or(hy == 0, hy == self.gy-1),
                        np.logical_or(hx == 0, hx == self.gx-1))
        self.set_node(wall_map, wall_bc)

        print "Defining velocity boundaries..."
        velocity_bc = NTEquilibriumVelocity
        velocity_map = land(lor(hz == 0, hz == self.gz - 1), lnot(wall_map))
        self.set_node(velocity_map, velocity_bc((0, 0, self.vel)))

        print "Defining fibrin boundaries..."
        self.load_fibrin_data()

        f_map = land(land(FibrinBlock.fibrin_map, lnot(wall_map)), lnot(velocity_map))
        self.set_node(f_map, wall_bc)

    def initial_conditions(self, sim, hx, hy, hz):
        sim.rho[:] = 1.0
        sim.vy[:] = 0.0
        sim.vx[:] = 0.0
        sim.vz[:] = 0.0

    @classmethod
    def set_fibrin_data_file(vtkfile):
        FibrinBlock.datafile = vtkfile

    def load_fibrin_data(self):
        reader = vtkXMLImageDataReader()
        reader.SetFileName(FibrinBlock.datafile)
        
        print "Loading fibrin data..."
        reader.Update()
        idata = reader.GetOutput()

        print "\tFibrin data dimensions: %s" % (idata.GetDimensions(),)
        domain_shape = (self.gz, self.gy, self.gx)
        data_shape = idata.GetDimensions()
        FibrinBlock.fibrin_map = np.zeros(domain_shape, dtype=np.float32)

        print "Mapping fibrin data..."
        xOffset = (data_shape[0] - domain_shape[2]) / 2
        yOffset = (data_shape[1] - domain_shape[1]) / 2
        for i in xrange(self.gx):
            for j in xrange(self.gy):
                for k in xrange(data_shape[2]):
                    FibrinBlock.fibrin_map[k+30][j][i] = idata.GetScalarComponentAsFloat(xOffset+i, yOffset+j, k, 0)

        FibrinBlock.fibrin_map = FibrinBlock.fibrin_map > 0.0

    @staticmethod
    def set_fibrin_data_file(vtkfile):
        FibrinBlock.datafile = vtkfile

class FibrinSimulation(LBFluidSim, LBForcedSim):
    subdomain = FibrinBlock

    @classmethod
    def update_defaults(cls, defaults):
        defaults.update({
            'lat_nx': 64,
            'lat_ny': 64,
            'lat_nz': 128,
            'grid': 'D3Q19'})

    @classmethod
    def modify_config(cls, config):
        pass

    @classmethod
    def add_options(cls, group, dim):
        LBFluidSim.add_options(group, dim)
        LBForcedSim.add_options(group, dim)
        group.add_argument('--fibrin_data', type=str, help='filename for the fibrin data',  default='')

    def __init__(self, config):
        super(FibrinSimulation, self).__init__(config)
        self.subdomain.set_fibrin_data_file(config.fibrin_data)


if __name__ == '__main__':
    ctrl = LBSimulationController(FibrinSimulation, EqualSubdomainsGeometry3D)
    ctrl.run()
