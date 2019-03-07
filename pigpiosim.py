#!/usr/bin/python3

import sys, os, socket, struct, pigpio, time, configparser
from threading import Thread, Event, Lock

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import mainthread


SCREEN = '''

<BorderLabel@Label>:
    border_width: 1
    border_color: (0.5, 0.5, 0.5, 1)
    background_color: (0, 0, 0, 1)
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: self.border_color
        Line:
            width: self.border_width
            rectangle: self.x, self.y, self.width, self.height
            
<Pin@BoxLayout>:
    orientation: 'horizontal'
    height: 22
    size_hint_y: None
    pin: ''
    name: ''

<GPIOPin@Pin>:
    mode: 'input'
    io: ''
    name: 'GPIO ' + self.io

<PinNumber@BorderLabel>:
    width: 30
    size_hint_x: None

<FixedPinL@Pin>:
    pin_color: (0, 0, 0, 1)
    label_color: (0, 0, 0, 1)
    BorderLabel:
        text: self.parent.name
        background_color: self.parent.label_color
    PinNumber:
        text: self.parent.pin
        background_color: self.parent.pin_color
        
<FixedPinR@Pin>:
    pin_color: (0, 0, 0, 1)
    label_color: (0, 0, 0, 1)
    PinNumber:
        text: self.parent.pin
        background_color: self.parent.pin_color
    BorderLabel:
        text: self.parent.name
        background_color: self.parent.label_color
        
<InputButton@Button>:
    text: 'M'
    font_size: '12sp'
    width: 40 if self.parent.mode == 'input' else 0
    size_hint_x: None if self.parent.mode == 'input' else 0
    disabled: self.parent.mode != 'input'
    opacity: 1 if self.parent.mode == 'input' else 0
    on_press: self.parent.parent.toggleInput(self.parent)
    on_release: self.parent.parent.toggleInput(self.parent)

<InputToggleButton@ToggleButton>:
    text: 'T'
    font_size: '12sp'
    width: 40 if self.parent.mode == 'input' else 0
    size_hint_x: None if self.parent.mode == 'input' else 0
    disabled: self.parent.mode != 'input'
    opacity: 1 if self.parent.mode == 'input' else 0
    on_state: self.parent.parent.toggleInput(self.parent)

<OutputValue@BorderLabel>:
    text: ''

<GPIOPinL@GPIOPin>:
    pin_color: (0, 0.6, 0, 1)
    label_color: (0, 0, 0, 1)
    display_value: ''
    BorderLabel:
        id: label
        text: self.parent.name
        background_color: self.parent.label_color
    InputButton:
    InputToggleButton:
    OutputValue:
        text: self.parent.display_value
    PinNumber:
        text: self.parent.pin
        background_color: self.parent.pin_color
        
<GPIOPinR@GPIOPin>:
    pin_color: (0, 0.6, 0, 1)
    label_color: (0, 0, 0, 1)
    display_value: ''
    PinNumber:
        text: self.parent.pin
        background_color: self.parent.pin_color
    OutputValue:
        text: self.parent.display_value
    InputToggleButton:
    InputButton:
    BorderLabel:
        id: label
        text: self.parent.name
        background_color: self.parent.label_color
    
<pigpioController>:
    cols: 2
    padding: 5
    spacing: 5
    
    FixedPinL:
        pin: '1'
        name: '3.3V'
        pin_color: (0.8, 0, 0, 1)
    FixedPinR:
        pin: '2'
        name: '5V'
        pin_color: (0.8, 0, 0, 1)
    GPIOPinL:
        pin: '3'
        io: '2'
    FixedPinR:
        pin: '4'
        name: '5V'
        pin_color: (0.8, 0, 0, 1)
    GPIOPinL:
        pin: '5'
        io: '3'
    FixedPinR:
        pin: '6'
        name: 'GND'
        pin_color: (0, 0, 0, 1)
    GPIOPinL:
        pin: '7'
        io: '4'
    GPIOPinR:
        pin: '8'
        io: '14'
    FixedPinL:
        pin: '9'
        name: 'GND'
        pin_color: (0, 0, 0, 1)
    GPIOPinR:
        pin: '10'
        io: '15'
    GPIOPinL:
        pin: '11'
        io: '17'
    GPIOPinR:
        pin: '12'
        io: '18'
    GPIOPinL:
        pin: '13'
        io: '27'
    FixedPinR:
        pin: '14'
        name: 'GND'
        pin_color: (0, 0, 0, 1)
    GPIOPinL:
        pin: '15'
        io: '22'
    GPIOPinR:
        pin: '16'
        io: '23'
    FixedPinL:
        pin: '17'
        name: '3.3V'
        pin_color: (0.8, 0, 0, 1)
    GPIOPinR:
        pin: '18'
        io: '24'
    GPIOPinL:
        pin: '19'
        io: '10'
    FixedPinR:
        pin: '20'
        name: 'GND'
        pin_color: (0, 0, 0, 1)
    GPIOPinL:
        pin: '21'
        io: '9'
    GPIOPinR:
        pin: '22'
        io: '25'
    GPIOPinL:
        pin: '23'
        io: '11'
    GPIOPinR:
        pin: '24'
        io: '8'
    FixedPinL:
        pin: '25'
        name: 'GND'
        pin_color: (0, 0, 0, 1)
    GPIOPinR:
        pin: '26'
        io: '7'
    GPIOPinL:
        pin: '27'
        io: '0'
    GPIOPinR:
        pin: '28'
        io: '1'
    GPIOPinL:
        pin: '29'
        io: '5'
    FixedPinR:
        pin: '30'
        name: 'GND'
        pin_color: (0, 0, 0, 1)
    GPIOPinL:
        pin: '31'
        io: '6'
    GPIOPinR:
        pin: '32'
        io: '12'
    GPIOPinL:
        pin: '33'
        io: '13'
    FixedPinR:
        pin: '34'
        name: 'GND'
        pin_color: (0, 0, 0, 1)
    GPIOPinL:
        pin: '35'
        io: '19'
    GPIOPinR:
        pin: '36'
        io: '16'
    GPIOPinL:
        pin: '37'
        io: '26'
    GPIOPinR:
        pin: '38'
        io: '20'
    FixedPinL:
        pin: '39'
        name: 'GND'
        pin_color: (0, 0, 0, 1)
    GPIOPinR:
        pin: '40'
        io: '21'
        
'''

class ClientException(Exception):
    pass
    
class pigpioClient:

    nextHandle = 0
    
    def __init__(self, app, sock, addr):
        self.app = app
        self.sock = sock
        self.addr = addr
        self.handle = pigpioClient.nextHandle
        pigpioClient.nextHandle = pigpioClient.nextHandle + 1
        self.eventSequence = 0
        self.lock = Lock()
        self.sock.settimeout(None)
        self.thread = Thread(target = self.loop, name = 'Client {}'.format(addr), daemon = True)
        self.thread.start()
        
    def loop(self):
        while self.sock:
            try:
                buffer = self.sock.recv(16)
                if not len(buffer): break
                if len(buffer) != 16:
                    raise ClientException('incomplete command')
                buffer = bytes(buffer)
                cmdStruct = struct.unpack('4I', buffer)
                extension = None
                if cmdStruct[3]:
                    buffer = self.sock.recv(cmdStruct[3])
                    if len(buffer) != cmdStruct[3]:
                        raise ClientException('incomplete command extension')
                    extension = bytes(buffer)
                self.processCommand(*cmdStruct, extension)
            except ClientException as e:
                print('Client {}: {}'.format(self.addr, e))
                break
            except IOError:
                break
        self.close()
        
    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print('Closed connection from {}'.format(self.addr))
        self.app.removeClient(self)
    
    def processCommand(self, cmd, p1, p2, p3, extension):
    
        if cmd == pigpio._PI_CMD_BR1:
            res = 0
            for io in reversed(range(32)):
                gpio = self.app.controller.getIO(io, False)
                if gpio:
                    res = (res << 1) + (1 if gpio.value else 0)
            self.sendResponse(res)
            
        elif cmd == pigpio._PI_CMD_NOIB:
            self.sendResponse(self.handle)
        
        elif cmd == pigpio._PI_CMD_MODES:
            gpio = self.app.controller.getIO(p1)
            if p2 == pigpio.INPUT: mode = 'input'
            elif p2 == pigpio.OUTPUT: mode = 'output'
            else:
                raise ClientException('unsupported mode {}'.format(p2))
            gpio.set_mode(mode)
            self.sendResponse()
            
        elif cmd == pigpio._PI_CMD_NC:  # stops notification on handle p1
            self.sendResponse()
            
        elif cmd == pigpio._PI_CMD_NB:
            for io in reversed(range(32)):
                gpio = self.app.controller.getIO(io, False)
                if gpio:
                    gpio.setup_callback(p1, (p2 & (1 << io)) > 0)
            self.sendResponse()
    
        elif cmd == pigpio._PI_CMD_PUD:
            gpio = self.app.controller.getIO(p1)
            gpio.set_pullup(p2)
            self.sendResponse()
        
        elif cmd == pigpio._PI_CMD_FG:
            self.sendResponse()
        
        elif cmd == pigpio._PI_CMD_READ:
            gpio = self.app.controller.getIO(p1)
            self.sendResponse(1 if gpio.value else 0)
        
        elif cmd == pigpio._PI_CMD_WRITE:
            gpio = self.app.controller.getIO(p1)
            gpio.set_value(p2 == pigpio.HIGH)
            self.sendResponse()
        
        elif cmd == pigpio._PI_CMD_PRS:
            gpio = self.app.controller.getIO(p1)
            gpio.set_pwm_range(p2)
            self.sendResponse(gpio.pwmRange)
        
        elif cmd == pigpio._PI_CMD_PWM:
            gpio = self.app.controller.getIO(p1)
            gpio.set_pwm_dutycycle(p2)
            self.sendResponse()
        
        elif cmd == pigpio._PI_CMD_PFS:
            gpio = self.app.controller.getIO(p1)
            gpio.set_pwm_frequency(p2)
            self.sendResponse(gpio.pwmFrequency)
        
        else:
            raise ClientException('unknown command: {}'.format(cmd))
                
    def sendResponse(self, res = 0):
        with self.lock:
            self.sock.send(struct.pack('4I', 0, 0, 0, res))
    
    def sendEvent(self, flags, level):
        with self.lock:
            ticks = int(time.time() * 1000000) % (1 << 32)
            self.sock.send(struct.pack('HHII', self.eventSequence, flags, ticks, level))
            #print('sent event: {}, {}, {}, {}'.format(self.eventSequence, hex(flags), ticks, hex(level)))
            self.eventSequence = (self.eventSequence + 1) % (1 << 16)

class GPIOPin:

    def __init__(self, app, widget):
        self.app = app
        self.widget = widget
        self.name = widget.name
        self.pin = widget.pin
        self.io = widget.io
        self.mode = 'input'
        self.bit = 1 << int(self.io)
        self.pullup = pigpio.PUD_OFF
        self.value = False
        self.pwmRange = 255
        self.pwmFrequency = 0
        self.pwmDutycycle = 0
        self.handles = []
        
        if self.app.simConfig.has_option('labels', self.io):
            widget.name = self.app.simConfig.get('labels', self.io)
            
        self.update()
        
    def add_handle(self, handle):
        if handle not in self.handles:
            self.handles.append(handle)
            
    def remove_handle(self, handle):
        if handle in self.handles:
            self.handles.remove(handle)
            
    def set_mode(self, mode):
        if mode != self.mode:
            self.mode = mode
            if mode == 'input' and not isinstance(self.value, bool):
                self.value = False
            self.update()
            print('GPIO {} mode set to {}'.format(self.io, self.mode))

    def set_pullup(self, pullup):
        self.pullup = pullup
        self.update()
        
    def set_value(self, value):
        if value != self.value:
            self.value = value
            self.update()
            print('GPIO {} value set to {}'.format(self.io, 'High' if self.value else 'Low'))

            for handle in self.handles:
                client = self.app.clientForHandle(handle)
                if client:
                    client.sendEvent(0, self.bit if self.value else 0)
        
    def toggle_value(self):
        if isinstance(self.value, bool):
            self.set_value(not self.value)
            
    def setup_callback(self, handle, on):
        if on:
            self.add_handle(handle)
        else:
            self.remove_handle(handle)
        print('GPIO {} callback turned {} for {}'.format(self.io, 'on' if handle in self.handles else 'off', handle))
    
    def set_pwm_range(self, range):
        self.pwmRange = range
        self.pwmDutycycle = min(self.pwmDutycycle, self.pwmRange)
        self.value = None
        self.update()
        print('GPIO {} PWM range set to {}'.format(self.io, self.pwmRange))
    
    def set_pwm_dutycycle(self, dutycycle):
        self.pwmDutycycle = max(min(dutycycle, self.pwmRange), 0)
        self.set_mode('output')
        self.value = None
        self.update()
        print('GPIO {} PWM dutycycle set to {}'.format(self.io, self.pwmDutycycle))
            
    def set_pwm_frequency(self, frequency):
        self.pwmFrequency = frequency
        self.set_mode('output')
        self.value = None
        self.update()
        print('GPIO {} PWM frequency set to {}'.format(self.io, self.pwmFrequency))
            
    @mainthread
    def update(self):
        self.widget.mode = self.mode
        
        if self.mode == 'input':
            if self.pullup == pigpio.PUD_OFF:
                pud = 'No pullup'
            elif self.pullup == pigpio.PUD_UP:
                pud = 'Pullup'
            elif self.pullup == pigpio.PUD_OFF:
                pud = 'Pulldown'
            self.widget.display_value = '{}/{}'.format(pud, 'High' if self.value else 'Low')
            
        else:
            if isinstance(self.value, bool):
                self.widget.display_value = 'High' if self.value else 'Low'
            else:
                self.widget.display_value = 'PWM {:0.0f}%/{}Hz'.format(100 * self.pwmDutycycle / self.pwmRange, self.pwmFrequency)
            
        
    
    
class pigpioController(GridLayout):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ios = {}
        for c in self.children:
            if hasattr(c, 'mode'):
                gpio = GPIOPin(app, c)
                self.ios[c.io] = gpio
        
    def toggleInput(self, widget):
        gpio = self.getIO(widget.io)
        if gpio:
            gpio.toggle_value()
        
    def getIO(self, io, raiseException = True):
        io = str(io)
        if io not in self.ios.keys():
            if raiseException:
                raise ClientException('unknown GPIO {}'.format(io))
            return None
        else:
            return self.ios[io]
            
class pigpioApp(App):

    title = 'pigpiod Simulator'
    
    def __init__(self):
        super().__init__()
        self.serverThread = None
        self.exitEvent = Event()
        self.clients = []
        self.controller = None

        self.simConfig = configparser.ConfigParser(interpolation = None)
        self.simConfig.optionxform = str    # preserve option case
        self.simConfig.clear()
        if len(sys.argv) > 1:
            self.simConfig.read(sys.argv[1])
        
    def build(self):
        Builder.load_string(SCREEN)
        self.serverThread = Thread(target = self.serverLoop, name = 'Server', daemon = True)
        self.serverThread.start()
        self.controller = pigpioController(self)
        return self.controller

    def serverLoop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        
        s.bind(('127.0.0.1', 8888))
        s.listen(2)
        print('Waiting for connection...')
        while not self.exitEvent.is_set():
            sock, addr = s.accept()
            print('Accepted connection from {}'.format(addr))
            client = pigpioClient(self, sock, addr)
            self.clients.append(client)
        s.close()
        for client in self.clients:
            client.close()
            self.removeClient(client)
            
    def removeClient(self, client):
        if client in self.clients:
            self.clients.remove(client)
            
    def clientForHandle(self, handle):
        return next(iter([c for c in self.clients if c.handle == handle]), None)
        
  
if __name__ == '__main__':
    app = pigpioApp()
    try:
        app.run()
    except KeyboardInterrupt:
        pass



