from distutils.core import setup

setup(
    name='monti_fmri',
    version='0.1.0',
    author='Jeff Chiang',
    author_email='jeff.njchiang@gmail.com',
    packages=['fmri_core', 'experimental'],
    url='https://github.com/njchiang/task-fmri-utils.git',
    license='LICENSE',
    description='fMRI analysis wrappers for Monti Lab at UCLA.',
    install_requires=[
        "nilearn",
        "nibabel",
        "scikit-learn",
        "numpy",
        "scipy"
    ],
)