# ESP32 API

## Overview
The API can be accessed from the `SPOT-iot` Wifi using the adress [`http://superscanner8000/`](http://superscanner8000/). The file `code/esp32-s2/esp32s2.py` makes the API available through an `ESP32S2` class for easy usage in python code.

## Endpoints

> ### GET `/status`
> return format:
> <pre><code>    {
>         "direction": one of <i>forward</i>, <i>backward</i>, <i>left</i>, <i>right</i>, <i>hard left</i>, <i>hard right</i>, <i>stop</i> 
>     }
> </code></pre>
> Returns the current movement the scanner is performing.

> ### POST `/fwd`
>    body format:
>
>        {
>            "ms": value
>        }
> 
> Makes the scanner run forward for `ms` milliseconds. If `ms <= 0` runs forever.

> ### POST `/bwd`
>    body format:
>
>        {
>            "ms": value
>        }
> 
> Makes the scanner run backward for `ms` milliseconds. If `ms <= 0` runs forever.

> ### POST `/lft`
>    body format:
>
>        {
>            "ms": value
>        }
> 
> Makes the scanner turn left for `ms` milliseconds. If `ms <= 0` runs forever.

> ### POST `/rgt`
>    body format:
>
>        {
>            "ms": value
>        }
> 
> Makes the scanner turn right for `ms` milliseconds. If `ms <= 0` runs forever.

> ### POST `/hlft`
>    body format:
>
>        {
>            "ms": value
>        }
> 
> Makes the scanner turn on itself anti-clockwise for `ms` milliseconds. If `ms <= 0` runs forever.

> ### POST `/hrgt`
>    body format:
>
>        {
>            "ms": value
>        }
> 
> Makes the scanner turn on itsels clockwise for `ms` milliseconds. If `ms <= 0` runs forever.

> ### POST `/stp`
>    
> Makes the scanner stop as quickly as possible. Does not need any body.

> ### GET `/arm/status`
>    return format:
>
>        {
>            "target x": x position where the arm is or wants to go if in movement
>            "target y": y position where the arm is or wants to go if in movement
>            "moving": boolean indicating whether the arm is moving or not
>        }
> 
> Returns informations about the arm.

> ### POST `/arm/goto`
>    body format:
>
>        {
>            "x": target x position
>            "y": target y position
>        }
> 
> Makes the arm move to the given position
>> might return error code `422` if coordinates are not valid

> ### POST `/arm/stop`
> 
> Stops the arm as quickly as possible. Does not need any body

> ### GET `/cam/status`
>    return format:
>
>        {
>            "alpha": alpha angle where the cam wants to go
>            "beta": beta angle where the cam wants to go
>            "moving": boolean indicating whether the camera is moving or not
>        }
> 
> Returns informations about the camera.

> ### POST `/cam/goto`
>    body format:
>
>        {
>            "alpha": target angle for vertical movement
>            "betha": target angle for horizontal movement
>        }
> 
> Makes the camera move to the given angles

> ### POST `/cam/stop`
> 
> Stops the camera as quickly as possible. Does not need any body

## class `ESP32S2`

Interfaces with the API to provide an abstracted access to the scanner.

> ### `ESP32S2()`
> Class constructor. Does not require any parameters.

> ### `forward(self, time)`
> - `time`: duration of movement in ms. Moves infinitely if <= 0
> - returns: `0` if operation was successful, `-1` otherwise

> ### `backward(self, time)`
> - `time`: duration of movement in ms. Moves infinitely if <= 0
> - returns: `0` if operation was successful, `-1` otherwise

> ### `left(self, time)`
> - `time`: duration of movement in ms. Moves infinitely if <= 0
> - returns: `0` if operation was successful, `-1` otherwise

> ### `right(self, time)`
> - `time`: duration of movement in ms. Moves infinitely if <= 0
> - returns: `0` if operation was successful, `-1` otherwise

> ### `hard_left(self, time)`
> - `time`: duration of movement in ms. Moves infinitely if <= 0
> - returns: `0` if operation was successful, `-1` otherwise

> ### `hard_right(self, time)`
> - `time`: duration of movement in ms. Moves infinitely if <= 0
> - returns: `0` if operation was successful, `-1` otherwise

> ### `stop(self)`
> - returns: `0` if operation was successful, `-1` otherwise

> ### `direction(self)`
> - returns: a `string` giving the current direction or `None` if request was unsuccessful

> ### `arm.goto(self, x_coord, y_coord)`
> - `x_coord`: target x coordinate in cm
> - `y_coord`: target y coordinate in cm
> - returns: `0` if operation was successful, `-1` otherwise

> ### `arm.stop(self)`
> - returns: `0` if operation was successful, `-1` otherwise

> ### `arm.pos(self)`
> - returns: `(x, y)` tuple representing the target coordinated of the arm or `None` if the request was unsuccessful

> ### `arm.is_moving(self)`
> - returns: a `boolean` indicating whether the arm is moving or `None` if the request was unsuccessful

## `__main__` in `esp32s2.py`

Running `esp32s2.py` provides a small graphical interface to test movements without having to write code.
