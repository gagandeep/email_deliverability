from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="email_deliverability",
    version="0.1.1",
    description="Comprehensive email deliverability management tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gagan (InnerKore)",
    author_email="gagan@innerkore.com",
    url="https://github.com/innerkore/email-deliverability",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Email",
    ],
    python_requires=">=3.7",
    install_requires=[
        "dnspython>=2.0.0",
        "requests>=2.25.0",
        "cryptography>=3.2.0",
        "schedule>=1.2.0",
    ],
    entry_points={
        'console_scripts': [
            'email-deliverability=email_deliverability.cli:main',
        ],
    },
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "sphinx",
            "sphinx_rtd_theme",
            "twine==6.0.1",
            "black>=20.8b1",
            "isort>=5.7.0",
            "flake8>=3.8.0",
            "myst-parser>=0.18.0",  # Added for Markdown support in Sphinx
            "wheel",
            "build",
        ],
        "docs": [
            "sphinx",
            "sphinx_rtd_theme",
        ],
    },
    keywords="email, deliverability, spf, dkim, dmarc, email authentication",
    project_urls={
        "Documentation": "https://github.com/innerkore/email-deliverability/docs",
        "Source": "https://github.com/innerkore/email-deliverability",
        "Tracker": "https://github.com/innerkore/email-deliverability/issues",
    },
)