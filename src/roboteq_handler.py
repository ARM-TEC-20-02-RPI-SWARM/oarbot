import serial
import time
# message
class RoboteqHandler:
    """
    Create a roboteq device object for communication, read the README for more information
    param: exit_on_interrupt - exits program with any error received (recommended for debugging)
    param: debug_mode - prints every data sent to the controller and received from the controller, doesnt stop the program.
    """

    def __init__(self, exit_on_interrupt = False, debug_mode = False):
        self.is_alive = False
        self.port = ""
        self.baudrate = 115200
        self.ser = None
        self.exit_on_interrupt = exit_on_interrupt
        self.debug_mode = debug_mode
    
    def connect(self, port, baudrate = 115200):
        """
        Attempt to establish connection with the controller
        If the attempt fails, the method will return False otherwise, True.
        """
        self.port = port
        self.baudrate = baudrate
        
        if self.debug_mode == True:
            print("DEBUG MODE: ")
            print("EXIT ON INTERRUPT: ")
            time.sleep(1)

        try: # attempt to create a serial object and check its status
            self.ser = serial.Serial(
                port = self.port,
                baudrate = self.baudrate,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize= serial.EIGHTBITS
            )
            if self.ser.isOpen():
                self.ser.close()
            self.ser.open()
            self.is_alive = True

        except Exception as e:
            if self.debug_mode == True:
                print("DEBUG MODE: ERROR: Failed to connect to the roboteq device, read the exception error below:")
                print(e)
                print("\n")
            self.is_alive = False
            
        return self.is_alive

    def send_raw_command(self, str_command= ""):
        """
        Send a raw string command, the library will handle sending the command, but how you write it
        is up to you.
        """
        raw_command = "%s+\r"%(str_command)
        try:
            #if self.debug_mode == True:
            #    print("DEBUG MODE: Tx:{raw_command}")
            self.ser.write(raw_command.encode())

        except Exception as e:
            if self.debug_mode == True:
                print("DEBUG MODE: Failed to send command to the controller, read the exception error below:")
                print(e)
                print("\n")
            if self.exit_on_interrupt == True:
                quit()
        
    def request_handler(self, request= ""):
        """
        Sends a command and a parameter, 
        """
        def get_data(serial):
            raw_data = b''
            while raw_data == b'':
                try:
                    raw_data = serial.read_all()
                except Exception as e:
                    if self.debug_mode == True:
                        print("DEBUG MODE: Failed to read from the controller, read the exception error below:")
                        print(e)
                        print("\n")
                    if self.exit_on_interrupt == True:
                        quit()
                    raw_data = b' '
            
            #if self.debug_mode == True:
            #    print("DEBUG MODE: Rx:{raw_data}")
            return raw_data

        self.send_raw_command(request)
        result = get_data(self.ser)
        result = result.decode()
        result = result.split("\r")
        try:
            return result[1]
        
        except IndexError: # will raise index error as sometimes the controller will return an odd answer, its rare, so its simply ignored.
            debug_return = "DEBUG MODE: Received faulty message, ignoring..."
            if self.exit_on_interrupt == True:
                quit()
            if self.debug_mode == True:
                print(debug_return)
            return debug_return

    def dual_motor_control(self, left_motor= 0, right_motor= 0):
        """
        Controlling the motor using a Dual Drive mode
        Send speed for the left, and right side of the robot/vehicle seperately 
        Effective for doing Pivot drive and running track based robots
        left_motor: integer from -1000 to 1000
        right_motor: integer from -1000 to 1000
        """
        raw_command ="!M %d %d "%(left_motor,right_motor)
        self.request_handler(raw_command)
    
    def send_command(self, command, first_parameter = "", second_parameter = ""):
        if first_parameter != "" and second_parameter != "":
            message = "%s %s %s "%(command,first_parameter,second_parameter)
        if first_parameter != "" and second_parameter == "":
            message = "%s %s "%(command,first_parameter)
        if first_parameter == "" and second_parameter == "":
            message = "%s "%(command)
        
        try:
            response = self.request_handler(message)
        except Exception as e:
            if self.debug_mode == True:
                print("DEBUG MODE: Failed to construct a message, read the exception error below:")
                print(e)
                print("Received message: {response}")
                print("\n")
            if self.exit_on_interrupt == True:
                quit()

    def read_value(self, command= "", parameter = ""):
        """
        Constructs a message and sends it to the controller.
        param: command (str)
        param: parameter (str/int)
        returns: answer from the controller, data from request commands, or echo from action commands.
        """
        request = "%s [%s]"%(command,parameter)
        response = self.request_handler(request)
        return response
