#mtdriver

A python driver for Appium to communicate with Chorus based on Official Appium Python Client

##Usage
Remote Version
```
>from AppiumDriver import AppiumServer
>server = AppiumServer("<remoteip>", "<hostname>", "<hostpassword>")
>server.start_server()
>driver = server._get_driver("<.app path>", "iOS")
>....
>driver.quit()
>server.stop_server()
```
Local Version
```
>from AppiumDriver import AppiumServer
>server = AppiumServer("localhost")
>server.start_server()
>driver = server._get_driver("<apk path>", "Android", platformVersion="18", deviceName="<adb device name>")
>....
>driver.quit()
>server.stop_server()
```