from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cfspider",
    version="1.7.3",
    author="violettools",
    author_email="violet@violetteam.cloud",
    description="Cloudflare Workers proxy IP pool client with stealth mode, anti-detection, async, HTTP/2, TLS fingerprint, browser, mirror and IP map",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/violettoolssite/CFspider",
    project_urls={
        "Bug Tracker": "https://github.com/violettoolssite/CFspider/issues",
        "Documentation": "https://spider.violetteam.cloud",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.20.0",
        "playwright>=1.40.0",
        "httpx[http2]>=0.25.0",
        "curl_cffi>=0.5.0",
        "beautifulsoup4>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "cfspider=cfspider.cli:main",
        ],
    },
    keywords="cloudflare workers proxy ip pool crawler spider browser playwright httpx http2 async curl_cffi tls fingerprint impersonate map visualization maplibre mirror offline stealth anti-detection anti-bot",
)
