#!/usr/bin/env python
from distutils.core import setup
import os
import slither


if __name__ == "__main__":
    setup(name="slither",
          version=slither.__version__,
          author="Alexander Fabisch",
          author_email="afabisch@googlemail.com",
          license="New BSD",
          scripts=[os.path.join("bin", "slither"),
                   os.path.join("bin", "slither_server")],
          packages=["slither", "slither/gui"],
          package_data={"slither": ["resources/*"]},
          requires=["pyyaml", "numpy", "matplotlib",
                    "lxml", "beautifulsoup4", "sqlalchemy",
                    "pyproj", "Jinja2", "folium"])
