from setuptools import setup

setup(
    name="astra-dirview",
    version="1.0.0",
    py_modules=["dirview", "core"],
    entry_points={
        "console_scripts": [
            "astra-dirview = dirview:main",
        ],
    },
)