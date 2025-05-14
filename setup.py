from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="po_generator",
    version="0.1.0",
    author="Taesh Kim",
    author_email="your.email@example.com",
    description="웹 페이지에서 Selenium 페이지 오브젝트를 자동으로 생성하는 도구",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/taeshkim/po_generator",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.10.0",
        "google-cloud-vision>=2.7.3",
        "python-dotenv>=0.21.0",
        "webdriver-manager>=3.8.0",
        "pillow>=9.0.0",
        "pytest>=7.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "po-generator=src.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires=">=3.8",
)