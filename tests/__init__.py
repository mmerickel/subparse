import os
import sys

here = os.path.dirname(__file__)
packages_dir = os.path.join(here, 'fake_packages')
for pkg in os.listdir(packages_dir):
    sys.path.insert(0, os.path.join(packages_dir, pkg))
