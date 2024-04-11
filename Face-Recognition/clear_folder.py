import os, time

path = "/home/admin/Pi-Sensor-Hub-with-Facial-Recognition/Face-Recognition/snapshots"
now = time.time()
x = 0.5

for filename in os.listdir(path):
    filestamp = os.stat(os.path.join(path, filename)).st_mtime
    x_days_ago = now - x * 86400
    if filestamp < x_days_ago: # if file is older than x days
        print(filename)
        os.remove(os.path.join(path, filename))
