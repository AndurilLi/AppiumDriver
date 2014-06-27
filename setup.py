from setuptools import setup
setup(
    name='AppiumDriver',
    version='1.0',
    author='Li, Peng; Yang, Zhenyu; Feng, Dong',
    author_email='pli@microstrategy.com, zheyang@microstrategy.com, dfeng@microstrategy.com',
    packages=['AppiumDriver'],
    include_package_data=True,
    zip_safe=False,
    install_requires=["PIL","paramiko","psutil","Appium-Python-Client"],
    license="MIT",
    url='http://git/pli/appiumdriver',
)
