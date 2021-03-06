# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(0)
import gc

# import webrepl
# webrepl.start()
gc.collect()


def reload(mod):
    import sys
    mod_name = mod.__name__
    del sys.modules[mod_name]
    return __import__(mod_name)


import sys

if sys.platform == "esp32_LoBo":
    sys.path.insert(0, "/flash")
    sys.path.append("/flash/lib")
