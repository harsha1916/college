import RPi.GPIO as GPIO
import time

# ----------------- PIN SETUP -----------------
ENA = 18   # PWM pin
IN1 = 23
IN2 = 24

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# PWM frequency (1000 Hz is fine for DC motors)
pwm = GPIO.PWM(ENA, 1000)
pwm.start(0)  # start stopped

# ----------------- MOTOR FUNCTIONS -----------------
def motor_forward(speed=60):
    """speed: 0 to 100"""
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(speed)

def motor_reverse(speed=60):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(speed)

def motor_stop():
    pwm.ChangeDutyCycle(0)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)

# ----------------- DEMO LOOP -----------------
try:
    print("Forward @ 70% for 5s")
    motor_forward(70)
    time.sleep(5)

    print("Stop for 2s")
    motor_stop()
    time.sleep(2)

    print("Reverse @ 50% for 5s")
    motor_reverse(50)
    time.sleep(5)

    print("Stop")
    motor_stop()

finally:
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up.")
