'''
Created on Jun 7, 2014

@author: pli
'''
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy as AppiumBy
import json
from pagesource_elements_tree import PageSourceElementsTree
import Utils

class Platform:
    Android = "Android"
    iOS = "iOS"

class AppiumDriver(webdriver.Remote):
    def __init__(self, ip, port, platform, desired_caps={}, _global_time_wait=2, newCommandTimeout=300,
                 browser_profile=None, proxy=None, keep_alive=False):
        self.command_executor = "http://%s:%s/wd/hub" % (ip, str(port))
        if platform in Platform.__dict__:
            self.platform = platform
        else:
            raise Exception("Platform type not exist")
        self.desired_caps = {"platformName":platform,
                             "newCommandTimeout": newCommandTimeout}
        self.browser_profile = browser_profile
        self.proxy = proxy
        self.keep_alive = keep_alive
        for key in desired_caps:
            self.desired_caps[key] = desired_caps[key]
        super(AppiumDriver, self).__init__(self.command_executor, self.desired_caps, self.browser_profile,
                                           self.proxy, self.keep_alive)
        self._global_time_wait = _global_time_wait
        self.set_timeout(self._global_time_wait)
    
    def __del__(self):
        self.quit()
    
    def loading_status(self):
        """
        return boolean telling whether is still loading or finished.
        only for iOS now, by Zhenyu
        """
        statusbar = self.find_element_by_xpath('//window[2]/statusbar[1]')
        # get all elements on the status bar
        eles = statusbar.find_elements_by_xpath('*')
        for ele in eles:
            #print ele.get_attribute('name')
            if "Network connection in progress" == ele.get_attribute('name'):
                return True
        try:
            self.set_timeout(0.1)
            eles = self.find_element_by_tag_name('activityIndicator')
            self.set_timeout()
            return eles[0].is_displayed()
        except:
            self.set_timeout()
            return False
    
    def get_elements_tree(self):
        pagesource = json.loads(self.page_source)
        elements_tree = PageSourceElementsTree(pagesource)
        nodes = elements_tree.get_all_available_elements()
        elements = []
        for node in nodes:
            xpath = node['xpath']
            elements.append(self.find_element_by_xpath(xpath))
        return elements
    
    def send_to_background(self, seconds):
        self.execute_script("mobile: background", {"seconds": seconds})
    
    def relaunch(self):
        super(AppiumDriver, self).__init__(self.command_executor, self.desired_caps, self.browser_profile,
                                           self.proxy, self.keep_alive)
        self.set_timeout(self._global_time_wait)
    
    def get_device_resolution(self):
        return self.get_window_size()
    
    def set_timeout(self, time_to_wait=2):
        if not time_to_wait:
            time_to_wait = self._global_time_wait
        self.implicitly_wait(time_to_wait)
    
    @classmethod
    def set_desired_capabilities(cls,
                                 app_path,
                                 platformName=Platform.iOS,
                                 platformVersion=None,
                                 deviceName=None,
                                 **kwargs):
        '''
        other caps refer to, can be called directly by this func
        https://github.com/appium/appium/blob/master/docs/en/caps.md
        '''
        cls.desired_caps = {
                            "app":app_path,
                            "platformName":platformName,
                            "platformVersion":platformVersion,
                            "deviceName":deviceName,
                            "autoAcceptAlerts":True
                            }
        for key in kwargs:
            cls.desired_caps[key] = kwargs[key]
        null_key = [k for k,v in cls.desired_caps.iteritems() if not v]
        for key in null_key:
            del cls.desired_caps[key]
        return cls.desired_caps
    
    def get_screenshot_without_items(self, filename, items, coordinates, color=(0,0,0)):
        '''
        the file name have to be ".png" type due to selenium restriction
        '''
        self.get_screenshot_as_file(filename)
        cords = []
        if items:
            for item in items:
                cord = [item.location["x"],item.location["y"],
                        item.location["x"]+item.size["width"],item.location["y"]+item.size["height"]]
                if cord:
                    cords.append(cord)
        if coordinates:
            for cord in coordinates:
                cords.append(cord)
        Utils.drawRec(filename, cords, color)
    
    def find_ele(self, by=AppiumBy.ID, value=None):
        '''key: id, xpath, link text, partial link text, name, tag name, class name, css selector
                -ios uiautomation, -android uiautomator, accessibility id
                You can also import AppiumBy to get the key'''
        if not AppiumBy.is_valid(by):
            raise "%s is not a Appium supported By key" % by
        if not isinstance(value, str):
            raise "%s is not a supported value, must be string" % str(value)
        try:
            return self.find_element(by, value)
        except:
            print "%s %s not found" % (by,value)
            return None
    
    def find_ele_by_partial_text(self, text, count=1):
        """
        2013.12.30 by Zhenyu

        Find an element by its partial text
        this function is with low efficiency.
        
        Parameters:
            text        : array of words
            count       : the number of the expected element  
            
        Return:
            the expected WebElement or None
        """
        pagesource = json.loads(self.page_source)
        elements_tree = PageSourceElementsTree(pagesource)
        elements = elements_tree.find_node_by_partial_text(text, count)
        if not elements:
            return False
        xpath = elements_tree.get_xpath_for_selected_node(elements)
        element = self.find_element_by_xpath(xpath)
        return element
        