import setuptools

with open("readme.rst", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='labml_db',
    version='0.0.2',
    author="Varuna Jayasiri, Nipun Wijerathne",
    author_email="vpjayasiri@gmail.com, hnipun@gmail.com",
    description="ORM for JSON/YAML file based DB",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/lab-ml/db",
    project_urls={
        'Documentation': 'https://lab-ml.com/'
    },
    packages=setuptools.find_packages(exclude=('test',
                                               'test.*')),
    install_requires=['pyyaml>=5.3.1'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='database,json,yaml',
)
