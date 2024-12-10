import requests


class Arm:
    def __init__(self, url):
        self.__url = url

    def goto(self, x_coord, y_coord):
        r = requests.post(self.__url + "/arm/goto", json={"x": x_coord, "y": y_coord})
        if r.status_code != 200:
            return -1
        return 0

    def stop(self):
        r = requests.post(self.__url + "/arm/stop", json={"stop": True})
        if r.status_code != 200:
            return -1
        return 0
    
    def pos(self):
        r = requests.get(self.__url + "/arm/status")
        if r.status_code != 200:
            return None
        json = r.json()
        return (json["x"], json["y"])
    
    def is_moving(self):
        r = requests.get(self.__url + "/arm/status")
        if r.status_code != 200:
            return None
        json = r.json()
        return json["moving"]


class ESP32S2:
    def __init__(self):
        self.url = "http://superscanner8000:80"
        self.arm = Arm(self.url)

    def forward(self, time):
        r = requests.post(self.url + "/fwd", json={"ms": time})
        if r.status_code != 200:
            return -1
        return 0

    def backward(self, time):
        r = requests.post(self.url + "/bwd", json={"ms": time})
        if r.status_code != 200:
            return -1
        return 0

    def stop(self):
        r = requests.post(self.url + "/stp")

    def right(self, time):
        r = requests.post(self.url + "/rgt", json={"ms": time})
        if r.status_code != 200:
            return -1
        return 0

    def left(self, time):
        r = requests.post(self.url + "/lft", json={"ms": time})
        if r.status_code != 200:
            return -1
        return 0

    def hard_right(self, time):
        r = requests.post(self.url + "/hrgt", json={"ms": time})
        if r.status_code != 200:
            return -1
        return 0

    def hard_left(self, time):
        r = requests.post(self.url + "/hlft", json={"ms": time})
        if r.status_code != 200:
            return -1
        return 0
    
    def direction(self):
        r = requests.get(self.url + "/status")
        if r.status_code != 200:
            return None
        return r.json()["direction"]


if __name__ == "__main__":
    from tkinter import Tk, Button, Entry

    root = Tk()
    car = ESP32S2()
    root.title("Car Control")
    root.geometry("300x300")

    time_entry = Entry(root)
    time_entry.insert(0, "-1")
    time_entry.grid(row=3, column=1)

    Button(root, text="Forward", command=lambda: car.forward(int(time_entry.get()))).grid(row=0, column=1)
    Button(root, text="Backward", command=lambda: car.backward(int(time_entry.get()))).grid(row=2, column=1)
    Button(root, text="Left", command=lambda: car.left(int(time_entry.get()))).grid(row=1, column=0)
    Button(root, text="Right", command=lambda: car.right(int(time_entry.get()))).grid(row=1, column=2)
    Button(root, text="Stop", command=car.stop).grid(row=1, column=1)
    Button(root, text="Hard Left", command=lambda: car.hard_left(int(time_entry.get()))).grid(row=0, column=0)
    Button(root, text="Hard Right", command=lambda: car.hard_right(int(time_entry.get()))).grid(row=0, column=2)

    posx = Entry(root)
    posx.insert(0, "0")
    posx.grid(row=5, column=1)
    posy = Entry(root)
    posy.insert(0, "0")
    posy.grid(row=5, column=2)
    Button(root, text="Goto", command=lambda: car.arm.goto(int(posy.get()), int(posy.get()))).grid(row=5, column=0)
    Button(root, text="Stop Arm", command=car.arm.stop).grid(row=4, column=0)

    txt = Entry(root)
    txt.insert(0, "0")
    txt.grid(row=6, column=1)
    Button(root, text="send", command=lambda: requests.post("http://superscanner8000:80/display", json={"text": txt.get()})).grid(row=6, column=0)
 
    root.mainloop()