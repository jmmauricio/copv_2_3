from pydae.bmapu import bmapu_builder
import json

M = 2
N = 3
grid = bmapu_builder.bmapu(f'./pv_{M}_{N}.json')

grid.build(f'pv_{M}_{N}')


