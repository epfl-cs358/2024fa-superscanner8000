import requests


class Arm:
    def __init__(self, url):
        self.__url = url

    def goto(self, x_coord, y_coord):
        requests.post(self.__url + "/arm/goto", json={"x": x_coord, "y": y_coord})

    def stop(self):
        requests.post(self.__url + "/arm/stop", json={"stop": True})


class Car:
    def __init__(self, ip):
        self.url = "http://" + ip + ":80"
        self.arm = Arm(self.url)

    def forward(self, time):
        requests.post(self.url + "/forward", json={"time": time})

    def backward(self, time):
        requests.post(self.url + "/backward", json={"time": time})

    def stop(self):
        requests.post(self.url + "/stop", json={"stop": True})

    def right(self, time):
        requests.post(self.url + "/right", json={"time": time})

    def left(self, time):
        requests.post(self.url + "/left", json={"time": time})


if __name__ == "__main__":
    ip = "192.168.137.28"
    obj = {"red": 10, "green": 1, "blue": 100}
    
    ctrl = Car(ip)
    ctrl.forward(obj)
    ctrl.arm.goto(0, 0)
    ctrl.arm.stop()