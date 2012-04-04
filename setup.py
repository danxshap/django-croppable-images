from setuptools import setup, find_packages

setup(
    name='django-croppable-images',
    version="0.1",
    description='Let\'s you easily manage cropped images on your Django models in conjunction with django-imagekit',
    author='Daniel Shapiro',
    author_email='danxshap@gmail.com',
    url='http://github.com/danxshap/django-croppable-images',
    packages=find_packages(),
    install_requires = ['setuptools', 'django-imagekit'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
