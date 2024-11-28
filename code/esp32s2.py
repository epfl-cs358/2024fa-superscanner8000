import requests


class Arm:
    def __init__(self, url):
        self.__url = url

    def goto(self, x_coord, y_coord):
        requests.post(self.__url + "/arm/goto", json={"x": x_coord, "y": y_coord})

    def stop(self):
        requests.post(self.__url + "/arm/stop", json={"stop": True})


class Car:
    def __init__(self):
        self.url = "http://superscanner8000:80"
        self.arm = Arm(self.url)

    def forward(self, time):
        requests.get(self.url + "/fwd")

    def backward(self, time):
        requests.get(self.url + "/bwd")

    def stop(self):
        requests.get(self.url + "/stp")

    def right(self, time):
        requests.get(self.url + "/rgt")

    def left(self, time):
        requests.get(self.url + "/lft")


if __name__ == "__main__":
    from tkinter import Tk, Button

    root = Tk()
    car = Car()
    root.title("Car Control")
    root.geometry("300x300")
    Button(root, text="Forward", command=lambda: car.forward(1)).grid(row=0, column=1)
    Button(root, text="Backward", command=lambda: car.backward(1)).grid(row=2, column=1)
    Button(root, text="Left", command=lambda: car.left(1)).grid(row=1, column=0)
    Button(root, text="Right", command=lambda: car.right(1)).grid(row=1, column=2)
    Button(root, text="Stop", command=car.stop).grid(row=1, column=1)

    root.mainloop()