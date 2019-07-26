from setuptools import setup, find_packages

setup(
    name="pyweben",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        'tornado',
        'sanic',
        'gevent',
        'django',
        'click',
    ],
    include_package_data=True,
    python_requires=">=3",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    zip_safe=False,
    entry_points={"console_scripts": ['pyweben=pyweben.__main__:cli']}
)
