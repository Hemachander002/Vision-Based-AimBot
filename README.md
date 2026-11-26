# Vision-Based Aimbot (AI Target-Tracking Prototype)

An experimental computer vision and target-tracking pipeline built to explore concepts behind autonomous optical tracking and sensor-guided targeting systems—such as real-time object detection, target locking, and predictive trajectory estimation.

> **Disclaimer:** This project is for educational and research purposes only. Do not use it to violate Terms of Service in online multiplayer games or for unauthorized or unsafe applications.
> 
I used AI to write the code , but the PLANNING and ALGORITHM is all mine ( proud ) <3 

## Architecture

```text
[Frame Source] ---> [Preprocess] ---> [Detector] ---> [Target Selector Algorithm] ---> [Control / Aim Output] --> [Shoot]
