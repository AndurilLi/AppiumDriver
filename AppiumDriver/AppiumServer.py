'''
Created on Jun 7, 2014

@author: pli
'''


import SSHHelper
import sys
import os
from AppiumDriver import AppiumDriver
import time

class AppiumServer:
    def __init__(self, ip, host_name=None, host_pwd=None, port=4723, outputpath="", args=""):
        self.ssh = SSHHelper.SSHHelper(ip, host_name, host_pwd, outputpath)
        self.ip = self.ssh.ip
        self.port = port
        self.args = args
        self.outputpath = outputpath

    def _get_driver(self, app_path, platform, platformVersion=None, deviceName=None,
                    newCommandTimeout=300, _global_time_wait=2, 
                    browser_profile=None, proxy=None, keep_alive=False,
                    **kwargs):
        '''
        iOS simulator doesn't need optional parameters
        Android will require all optional parameters 
        '''
        caps = AppiumDriver.set_desired_capabilities(app_path, platformName=platform,
                                                     platformVersion=platformVersion,
                                                     deviceName=deviceName, **kwargs)
        return AppiumDriver(self.ip, self.port, platform, caps, _global_time_wait=_global_time_wait,
                            newCommandTimeout=newCommandTimeout,
                            browser_profile=browser_profile, proxy=proxy, keep_alive=keep_alive)
    
    def start_server(self, force_kill_old=False):
        self.ssh.connect()
        if force_kill_old:
            self._kill_appium()
        filepath = os.path.join(self.outputpath, "appium.log")
        base_cmd = ["appium","-p",str(self.port),"--log-no-colors"]
        cmd = " ".join(base_cmd+self.args.split(" ") if self.args else base_cmd)
        self.session = self.ssh.start_blocking_session(cmd, filepath)

    def stop_server(self):
        self.ssh.close_blocking_session(self.session)
        print "Appium Server is stopped"
        self.ssh.disconnect()
    
    def _kill_appium(self, printerr=False):
        os_type = self.ssh.get_system_type()
        print "Appium machine OS is %s" % os_type
        if os_type != "Windows":
            output = self.ssh.exe_cmd("killall -9 node", True)
        else:
            output = self.ssh.exe_cmd("taskkill /F /IM node.exe", True)
        if output.code == 0:
            print "Kill appium successful"
        elif printerr:
            sys.stderr.write(output.stderr)
            

if __name__=="__main__":
    server = AppiumServer("localhost")
#     server = AppiumServer("10.197.60.69", "mxu", "mstr123")
    server.start_server()
    try:
        driver = server._get_driver("C:\\Users\pli\Desktop\UBA.apk", platform="Android", platformVersion="19",
                          deviceName="emulator-5554")
#         driver = server._get_driver("/Users/mxu/Library/Developer/Xcode/DerivedData/SingleBadge-euzismtugfkglkdnahbrxckkuhxk/Build/Products/Debug-iphonesimulator/Usher.app",
#                                     "iOS")
        from AppiumDriver import AppiumBy
        from AppiumElement import AppiumElement
        current = time.time()
        while not driver.find_ele(AppiumBy.NAME,"Badge Recovery"):
            time.sleep(3)
            if time.time()-current>60:
                break
            pass
        badge_recovery = AppiumElement(driver, AppiumBy.NAME, "Badge Recovery")
        badge_recovery.click()
        driver.find_ele(AppiumBy.NAME, "Submit")
        time.sleep(2)
        driver.get_screenshot_as_file("badge_recovery.jpg")
        driver.quit()
    except Exception,e:
        import traceback
        traceback.print_exc()
    server.stop_server()