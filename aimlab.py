import time
import math
import ctypes
from ctypes import wintypes

import cv2
import mss
import numpy as np
import pyautogui
from ultralytics import YOLO


# ============================================================
# SETTINGS
# ============================================================

MODEL_PATH = r"E:\GTA autopilot\runs\aimlabs\weights\best.pt"

START_DELAY = 10

# YOLO
CONFIDENCE = 0.50
IMG_SIZE = 1080

# Aim tolerance in screen pixels
AIM_TOLERANCE = 20

# Mouse calibration
MOUSE_SCALE_X = 2
MOUSE_SCALE_Y = 2

# Maximum relative mouse movement in ONE iteration
MAX_MOUSE_STEP = 2000

# Timing
CLICK_DELAY = 0.02
FRAME_DELAY = 0.005


# ============================================================
# WINDOWS RELATIVE MOUSE INPUT
# ============================================================

user32 = ctypes.WinDLL("user32", use_last_error=True)

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("union",)

    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION),
    ]


def move_mouse_relative(dx, dy):

    extra = wintypes.ULONG(0)

    mouse_input = MOUSEINPUT(
        dx=int(dx),
        dy=int(dy),
        mouseData=0,
        dwFlags=MOUSEEVENTF_MOVE,
        time=0,
        dwExtraInfo=ctypes.pointer(extra)
    )

    input_event = INPUT(
        type=INPUT_MOUSE,
        mi=mouse_input
    )

    result = user32.SendInput(
        1,
        ctypes.byref(input_event),
        ctypes.sizeof(INPUT)
    )

    if result != 1:
        raise ctypes.WinError(ctypes.get_last_error())


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO model loaded.")


# ============================================================
# SCREEN
# ============================================================

sct = mss.mss()

monitor = sct.monitors[1]

screen_width = monitor["width"]
screen_height = monitor["height"]

print(f"Screen: {screen_width} x {screen_height}")

# Crosshair is permanently at screen center
crosshair_x = screen_width / 2
crosshair_y = screen_height / 2

print(
    f"Crosshair: "
    f"({crosshair_x:.0f}, {crosshair_y:.0f})"
)


# ============================================================
# STARTUP DELAY
# ============================================================

print()
print("Starting in 10 seconds...")

for i in range(START_DELAY, 0, -1):
    print(f"{i}...", flush=True)
    time.sleep(1)

print("STARTING AIM CONTROLLER!")


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        # ----------------------------------------------------
        # CAPTURE FULL SCREEN
        # ----------------------------------------------------

        screenshot = np.array(
            sct.grab(monitor)
        )

        frame = cv2.cvtColor(
            screenshot,
            cv2.COLOR_BGRA2BGR
        )


        # ----------------------------------------------------
        # YOLO
        # ----------------------------------------------------

        results = model.predict(
            frame,
            conf=CONFIDENCE,
            imgsz=IMG_SIZE,
            verbose=False
        )

        result = results[0]

        targets = []


        # ----------------------------------------------------
        # GET TARGETS
        # ----------------------------------------------------

        if result.boxes is not None:

            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()

            for box, confidence, cls in zip(
                boxes,
                confidences,
                classes
            ):

                # Class 0 = target
                if int(cls) != 0:
                    continue

                x1, y1, x2, y2 = box

                target_x = (x1 + x2) / 2
                target_y = (y1 + y2) / 2

                dx = target_x - crosshair_x
                dy = target_y - crosshair_y

                distance = math.sqrt(
                    dx * dx +
                    dy * dy
                )

                targets.append({
                    "x": target_x,
                    "y": target_y,
                    "dx": dx,
                    "dy": dy,
                    "distance": distance,
                    "confidence": confidence,
                    "box": (x1, y1, x2, y2)
                })


        # ----------------------------------------------------
        # SELECT CLOSEST TARGET
        # ----------------------------------------------------

        if not targets:
            time.sleep(FRAME_DELAY)
            continue

        target = min(
            targets,
            key=lambda t: t["distance"]
        )

        dx = target["dx"]
        dy = target["dy"]


        # ----------------------------------------------------
        # ARE WE AIMING AT IT?
        # ----------------------------------------------------

        if (
            abs(dx) <= AIM_TOLERANCE
            and
            abs(dy) <= AIM_TOLERANCE
        ):

            print(
                f"AIMED | "
                f"dx={dx:.1f}, "
                f"dy={dy:.1f} | "
                f"CLICK"
            )

            pyautogui.click()

            time.sleep(CLICK_DELAY)

            continue


        # ----------------------------------------------------
        # CONVERT SCREEN ERROR → MOUSE MOVEMENT
        # ----------------------------------------------------

        mouse_dx = dx * MOUSE_SCALE_X
        mouse_dy = dy * MOUSE_SCALE_Y


        # ----------------------------------------------------
        # LIMIT MOVEMENT
        # ----------------------------------------------------

        mouse_dx = max(
            -MAX_MOUSE_STEP,
            min(MAX_MOUSE_STEP, mouse_dx)
        )

        mouse_dy = max(
            -MAX_MOUSE_STEP,
            min(MAX_MOUSE_STEP, mouse_dy)
        )


        # ----------------------------------------------------
        # MOVE CAMERA
        # ----------------------------------------------------

        move_mouse_relative(
            int(mouse_dx),
            int(mouse_dy)
        )


        # ----------------------------------------------------
        # OPTIONAL TERMINAL INFORMATION
        # ----------------------------------------------------

        print(
            f"Targets={len(targets):2d} | "
            f"Target=({target['x']:.0f}, {target['y']:.0f}) | "
            f"Error=({dx:.0f}, {dy:.0f}) | "
            f"Move=({mouse_dx:.0f}, {mouse_dy:.0f})"
        )


        time.sleep(FRAME_DELAY)


except KeyboardInterrupt:

    print("\nStopping...")


finally:

    pyautogui.mouseUp()

    print("Controller stopped.")