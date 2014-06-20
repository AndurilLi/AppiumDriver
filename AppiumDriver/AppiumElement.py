'''
Created on Jun 7, 2014

@author: pli
'''

from appium.webdriver import WebElement
import Utils
import time

class AppiumElement(WebElement):
    def __init__(self, driver, by, value, initial_find = True):
        self.driver = driver
        self.by = by
        self.value = value
        if initial_find:
            self.find_ele()
        else:
            self.ele = None
            
    def find_ele(self, by=None, value=None, time_to_wait = None):
        if time_to_wait:
            self.driver.set_timeout(time_to_wait)
        if by:
            self.by = by
        if value:
            self.value = value
        self.ele = self.driver.find_ele(self.by, self.value)
        if self.ele:
            super(AppiumElement, self).__init__(self.ele._parent, self.ele._id)
            self.centerx = self.location["x"] + self.size["width"]/2
            self.centery = self.location["y"] + self.size["height"]/2
        if time_to_wait:
            self.driver.set_timeout()
    
    @property
    def existence(self):
        return True if self.ele else False
    
    def tap(self):
        self.click()
        
    def longtap(self, duration=2):
        self.driver.tap([self.centerx, self.centery], duration)
    
    def EnterText(self, text):
        self.send_keys(text)
    
    def pinch(self, percent=200, steps=50):
        '''
        Pinch on an element a certain amount
        - percent - (optional) amount to pinch. Defaults to 200%
        - steps - (optional) number of steps in the pinch action
        '''
        self.driver.pinch(self.ele, percent, steps)
    
    def zoom(self, percent=200, steps=50):
        '''
        Zooms in on an element a certain amount
        - percent - (optional) amount to pinch. Defaults to 200%
        - steps - (optional) number of steps in the pinch action
        '''
        self.driver.zoom(self.ele, percent, steps)
    
    def scroll(self, target_element):
        self.driver.scroll(self.ele, target_element)
        
    def drag_to_element(self, target_element):
        self.driver.drag_and_drop(self.ele, target_element)
        
    def swipe_to_coordinates(self, x, y, duration=None):
        self.driver.swipe(self.centerx, self.centery, x, y, duration)
        
    def flick_to_coordinated(self, x, y):
        self.driver.flick(self.centerx, self.centery, x, y)
    
    def set_value(self, value):
        self.driver.set_value(self.ele, value)
    
    def wait_for(self, timeout, displayed = True, time_to_wait = 0.5):
        current_time = time.time()
        while time.time() <= current_time + timeout:
            self.find_ele(time_to_wait=time_to_wait)
            if self.ele:
                if not displayed:
                    return True
                elif self.is_displayed():
                    return True
        print "wait for element failed"
        return False
        
    def wait_for_disappear(self, timeout, displayed = False, time_to_wait = 0.5):
        current_time = time.time()
        while time.time() <= current_time + timeout:
            self.find_ele(time_to_wait=time_to_wait)
            if not self.ele:
                return True
            elif not displayed:
                if not self.is_displayed():
                    return True
        print "wait for element disappear failed"
        return False
    
    def get_screen_shot_as_file(self, filename):
        self.driver.get_screenshot_as_file(filename)
        Utils.getRec(filename, self.location["x"], self.location["y"], 
                     self.location["x"] + self.size["width"], 
                     self.location["y"] + self.size["height"])
        
    def get_screenshot_without_items(self, filename, items=None, cordinates=None, color=(0,0,0)):
        self.driver.get_screenshot_as_file(filename)
        if cordinates:
            cords = []
            for cord in cordinates:
                cords.append(cord)
            Utils.drawRec(filename, cords, color)
        
            