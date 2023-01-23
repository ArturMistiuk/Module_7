from setuptools import setup, find_namespace_packages

setup(
    name='clean_folder',
    version='1.0.0',
    description='This is a script that will parse the specified folder.',
    url='https://github.com/ArturMistiuk/clean_folder',
    author='Artur Mistiuk',
    author_email='mistiuk.artur@gmail.com',
    license='MIT',
    packages=find_namespace_packages(),
    include_package_data = True,
    install_requires=['setuptools', 'wheel'],
    entry_points = {'console_scripts': ['clean-folder=clean_folder.clean:main']}
)