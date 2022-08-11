import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='XBRLi_converter',  
     version='1.3',
     author="Filippo Ciceri",
     author_email="filippo.ciceri@gmail.com",
     description="Convert XBRLi documents into simple XBRL",
     py_modules=['XBRLi_converter'],
     package_dir={'':'src'},
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/filippo-ciceri/XBRLI_converter",
     dependency_links=['www.financialdatatree.com/download/XBRLI_converter'],
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires = [
        "bs4",
        "lxml"
     ],
 )
