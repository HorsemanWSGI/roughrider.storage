from setuptools import setup


setup(
    name='roughrider.storage',
    install_requires=[
        'nanoid',
    ],
    extras_require={
        'test': [
            'pytest'
        ]
    }
)
