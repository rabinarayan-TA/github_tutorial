### **_Good Integration Practises_**

---

- Place a setup.py file in the root of your package with the following minimum content:

```
from setuptools import setup, find_packages

setup(name="PACKAGENAME", packages=find_packages(),author="",description="",version="0.1.0",
packages=find_packages(include=["mysklearn", "mysklearn.*"],package_dir={"": "src"},
install_requires=[],
python_requires=))
version number=(majornumber).(minornumber).(patchnumber)

*increase patch number for bug fixes and improvments to the function that already exist
*increase minor number for new features
* increase major number for really big changes
* package_dir is necessary when you want to keep your package in src directory

```

- To install the package run "pip install -e ." in terminal
- . indicate that package will install in current directory and -e indicate the editor mode that means any changes made to the code will reflect every time we import the packages
- Save Packages requirment to a file using
  ` pip freeze > requirements.txt`
- install requirements from file ` pip install -r requirements.txt`
