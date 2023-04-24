import socket


class Test:
      def __init__(self):
            used_status_ports = [3400]
            self.used_status_ports = used_status_ports


test = Test()

def get_control_port() -> int:
    # All 255 usable drone status ports, since its from 3400 to, but not including, 3656 alas a total of 255.
    for port in range(3400, 3656):

        # if the port is not yet used, use it.
        if port not in test.used_status_ports:
            local_status_port = port

            return local_status_port

    raise Exception("No available status ports")

print(get_control_port())

