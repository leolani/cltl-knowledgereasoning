from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read().strip()

setup(
    name="cltl.thoughts",
    description="The Leolani Thoughts module for reasoning over accumulated knowledge",
    version=version,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leolani/cltl-knowledgereasoning",
    license='MIT License',
    authors={
        "Baez Santamaria": ("Selene Baez Santamaria", "s.baezsantamaria@vu.nl"),
        "Baier": ("Thomas Baier", "t.baier@vu.nl")
    },
    package_dir={'': 'src'},
    packages=find_namespace_packages(include=['cltl.*', 'cltl_service.*'], where='src'),
    package_data={'cltl.thoughts': []},
    python_requires='>=3.7',
    install_requires=[
        "cltl.brain",
        "cltl.combot~=1.0.dev0",
        "cltl.dialogue_evaluation",
        "matplotlib",
        "tqdm"
    ],
    setup_requires=['flake8'],
    extras_require={
        "transformers": [
            'torch~=1.10.2',
            'transformers~=4.16.2',
        ],
        "service": [
        ]
    }
)
