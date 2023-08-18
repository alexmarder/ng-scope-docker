from setuptools import setup, find_packages

setup(
    name="ng-scope-docker",
    version='0.1',
    author='Alex Marder',
    # author_email='notlisted',
    description="Wrapper for modified NG-Scope.",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ngdock=ng_scope_docker.run:main',
        ],
    },
    install_requires=['libconf'],
    zip_safe=False,
    include_package_data=True,
    python_requires='>3.4'
)
