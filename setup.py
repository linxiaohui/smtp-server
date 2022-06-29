import setuptools

with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="smtp-server",
    version="0.0.2",
    author="Lin Xiao Hui",
    author_email="llinxiaohui@126.com",
    description="Simple SMTP Server Demo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/linxiaohui/smtp-server",
    packages=setuptools.find_packages(),
    install_requires=['dnspython'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)