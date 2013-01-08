#!/usr/bin/python

"""Converts npz data files to VTK files.

Usage:
    ./npz_to_vti.py <file.npz>
"""

__author__ = 'Michal Januszewski'
__email__ = 'sailfish-cfd@googlegroups.com'
__license__ = 'LGPL3'

import os
import sys
import numpy as np

os.environ['ETS_TOOLKIT'] = 'null'

filename = sys.argv[1]
src_data = np.load(filename)

max_len = 0
for field in src_data.files:
    max_len = max(len(src_data[field].shape), max_len)

field = src_data[src_data.files[0]]
shape = None

# 3D
if max_len == 4:
    dim = 3
    if len(field.shape) == 3:
        shape = field.shape
    else:
        shape = field.shape[1:]
# 2D:
elif max_len == 3:
    dim = 2
    if len(field.shape) == 2:
        shape = field.shape
    else:
        shape = field.shape[1:]
else:
    raise ValueError('Unexpected field shape length %d' % max_len)

def use_tvtk(idata):

    first = True

# Only process scalar fields.
    for field in src_data.files:
        if len(src_data[field].shape) == max_len:
            continue

        if first:
            idata.point_data.scalars = src_data[field].flatten()
            idata.point_data.scalars.name = field
            first = False
        else:
            t = idata.point_data.add_array(src_data[field].flatten())
            idata.point_data.get_array(t).name = field

# Only process vector fields.
    for field in src_data.files:
        if len(src_data[field].shape) != max_len:
            continue

        f = src_data[field]

        if dim == 3:
            tmp = idata.point_data.add_array(np.c_[f[0].flatten(),
                                         f[1].flatten(), f[2].flatten()])
        else:
            tmp = idata.point_data.add_array(np.c_[f[0].flatten(),
                                         f[1].flatten(),
                                         np.zeros_like(f[0].flatten())])
        idata.point_data.get_array(tmp).name = field

    if dim == 3:
        idata.dimensions = list(reversed(shape))
    else:
        idata.dimensions = list(reversed(shape)) + [1]

    out_filename = filename.replace('.npz', '.vti')
    w = tvtk.XMLImageDataWriter(input=idata, file_name=out_filename)
    w.write()

def use_vtk():
    from vtk import *

    idata = vtkImageData()
    idata.SetSpacing(1, 1, 1)
    idata.SetOrigin(0, 0, 0)

    first = True

    # Only process scalar fields.
    for field in src_data.files:
        if len(src_data[field].shape) == max_len:
            continue

        scalars = vtkDoubleArray()
        for s in src_data[field].flatten():
            scalars.InsertNextValue(s)
        
        if first:
            idata.GetPointData().SetScalars(scalars)
            idata.GetPointData().GetScalars().SetName(field)
            first = False
        else:
            t = idata.GetPointData().AddArray(scalars)
            idata.GetPointData().GetArray(t).SetName(field)

    # Only process vector fields.
    for field in src_data.files:
        if len(src_data[field].shape) != max_len:
            continue

        f = src_data[field]
        xs = f[0].flatten()
        ys = f[1].flatten()
        zs = f[2].flatten() if dim == 3 else np.zeros_like(xs)

        vectors = vtkDoubleArray()
        vectors.SetNumberOfComponents(3)

        for [x, y, z] in np.c_[xs, ys, zs]:
            vectors.InsertNextTuple3(x, y, z)

        t = idata.GetPointData().AddArray(vectors)
        idata.GetPointData().GetArray(t).SetName(field)

    revl = list(reversed(shape))
    idata.SetDimensions(revl[0], revl[1], revl[2] if dim == 3 else 1)

    out_filename = filename.replace('.npz', '.vti')
    w = vtkXMLImageDataWriter()
    w.SetInput(idata)
    w.SetFileName(out_filename)
    w.write()

try:
    from tvtk.api import tvtk
    idata = tvtk.ImageData(spacing=(1, 1, 1), origin=(0, 0, 0))
    use_tvtk(idata)
except ImportError:
    use_vtk()    

