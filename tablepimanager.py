#This script is to manage the tablepi and its features
#These Features are
#   -GPIO Buttons
#   -StreamPi Application Management
#   -Screen Power mangement

#What should happen when the PC status changes.
#   1. Nothing
#   2. Screen Power
#   3. StreamPi App

from time import sleep

import websrv
import configloader as cloader
import syscontrol
    
if (__name__ == "__main__"):
    
    #Current Button layout
    #   - Match PC status switch
    #   - Screen power switch

    #kill_streampi()
    #launch_streampi()
    
    #config = configloader.get_config()
    
    failed, msg = cloader.validate_config()
    
    if failed == True:
        print(f"[ERROR] - Config file is wrong: {msg}")
        exit()
    print(f"[EVENT] - Config file is valid")

    syscontrol.init_all()

    if cloader.config["WebServer"]["enabled"]:
        websrv.start_webserver(True)
    
    
    if cloader.config["GPIO"]["enabled"]:
        syscontrol.handle_gpio()
        

    while True:
        syscontrol.main_loop()
        
        sleep(float(cloader.config["General"]["updateinterval"]))