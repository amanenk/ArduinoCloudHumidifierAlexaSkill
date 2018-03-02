
#Start with a temperature, in Kelvin, somewhere between 1000 and 40000.  (Other values may work,
#but I can't make any promises about the quality of the algorithm's estimates above 40000 K.)
#Note also that the temperature and color variables need to be declared as floating-point.
import math

def calculateRed(temperature):
    if temperature <= 66:
        red = 255
        return red
    else:
        red = temperature - 60
        red = 329.698727446 * (red ** (-0.1332047592))
        if red < 0:
            red = 0
        if red > 255:
            red = 255
        return red


def calculateGreen(temperature):
    if temperature <= 66:
        green = temperature
        green = 99.4708025861 * math.log(green) - 161.1195681661
        if green < 0:
            green = 0
        if green > 255:
            green = 255
        return green
    else:
        green = temperature - 60
        green = 288.1221695283 * (green ** (-0.0755148492))
        if green < 0:
            green = 0
        if green > 255:
            green = 255
        return green


def calculateBlue(temperature):
    if temperature >= 66:
        blue = 255
        return blue
    elif temperature <= 19:
        blue = 0
        return blue
    else:
        blue = temperature - 10
        blue = 138.5177312231 * math.log(blue) - 305.0447927307
        if blue < 0:
            blue = 0
        if blue > 255:
            blue = 255
        return blue


def temperatureToRgb(temperature):
    temperature = temperature / 100

    red = int(calculateRed(temperature))
    green = int(calculateGreen(temperature))
    blue = int(calculateBlue(temperature))
    return red, green, blue
