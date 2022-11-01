from asyncio import subprocess
import gpiozero as gp
from gpiozero.pins.mock import MockFactory



DEBUG_MODE = False


from time import sleep
import subprocess as sp
import enum
import threading
import os, signal


from enums import *
from configloader import config

#Other Commands
def return_command(cmd:str):
    # The command you want to execute   
    cmdlist = cmd.strip().split(" ")

    # send one packet of data to the host 
    # this is specified by '-c 1' in the argument list 
    #cmd.append("/dev/null")
    # Iterate over all the servers in the list and ping each server
    
    process = sp.Popen(cmdlist, stdout=sp.PIPE, stderr=sp.PIPE)
    
    stdout, stderr = process.communicate()
    #print(stderr.decode("utf-8"))
    return stdout.decode("utf-8").strip()

try:
    print(return_command('hostnamectl'))
    if (return_command('hostnamectl') == None):
        gp.Device.pin_factory = MockFactory()
        DEBUG_MODE = True
        print("[DEBUG-MODE] - NOW ENABLED\n------------------")
except FileNotFoundError:
    gp.Device.pin_factory = MockFactory()
    print("[DEBUG-MODE] - NOW ENABLED\n------------------")
    DEBUG_MODE = True


def ping_test(ip:str):
    #outStr = ""
    if DEBUG_MODE:
        print("[DEBUG-MODE] - Ping Result False")
        return False
    testresult = True
    try:
        stdout = sp.check_output(f"ping -c 1 -W 1 {ip}",shell=True,stderr=sp.STDOUT)
        #outStr = stdout.decode("utf-8")
        #print("SUCESS")
    except sp.CalledProcessError as e:
        testresult = False
        #outStr = e.output.decode("utf-8")
        #print(f"FAILE with {e.returncode}")
        #raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    #x = re.search(" received", outStr)
    #print(outStr)
    #print(x)
    #recnum = outStr[x.start()-1:x.start()]
    return testresult
    
def get_temp():
    if DEBUG_MODE:
        print("[DEBUG-MODE] - Pi Temp Set 45")
        return 45
    #return 9999
    temp_response = return_command("vcgencmd measure_temp")
    final_res = temp_response[5:-2]
    return float(final_res)

# Config Constants
GPIO_MANAGER_BUTTON_PIN = config["GPIO"]["managerbtn"]
GPIO_SCREEN_BUTTON_PIN = config["GPIO"]["screenbtn"]
GPIO_FAN_PIN = config["GPIO"]["fanpin"]
PING_HOST_IP = config["General"]["pcip"]
# PING_HOST_IP = "169.254.141.196"
# PING_HOST_IP = "192.168.1.190"


# Vars
check_pc = True

fan_behave_match_screen = False
fan_behave_always_on = False
fan_behave_always_off = False
fan_behave_after_temp = -1



# PC Status
def get_pc_power_status():
    #I will use simple ping for this
    powerStatus = None
    pingresult = ping_test(PING_HOST_IP)
    if pingresult:
        powerStatus = PCSTATUS.ON
    else:
        powerStatus = PCSTATUS.OFF
    return powerStatus

# StreamPi functions

def get_streampi_status():
    if DEBUG_MODE:
        print("[DEBUG-MODE] - StreamPi Set Closed")
        return False
    name = "stream_pi.client"
    try:
         
        # iterating through each instance of the process
        for line in os.popen("ps ax | grep " + name + " | grep -v grep"):
            return True
        return False
    except:
        print("Error Encountered while running script")

def launch_streampi():
    if get_streampi_status() == False:
        if DEBUG_MODE:
            print("[DEBUG-MODE] - StreamPi Launched")
            return 

        sp.Popen(["bash", "./stream-pi-client/run_desktop"],stdout=sp.DEVNULL, stderr=sp.DEVNULL)

def kill_streampi():
    if DEBUG_MODE:
        print("[DEBUG-MODE] - StreamPi kill stopped")
        return 
    name = "stream_pi.client"
    try:
         
        # iterating through each instance of the process
        for line in os.popen("ps ax | grep " + name + " | grep -v grep"):
            fields = line.split()
             
            # extracting Process ID from the output
            pid = fields[0]
             
            # terminating process
            os.kill(int(pid), signal.SIGKILL)
        print("Process Successfully terminated")
         
    except:
        print("Error Encountered while running script")

# Screen functions
def get_screen_power_status():
    out_screen_status = None
    if DEBUG_MODE:
        print("[DEBUG-MODE] - get_screen_power_status() forced return SCREENSTATUS.ON")
        return SCREENSTATUS.ON
    screen_command_response = return_command("vcgencmd display_power")
    #print(screen_command_response)
    if screen_command_response == "display_power=1":
        out_screen_status = SCREENSTATUS.ON
    elif screen_command_response == "display_power=0":
        out_screen_status = SCREENSTATUS.OFF
    return out_screen_status

def turn_on_screen_power():
    if DEBUG_MODE:
        print("[DEBUG-MODE] - Screen now ON")
        return 
    return_command("vcgencmd display_power 1")

def turn_off_screen_power():
    if DEBUG_MODE:
        print("[DEBUG-MODE] - Screen now OFF")
        return 
    return_command("vcgencmd display_power 0")

def toggle_screen_power():
    screen_status = get_screen_power_status()
    #print(screen_status)
    #print(type(screen_status))
    if screen_status is SCREENSTATUS.ON:
        turn_off_screen_power()
    elif screen_status is SCREENSTATUS.OFF:
        turn_on_screen_power()

# GPIO
class gpioThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("[EVENT] Starting GPIO handle")
        t_manger_btn = gp.Button(GPIO_MANAGER_BUTTON_PIN)
        t_screen_btn = gp.Button(GPIO_SCREEN_BUTTON_PIN)
        while True:
            if t_manger_btn.is_pressed:
                print("[EVENT] Manger button pressed")
                #Manger button is pressed
                #Toggling manger button
                global check_pc
                if check_pc: 
                    check_pc = False
                    kill_streampi()
                else: 
                    check_pc = True
                
                sleep(0.25)
            
            if t_screen_btn.is_pressed:
                print("[EVENT] Screen button pressed")
                toggle_screen_power()
                sleep(0.25)



def handle_gpio():
    gpioT = gpioThread()
    gpioT.start()

# Fan
_fan = gp.LED
def fan_status():
    return bool(_fan.value)

def fan_toggle():
    _fan.toggle()

def fan_on():
    _fan.on()

def fan_off():
    _fan.off()

def init_all():
    global _fan
    _fan = gp.LED(GPIO_FAN_PIN)

def handle_fan():
    global _fan
    # Multiple behavious can be true at the same time in this order:
    # - Always Off
    # - Always On
    # - Enable After Temp
    # - Match Screen
    turn_on_fan = False


    if fan_behave_match_screen:
        if get_screen_power_status() == SCREENSTATUS.ON: turn_on_fan = True
    if fan_behave_after_temp > -1:
        temp = get_temp()
        if temp > fan_behave_after_temp: turn_on_fan = True
    if fan_behave_always_on:
        turn_on_fan = True
    if fan_behave_always_off:
        turn_on_fan = False

    if turn_on_fan:
        fan_on()
    else:
        fan_off()



#main loop
def main_loop():
    
    if check_pc:
        print("[EVENT] Starting PC status check")
        PC_power_status = get_pc_power_status()

        if PC_power_status is PCSTATUS.ON:
            print("[EVENT] PC is ON")
            launch_streampi()
            turn_on_screen_power()
        elif PC_power_status is PCSTATUS.OFF:
            print("[EVENT] PC is OFF")
            kill_streampi()
            turn_off_screen_power()
    handle_fan()