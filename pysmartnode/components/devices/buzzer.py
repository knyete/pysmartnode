'''
Created on 31.10.2017

@author: Kevin K�ck
'''

"""
example config:
{
    package: .devices.buzzer,
    component: Buzzer,
    constructor_args: {
        pin: D5,
        pwm_values: [512,819,1020,786]  #list of pwm dutys, on esp32 use percentage, max is 1024 on esp8266
        #on_time: 500                #optional, defaults to 500ms, time buzzer stays at one pwm duty
        #iters: 1                   #optional, iterations done, defaults to 1
        #freq: 1000                 #optional, defaults to 1000
        #mqtt_topic: null     #optional, defaults to home/<id>/Buzzer/set
    }
}
"""

__updated__ = "2018-07-13"
__version__ = "2.5"

import gc

from machine import Pin, PWM
from pysmartnode import config
import uasyncio as asyncio

mqtt = config.getMQTT()

gc.collect()


class Buzzer:
    def __init__(self, pin, pwm_values, on_time=500, iters=1, freq=1000, mqtt_topic=None):
        if type(pin) == str:
            pin = config.pins[pin]
        mqtt_topic = mqtt_topic or mqtt.getDeviceTopic("Buzzer", is_request=True)
        self.pin = pin
        self.on_time = on_time
        self.values = pwm_values
        self.iters = iters
        self.lock = config.Lock()
        self.pin = PWM(Pin(self.pin, Pin.OUT), freq=freq)
        self.pin.duty(0)
        mqtt.scheduleSubscribe(mqtt_topic, self.notification, check_retained=False)
        # not checking retained as buzzer only activates single-shot
        self.mqtt_topic = mqtt_topic

    async def notification(self, topic, msg, retain):
        if self.lock.locked():
            return False
        async with self.lock:
            if msg in mqtt.payload_on:
                mqtt.schedulePublish(self.mqtt_topic, "ON")
                for i in range(0, self.iters):
                    for duty in self.values:
                        self.pin.duty(duty)
                        await asyncio.sleep_ms(self.on_time)
                self.pin.duty(0)
                await mqtt.publish(self.mqtt_topic, "OFF")
        return False  # will not publish the state "ON" to mqtt
