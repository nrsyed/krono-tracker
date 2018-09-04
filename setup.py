from setuptools import setup

setup(
    name="krono-tracker",
    version="0.1",
    description="Simple terminal-based time tracking utility",
    url="https://github.com/nrsyed/krono-tracker",
    author="Najam R Syed",
    author_email="najam.r.syed@gmail.com",
    license="GPL",
    packages=["krono"],
    entry_points={
        "console_scripts": ["krono = krono.__main__:main"]},
    zip_safe=True)
