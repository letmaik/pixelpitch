from setuptools import setup, find_packages

setup(
    name = 'pixelpitch',
    version = '1.0.0',
    author = 'Maik Riechert',
    author_email = 'maik.riechert@arcor.de',
    url = 'https://github.com/neothemachine/pixelpitch',
    classifiers=[
      'Development Status :: 4 - Beta',
      'Natural Language :: English',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3',
      'Operating System :: OS Independent',
    ],
    packages = find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['jinja2',
                      ],
    entry_points = {
        'console_scripts': [
            'pixelpitch-html = pixelpitch.html:main',
        ]
    }
)