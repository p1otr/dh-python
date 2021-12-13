from setuptools import setup, Extension

setup_args = dict(
    ext_modules = [
        Extension(
            'foo.ext',
            ['foo/ext.c'],
            py_limited_api = True,
        )
    ]
)
setup(**setup_args)
