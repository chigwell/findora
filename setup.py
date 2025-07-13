from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='findora',
    version='2025.7.131053',
    author='Eugene Evstafev',
    author_email='chigwel@gmail.com',
    description='Search engine',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chigwell/findora',
    packages=find_packages(),
    install_requires=[
        "langchain_llm7==2025.4.101205",
        "llmatch==2025.4.181303"
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license='MIT',
    tests_require=['unittest'],
    test_suite='test',
    extras_require={
        'test': [
            'pytest',
            "langchain_llm7==2025.4.101205",
            "llmatch==2025.4.181303"
        ]
    },
)