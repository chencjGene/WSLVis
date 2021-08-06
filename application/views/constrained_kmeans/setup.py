
import os
from setuptools import setup, Extension
from Cython.Build import cythonize
try:
    from numpy import get_include
except:
    def get_include():
        # Defer import to later
        from numpy import get_include
        return get_include()


extensions = [
    Extension("_k_means", ["_k_means.pyx"],
              include_dirs=[get_include()]),
]

CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 1))) and cythonize is not None

compiler_directives = {"language_level": 3, "embedsignature": True}
extensions = cythonize(extensions, compiler_directives=compiler_directives)



setup(
    ext_modules=extensions,
    extras_require={
        "docs": ["sphinx", "sphinx-rtd-theme"]
    }
)