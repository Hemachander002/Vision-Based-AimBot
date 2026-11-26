# Vision-Based Aimbot (AI Target-Tracking Prototype)

An experimental computer vision and target-tracking pipeline built to explore concepts behind autonomous optical tracking and sensor-guided targeting systems—such as real-time object detection, target locking, and predictive trajectory estimation.

> **Disclaimer:** This project is for educational and research purposes only. Do not use it to violate Terms of Service in online multiplayer games or for unauthorized or unsafe applications.
>
I used AI to write the code , but the PLANNING and ALGORITHM is all mine ( proud ) <3 
### Interesting thing is ,it plays better than AVG gamers and with 100% Accuracy !!!!!

demo video : https://youtu.be/Q902f4eImyA

1. Create your Virtual Environment
2. Install all the dependencies in the req.txt
3. keep aimlabs gridshot running in the background
4. run the script in the terminal and get back to the aimlabs window
5. make sure it is on fullscreen mode

## Architecture

```text
[Frame Source] ---> [Preprocess] ---> [Detector] ---> [Target Selector Algorithm] ---> [Control / Aim Output] --> [Shoot]
