import enum
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from tkinter import ON
from urllib.parse import urlparse, parse_qs
import json

from enums import *
import syscontrol as sysc
from configloader import config

hostName = "0.0.0.0"
serverPort = int(config["WebServer"]["port"])

class ControlServer(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        
        if url.path == "/":
            self.deliver_file("web/index.html")
            return
        elif url.path == "/favicon.ico":
            #pass
            self.deliver_file("web/favicon.ico","image/x-icon")
            return
        elif url.path == "/api":
            self.send_api_response("no api", failed=True)
            return

        elif url.path == "/api/gettemp":
            temper = sysc.get_temp()
            self.send_api_response(f"rpi temp is {temper}'C", temper)
            return

        elif url.path == "/api/getconfig":
            if ("get" in query) == False:
                self.send_api_response("no get", failed=True)
                return
            
            def fan_mode():
                print("\n[DEBUG] FAN_MODE")
                outDict = {
                    "always_off": sysc.fan_behave_always_off,
                    "always_on": sysc.fan_behave_always_on,
                    "after_temp": sysc.fan_behave_after_temp,
                    "match_screen": sysc.fan_behave_match_screen,
                }
                return outDict
                
            def streampi():
                print("\n[DEBUG] streampi")
                

            def service(name):
                print(f"\n[DEBUG] SERVICE - {name}")
                

            def docker(name):
                print(f"\n[DEBUG] DOCKER - {name}")
                

            def screen():
                print("\n[DEBUG] SCREEN")
                value = sysc.get_screen_power_status()
                if value == SCREENSTATUS.ON:
                    return True
                elif value == SCREENSTATUS.OFF:
                    return False
                
            def fan():
                print("\n[DEBUG] FAN")
                return sysc.fan_status()

            switch={
                "fan_mode": fan_mode,
                "streampi": streampi,

                "tablepi": lambda : service("tablepi"),
                "smdp": lambda : service("smdp"),
                "minidlna": lambda : service("minidlna"),

                "home_assistant": lambda : docker("home_assistant"),
                
                "screen": screen,
                "fan": fan
            }
            outData = {}
            for item in query["get"][0].split(","):
                res = switch.get(item, None)
                if res != None:
                    outData[item] = res()
            
                    



            self.send_api_response(f"Under Construction", outData)
            return

        elif url.path == "/api/hardware/fan":
            if query["mode"] == ["on"]:
                sysc.fan_on()
                self.send_api_response("fan now ON")
                return
            elif query["mode"] == ["off"]:
                sysc.fan_off()
                self.send_api_response("fan now OFF")
                return
            elif query["mode"] == ["to"]:
                sysc.fan_toggle()
                self.send_api_response("fan now TOGGLED")
                return
            else:
                self.send_api_response("wrong query", failed=True)
                return

        elif url.path == "/api/hardware/screen":
            if query["mode"] == ["on"]:
                sysc.turn_on_screen_power()
                self.send_api_response("screen now ON")
                return
            elif query["mode"] == ["off"]:
                sysc.turn_off_screen_power()
                self.send_api_response("screen now OFF")
                return
            elif query["mode"] == ["to"]:
                sysc.toggle_screen_power()
                self.send_api_response("fan now TOGGLED")
                return
            else:
                self.send_api_response("wrong query", failed=True)
                return

        elif url.path == "/api/behaviour/fanmode":
            if ("value" in query) == False:
                self.send_api_response("no value", failed=True)
                return

            if query["mode"] == ["aoff"]:
                rawvalue = query["value"][0]
                
                if rawvalue.lower() == "true":
                    sysc.fan_behave_always_off = True
                    self.send_api_response("Always Off Enabled", True)
                elif rawvalue.lower() == "false":
                    sysc.fan_behave_always_off = False
                    self.send_api_response("Always Off Disabled", False)
                else:
                    self.send_api_response("wrong value", failed=True)
                    return

            elif query["mode"] == ["aon"]:
                rawvalue = query["value"][0]
                
                if rawvalue.lower() == "true":
                    sysc.fan_behave_always_on = True
                    self.send_api_response("Always On Enabled", True)
                elif rawvalue.lower() == "false":
                    sysc.fan_behave_always_on = False
                    self.send_api_response("Always On Disabled", False)
                else:
                    self.send_api_response("wrong value", failed=True)
                    return
            elif query["mode"] == ["screen"]:
                rawvalue = query["value"][0]
                
                if rawvalue.lower() == "true":
                    sysc.fan_behave_match_screen = True
                    self.send_api_response("Match screen enabled", True)
                elif rawvalue.lower() == "false":
                    sysc.fan_behave_match_screen = True
                    self.send_api_response("Match screen disabled", False)
                else:
                    self.send_api_response("wrong value", failed=True)
                    return
            elif query["mode"] == ["temp"]:
                rawvalue = query["value"][0]
                
                if rawvalue.isnumeric():
                    sysc.fan_behave_after_temp = int(rawvalue)
                    self.send_api_response(f"after temp set to {rawvalue}", sysc.fan_behave_after_temp)
                    print(sysc.fan_behave_after_temp)
                else:
                    self.send_api_response("wrong value", failed=True)
                    return
            else:
                self.send_api_response("wrong query", failed=True)
                return
            

        elif url.path == "/api/service":
            self.send_api_response("Unavalible", failed=True)
            return


        else:
            print(url.path)
            self.test_deliver()
            return
    
    def deliver_file(self, path, content_header="text/html"):
        self.send_response(200)
        self.send_header("Content-type", content_header)
        self.end_headers()
        with open(path, "rb") as file:
            self.wfile.write(file.read())
            

    def send_api_response(self, msg, data=None, failed=False):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        typeStr = "successful"
        if failed:
            typeStr = "error"
        
        res = json.dumps({
            "type": typeStr,
            "msg": msg,
            "data": data
        })
        self.wfile.write(bytes(res,"utf-8"))
        

    def test_deliver(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

class WebThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        start_webserver()


def start_webserver(new_thread=False):

    if new_thread:
        webThread = WebThread()
        webThread.start()
    else:
        webServer = HTTPServer((hostName, serverPort), ControlServer)
        print("Server started http://%s:%s" % (hostName, serverPort))

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass

        webServer.server_close()
        print("Server stopped.")