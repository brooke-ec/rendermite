from typing import List
import numpy as np
import math

def multiply_matricies(*matricies) -> List[List[float]]:
    result = matricies[0]
    for mat in matricies[1:]:
        result = np.matmul(mat, result)
    return result

def scale_mat(x:float, y:float, z:float) -> List[List[float]]:
    return [[ x,  0,  0,  0],
            [ 0,  y,  0,  0],
            [ 0,  0,  z,  0],
            [ 0,  0,  0,  1]]

def rotx_mat(angle:float) -> List[List[float]]:
    angle = math.radians(angle)
    s = math.sin(angle)
    c = math.cos(angle)
    return [[ 1,  0,  0,  0],
            [ 0,  c, -s,  0],
            [ 0,  s,  c,  0],
            [ 0,  0,  0,  1]]

def roty_mat(angle:float) -> List[List[float]]:
    angle = math.radians(angle)
    s = math.sin(angle)
    c = math.cos(angle)
    return [[ c,  0,  s,  0],
            [ 0,  1,  0,  0],
            [-s,  0,  c,  0],
            [ 0,  0,  0,  1]]

def rotz_mat(angle:float) -> List[List[float]]:
    angle = math.radians(angle)
    s = math.sin(angle)
    c = math.cos(angle)
    return [[ c, -s,  0,  0],
            [ s,  c,  0,  0],
            [ 0,  0,  1,  0],
            [ 0,  0,  0,  1]]

def trans_mat(x:float, y:float, z:float) -> List[List[float]]:
    return [[ 1,  0,  0,  x],
            [ 0,  1,  0,  y],
            [ 0,  0,  1,  z],
            [ 0,  0,  0,  1]]