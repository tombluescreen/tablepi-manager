import configparser

config = configparser.ConfigParser()

def init_config_file():
    config_file = configparser.ConfigParser()

    config_file.add_section("General")
    config_file.set("General", "validateconfig", True)
    config_file.set("General", "password", "fullbeans")
    config_file.set("General", "pcIP", "PLSSET")
    config_file.set("General", "updateinterval", 5)

    config_file.add_section("GPIO")
    config_file.set("GPIO", "enabled", True)
    config_file.set("GPIO", "screenBtn", "-1")
    config_file.set("GPIO", "managerBtn", "-1")
    config_file.set("GPIO", "fanpin", "-1")

    config_file.add_section("WebServer")
    config_file.set("WebServer", "enabled", True)
    config_file.set("WebServer", "port", "8080")
    config_file.set("WebServer", "allowControl", True)
    save_config_file(config_file)

def save_config_file(config_file):
    with open(r"config.ini", 'w') as configfileObj:
        config_file.write(configfileObj)
        configfileObj.flush()
        configfileObj.close()
        print("Config file 'config.ini' saved")


def get_config():
    config_file = configparser.ConfigParser()
    config_file.read("config.ini")
    return config_file

def get_config_str():
    read_file = open("config.ini","r")
    content = read_file.read()
    read_file.flush()
    read_file.close()
    return content

def validate_config():
    #This function will validate all settings, looking for wrong types and impossible values
    validator_mask = {
        "validateconfig": bool,
        "password": str,
        "enabled": bool,
        "screenBtn": int,
        "managerBtn": int,
        "fanpin": int,
        "port": int,
        "allowControl": bool,
        "updateinterval": float
    }
    temp_config = get_config()
    
    fail = False
    failMsg = []
    def failed(msg):
        global fail
        fail = True
        failMsg.append(msg)
    
    for sec in temp_config.sections():
        for name in temp_config[sec]:
            #print(name)
            v = temp_config[sec][name]
            mask = None
            try:
                mask = validator_mask[name]
            except KeyError:
                continue
            #print(f"BEANS: {type(v)} {v}")
            if mask is bool:
                if ((v == bool(v).conjugate()) or ((v.lower() == "false") or (v.lower() == "true"))): # Then is real boolean
                    pass
                else:
                    #IS NOT BOOL
                    failed(f"{sec}#{name} not {mask.__name__}")
            else:
                try:
                    test = mask(v)
                except ValueError:
                    failed(f"{sec}#{name} not {mask.__name__}")
                
    return fail, (", ".join(failMsg))

def init_config():
    global config
    config = get_config()
init_config()