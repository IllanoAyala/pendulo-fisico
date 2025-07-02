import cv2
import numpy as np
import time

from utils.config import MIN_CONTOUR_AREA, COLOR_TRACKING


def track_pendulum(app, frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if contours:
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > MIN_CONTOUR_AREA:
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                center = (cx, cy)

                cv2.circle(app.display_frame, center, 8, COLOR_TRACKING, -1)

                for i in range(1, len(app.positions)):
                    if app.positions[i - 1] is None or app.positions[i] is None:
                        continue
                    pt1 = app.positions[i - 1][1]
                    pt2 = app.positions[i][1]
                    cv2.line(app.display_frame, pt1, pt2, COLOR_TRACKING, 2)

                current_time = time.time()
                app.positions.append((current_time - app.start_time, center))

                if app.center_x_reference is None and len(app.positions) >= 30:
                    xs = [p[1][0] for p in app.positions[-30:]]
                    app.center_x_reference = int(np.mean(xs))

                if app.center_x_reference:
                    cv2.line(app.display_frame,
                             (app.center_x_reference, 0),
                             (app.center_x_reference, app.display_frame.shape[0]),
                             (0, 0, 255), 2)

                    current_side = 'left' if cx < app.center_x_reference else 'right'

                    if app.last_side and current_side != app.last_side:
                        if app.crossed_center_time:
                            elapsed = current_time - app.crossed_center_time
                            if elapsed > 0.3:
                                period_duration = elapsed * 2
                                app.periods.append(period_duration)
                                app.timestamps.append(time.strftime('%H:%M:%S'))
                                app.period_count += 1
                        app.crossed_center_time = current_time

                    app.last_side = current_side

                    amplitude = abs(cx - app.center_x_reference)
                    app.amplitude_data.append((current_time - app.start_time, amplitude))

                avg_period = sum(app.periods) / len(app.periods) if app.periods else 0
                cv2.putText(app.display_frame, f"Periodos: {app.period_count}", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
                cv2.putText(app.display_frame, f"Periodo medio: {avg_period:.2f}s", (10, 35),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
