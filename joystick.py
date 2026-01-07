from flask import Flask, request, jsonify, render_template
import time
import RPi.GPIO as GPIO

app = Flask(__name__)

# ---------------- GPIO PINS ----------------
ENA = 18   # PWM
IN1 = 23
IN2 = 24

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([IN1, IN2], GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

pwm = GPIO.PWM(ENA, 1000)  # 1kHz PWM
pwm.start(0)

# ---------------- MOTOR CONTROL ----------------
current_speed = 60  # default 0..100

def motor_forward(speed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(speed)

def motor_reverse(speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(speed)

def motor_stop():
    pwm.ChangeDutyCycle(0)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/speed", methods=["POST"])
def set_speed():
    global current_speed
    data = request.get_json(force=True)
    spd = int(data.get("speed", current_speed))
    spd = max(0, min(100, spd))
    current_speed = spd
    return jsonify({"ok": True, "speed": current_speed})

@app.route("/api/drive", methods=["POST"])
def drive():
    """
    Receives joystick vector x,y in range [-1..1].
    We'll map:
      y > 0 => forward, y < 0 => reverse
      magnitude controls PWM duty (scaled by current_speed)
      x is optional (you can extend to steering with 2 motors)
    """
    data = request.get_json(force=True)
    x = float(data.get("x", 0.0))
    y = float(data.get("y", 0.0))

    # deadzone to prevent jitter
    dead = 0.12
    if abs(y) < dead:
        motor_stop()
        return jsonify({"ok": True, "state": "stop", "speed": 0})

    # magnitude based on |y| (0..1), scaled by current_speed (0..100)
    mag = min(1.0, abs(y))
    duty = int((mag * current_speed))
    duty = max(0, min(100, duty))

    if y > 0:
        motor_forward(duty)
        state = "forward"
    else:
        motor_reverse(duty)
        state = "reverse"

    return jsonify({"ok": True, "state": state, "duty": duty, "x": x, "y": y})

@app.route("/api/stop", methods=["POST"])
def stop():
    motor_stop()
    return jsonify({"ok": True, "state": "stop"})

@app.route("/api/cleanup", methods=["POST"])
def cleanup():
    motor_stop()
    pwm.stop()
    GPIO.cleanup()
    return jsonify({"ok": True})

if __name__ == "__main__":
    # Run on all interfaces so your phone/PC can open it
    app.run(host="0.0.0.0", port=5000, threaded=True)
