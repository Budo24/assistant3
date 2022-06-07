'''Setup'''

import setuptools

import platform

system = platform.system()
architecture = platform.architecture()[0]

with open('README.rst', 'r') as fh:
    long_description = fh.read()

# Create OS-dependent, but Python-independent wheels.
try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    cmdclass = {}
else:
    class BdistWheelTagName(bdist_wheel):
        """undependent"""
        
        def get_tag(self):
            abi = 'none'
            if system == 'Darwin':
                oses = 'macosx_10_6_universal2'
            elif system == 'Windows' and architecture == '32bit':
                oses = 'win32'
            elif system == 'Windows' and architecture == '64bit':
                oses = 'win_amd64'
            elif system == 'Linux' and architecture == '64bit':
                oses = 'linux_x86_64'
            elif system == 'Linux':
                oses = 'linux_' + architecture
            else:
                raise TypeError('Unknown build environment')
            return 'py3', abi, oses
    cmdclass = {'bdist_wheel': BdistWheelTagName}

setuptools.setup(
    name='assistent3',
    version='0.1.0',
    author='rojektpraktikum Python',
    author_email='python@ldv.ei.tum.de',
    description='Offline open source speech recognition API based on Kaldi and Vosk',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://gitlab.ldv.ei.tum.de/python2022/project',
    package_dir={'': 'src/assistent3'},
    packages=setuptools.find_packages(exclude=('models')),
    include_package_data=True,
    package_data={'': ['models']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'Typing :: Typed',
    ],
    cmdclass=cmdclass,
    python_requires='>=3',
    zip_safe=False,
    setup_requires=['setuptools >=40.8.0', 'wheel'],
    install_requires=['vosk'],
)
