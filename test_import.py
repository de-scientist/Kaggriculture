#!/usr/bin/env python3
import sys
import os

print('Python version:', sys.version)
print('Python executable:', sys.executable)

# Check current directory
print('Current dir:', os.getcwd())
print('Files in E:/Kaggriculture:', os.listdir('E:/Kaggriculture'))

# Try to import the module
try:
    import agent.optimization.crop_optimizer
    print('Successfully imported agent.optimization.crop_optimizer')
    print('Module file:', agent.optimization.crop_optimizer.__file__)
except Exception as e:
    print('Import failed:', e)
    import traceback
    traceback.print_exc()
