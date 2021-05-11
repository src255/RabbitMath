import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import matplotlib.animation as ani


def dr_dt(r, t):
    
    return [r[1], -g/R * np.sin(r[0])]


def space(a, b):
    if a <= 0:
        return np.linspace(a, 0, b)
    else:
        return np.linspace(0, a, b)
        

def local_min(a):
    for j in range(1, len(a)):
        if a[j] < a[j-1] and a[j] < a[j+1]:
            return j


def local_max(a, b):
    for j in range(b, len(a)):
        if a[j] > a[j-1] and a[j] > a[j+1]:
            return j


def gt(a, b, c):
    for j in range(c, len(a)):
        if b < a[j]:
            return j


# CHOOSE YOUR LAUNCH ANGLE IN RADIANS
theta_L = 1.2

# other initial values
theta_0 = np.pi/2                       # initial angle (speed = 0)
g = 9.81                                # gravity
R = 2                                   # radius of swing
H = 0.5                                  # height off ground
swing_supports = True                   # choose if you want to show swing supports
semicircle = False                      # choose if you want to show swing semicircle

# calculated  initial values
x_L = R * np.sin(theta_L)               # x at launch
y_L = R * (1 - np.cos(theta_L)) + H     # y at launch
v_r = np.sqrt(2*R*g*np.cos(theta_L))    # speed at launch
v_x = v_r * np.cos(theta_L)             # x speed at launch
v_y = v_r * np.sin(theta_L)             # y speed at launch

# solving pendulum ODE
end = int(np.ceil(3/2*np.pi*np.sqrt(g/R)))
fps = 60
q = end * fps
t = np.linspace(0, end, q)
dt = 1 / fps  # time step in seconds
DT = 1000 / fps  # time step in milliseconds
r0 = [np.pi/2, 0]            
rs = odeint(dr_dt, r0, t)
angle = np.array(rs[:, 0])
x = R * np.sin(angle)
y = R * (1 - np.cos(angle)) + H
if theta_0 <= np.pi/2:
    c1 = local_min(x)
else:
    c1 = local_max(x, local_min(x))
c2 = gt(angle, theta_L, c1)

# create the figure
fig = plt.figure()
ax = plt.axes(xlim=(-R-1, 3*R), ylim=(0, np.ceil(2*R + H)))
plt.xticks(np.arange(-R - 1, 3*R, step=1))
plt.yticks(np.arange(0, np.ceil(2*R + H), step=1))
ax.set_aspect("equal")
ax.grid()

# plot the swing
if semicircle:
    x_swing = np.linspace(-R, R, 200)
    y_swing = R + H - np.sqrt(R**2 - np.square(x_swing))
    swing = ax.plot(x_swing, y_swing, color='black', linestyle='-', lw=2)
centre = ax.plot(0, R + H, 'k.', markersize=10)
launch_point = ax.plot(x_L, y_L, 'r.', markersize=10)
if swing_supports:
    x_support1 = np.linspace(-R/3, 0, 200)
    y_support1 = 3*(R + H)/R * x_support1 + R + H
    x_support2 = np.linspace(0, R/3, 200)
    y_support2 = -3*(R + H)/R * x_support2 + R + H
    supports = ax.plot(x_support1, y_support1, x_support2, y_support2, color='black', linestyle='-', lw=2)

# plot the chain
chain_data = [[], []] * q
for j in range(q):
    X = space(x[j], q)
    if x[j] == 0:
        chain_data[j] = [X, list(np.linspace(H, R + H, q))]
    else:
        chain_data[j] = [X, list(((R + H - y[j])/-x[j]) * np.array(X) + R + H)]
chain, = ax.plot(chain_data[0][0], chain_data[0][1], lw=2, color='green', linestyle='-')

# plot the rider
x_rider = [-R - 1] * q
y_rider = [-1] * q
for j in range(c2):
    x_rider[j] = x[j]
for j in range(c2):
    y_rider[j] = y[j]
x_rider[c2] = x_L
y_rider[c2] = y_L
c = c2
while 0 <= y_rider[c]:
    c += 1
    x_rider[c] = x_rider[c-1] + v_x * dt
    v_yprev = v_y
    v_y -= g * dt
    v_yavg = (v_yprev + v_y) / 2
    y_rider[c] = y_rider[c-1] + v_yavg * dt
x_rider = [x for x in x_rider if x != -1-R]
y_rider = [y for y in y_rider if y != -1]
N = len(x_rider)
rider, = ax.plot(x_rider[0], y_rider[0], 'g.', markersize=10)

# plot the path of rider
x_path = [x_rider[j] for j in range(c1, N)]
y_path = [y_rider[j] for j in range(c1, N)]
path, = ax.plot(x_path[0], y_path[0], color='green', linestyle='--', lw=2)


def motion(i):
    chain.set_data(chain_data[i][0], chain_data[i][1])
    rider.set_data(x_rider[i], y_rider[i])
    if c1 <= i:
        path.set_data(x_path[:i - c1], y_path[:i - c1])
    # final distance text
    # if N - 1 <= i:
    #     final_x = "{:.3f}".format(x_rider[N - 1])
    #     ax.text(x_rider[N - 1] / 3, R, 'Final Distance: ' + final_x, color='black', fontsize=10)


Writer = ani.writers['ffmpeg']
writer = Writer(fps=60, metadata=dict(artist='Me'), bitrate=1800)

anim = ani.FuncAnimation(fig, motion, frames=N, interval=DT, repeat=False)
anim.save('motion.mp4', writer=writer)

