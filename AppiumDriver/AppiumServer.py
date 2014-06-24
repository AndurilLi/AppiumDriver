'''
Created on Jun 7, 2014

@author: pli
'''


import SSHHelper
import psutil
import os
from AppiumDriver import AppiumDriver
import time

class AppiumServer:
    def __init__(self, ip, host_name=None, host_pwd=None, port=4723, output="", args=""):
        self.ssh = SSHHelper.SSHHelper(ip, host_name, host_pwd)
        self.ssh.connect()
        self.ip = SSHHelper.check_ip(ip)
        self.port = port
        self.args = args
        self.output = output

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
    
    def start_server(self):
        self.__kill_appium()
        filepath = os.path.join(self.output, "appium.log")
        self.logfile = open(filepath,"wb")
        base_cmd = ["appium","-p",str(self.port),"--log-no-colors"]
        cmd = base_cmd+self.args.split(" ") if self.args else base_cmd
        if not self.ip.find("localhost")==0:
            stdout, stderr = self.ssh.exe_cmd(" ".join(cmd))
            try:
                firstline = stdout.readline()
                self.logfile.write(firstline)
                print firstline
                self.stdout = stdout
                self.stderr = stderr
            except:
                error = stderr.readline()
                print error
                raise Exception(error)
        else:
            self.proc = self.ssh.exe_cmd(" ".join(cmd)+" &", self.logfile)
        time.sleep(3)
            
    def stop_server(self):
        self.__kill_appium()
        if not self.ip.find("localhost")==0:
            data = self.stdout.read()
            self.logfile.write(data)
            self.logfile.close()
            self.ssh.disconnect()
        else:
            self.logfile.close()
            self.proc.kill()
    
    def __kill_appium(self):
        if self.ip.find("localhost")==0:
            for proc in psutil.process_iter():
                try:
                    if proc.name().find("adb")==0:
                        proc.kill()
                    if proc.name().find("node")==0:
                        proc.kill()
                        print "kill appium successful"
                except:
                    continue
        else:
            stdout, stderr = self.ssh.exe_cmd("killall -9 node")
            del stdout
            error = stderr.read()
            if not error or error.find("No matching processes")==0:
                print "remote kill appium successful"

if __name__=="__main__":
#     server = AppiumServer("localhost")
    server = AppiumServer("10.197.60.109", "mxu", "mstr123")
    server.start_server()
    try:
#         driver = server._get_driver("C:\\Users\pli\Desktop\UBA.apk", platform="Android", platformVersion="18",
#                           deviceName="2b19b4f0")
        driver = server._get_driver("/Users/mxu/Library/Developer/Xcode/DerivedData/SingleBadge-euzismtugfkglkdnahbrxckkuhxk/Build/Products/Debug-iphonesimulator/Usher.app","iOS")
        driver.quit()
    except Exception,e:
        import traceback
        traceback.print_exc()
    server.stop_server()