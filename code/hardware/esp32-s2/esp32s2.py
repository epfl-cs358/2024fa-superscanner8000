import requests

class Cam:
    def __init__(self, url):
        self.__url = url

    def goto(self, x_coord, y_coord):
        r = requests.post(self.__url + "/cam/goto", json={"alpha": x_coord, "beta": y_coord})
        print(r.status_code,  r.content)
        if r.status_code != 200:
            return -1
        return 0

    def stop(self):
        r = requests.post(self.__url + "/cam/stp", json={"stop": True})
        print(r.status_code,  r.content)
        if r.status_code != 200:
            return -1
        return 0
    
    def pos(self):
        r = requests.get(self.__url + "/cam/status")
        if r.status_code != 200:
            return None
        json = r.json()
        return (json["x"], json["y"])
    
    def is_moving(self):
        r = requests.get(self.__url + "/cam/status")
        if r.status_code != 200:
            return None
        json = r.json()
        return json["moving"]


class Arm:
    def __init__(self, url):
        self.__url = url

    def goto(self, x_coord, y_coord):
        r = requests.post(self.__url + "/arm/goto", json={"x": x_coord, "y": y_coord, "angles": False})
        print(r.status_code,  r.content)
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
        self.cam = Cam(self.url)

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

    print(requests.get("http://superscanner8000:80/cam/status").json())

    root = Tk()
    car = ESP32S2()
    root.title("Car Control")
    root.geometry("400x300")

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
    Button(root, text="Goto", command=lambda: car.arm.goto(int(posx.get()), int(posy.get()))).grid(row=5, column=0)
    Button(root, text="Stop Arm", command=car.arm.stop).grid(row=4, column=0)

    txt = Entry(root)
    txt.insert(0, "0")
    txt.grid(row=6, column=1)
    Button(root, text="send", command=lambda: requests.post("http://superscanner8000:80/text", json={"text": txt.get()})).grid(row=6, column=0)
 
    cposx = Entry(root)
    cposx.insert(0, "0")
    cposx.grid(row=8, column=1)
    cposy = Entry(root)
    cposy.insert(0, "0")
    cposy.grid(row=8, column=2)
    Button(root, text="Goto", command=lambda: car.cam.goto(int(cposx.get()), int(cposy.get()))).grid(row=8, column=0)
    Button(root, text="Stop Cam", command=car.cam.stop).grid(row=7, column=0)


    # r, g, b fields and send button
    r = Entry(root)
    r.insert(0, "0")
    r.grid(row=9, column=0)
    g = Entry(root)
    g.insert(0, "0")
    g.grid(row=9, column=1)
    b = Entry(root)
    b.insert(0, "0")
    b.grid(row=9, column=2)
    Button(root, text="Set LED", command=lambda: requests.post("http://superscanner8000:80/led/set", json={"r": int(r.get()), "g": int(g.get()), "b": int(b.get())})).grid(row=10, column=0)
    Button(root, text="rainbow", command=lambda: requests.post("http://superscanner8000:80/led/rainbow", json={"rainbow": True})).grid(row=10, column=1)

    root.mainloop()