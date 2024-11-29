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
        requests.post(self.url + "/fwd", json={"ms": time})

    def backward(self, time):
        requests.post(self.url + "/bwd", json={"ms": time})

    def stop(self):
        requests.post(self.url + "/stp")

    def right(self, time):
        requests.post(self.url + "/rgt", json={"ms": time})

    def left(self, time):
        requests.post(self.url + "/lft", json={"ms": time})


if __name__ == "__main__":
    from tkinter import Tk, Button, Entry

    root = Tk()
    car = Car()
    root.title("Car Control")
    root.geometry("300x300")

    time_entry = Entry(root)
    time_entry.insert(0, "1")
    time_entry.grid(row=4, column=1)

    Button(root, text="Forward", command=lambda: car.forward(int(time_entry.get()))).grid(row=0, column=1)
    Button(root, text="Backward", command=lambda: car.backward(int(time_entry.get()))).grid(row=2, column=1)
    Button(root, text="Left", command=lambda: car.left(int(time_entry.get()))).grid(row=1, column=0)
    Button(root, text="Right", command=lambda: car.right(int(time_entry.get()))).grid(row=1, column=2)
    Button(root, text="Stop", command=car.stop).grid(row=1, column=1)

    Button(root, text="Goto 0,0", command=lambda: car.arm.goto(0, 0)).grid(row=3, column=0)
    Button(root, text="Goto 0,80", command=lambda: car.arm.goto(0, 80)).grid(row=3, column=2)
    Button(root, text="Stop Arm", command=car.arm.stop).grid(row=3, column=1)

    root.mainloop()