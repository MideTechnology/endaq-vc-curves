import setuptools


INSTALL_REQUIRES = [
    "numpy",
    "scipy",
    "pandas",
    "idelib>=3.1.0",
    "backports.cached-property; python_version<'3.8'",
]

setuptools.setup(
    name="BSVP",
    author="Mide Technology",
    packages=setuptools.find_packages(exclude=["tests"])
    + [
        "common_utils." + i
        for i in setuptools.find_packages(where="common_utils", exclude="tests")
    ],
    test_suite="tests",
    install_requires=INSTALL_REQUIRES,
)
