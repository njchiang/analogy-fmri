from distutils.core import setup

setup(
    name='fmri',
    version='0.1.0',
    author='Jeff Chiang',
    author_email='jeff.njchiang@gmail.com',
    packages=['fmri'],
    license='LICENSE',
    description='fMRI analysis wrappers for Analogy Project Monti Lab at UCLA.',
    install_requires=[
        "nilearn",
        "nibabel",
        "scikit-learn",
        "numpy",
        "scipy"
    ],
)