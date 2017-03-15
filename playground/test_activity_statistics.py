import matplotlib.pyplot as plt
from slither.gui.activity import plot_velocities


from slither.service import Service
s = Service()
activities = s.list_activities()
a = [a for a in activities if a.has_path][0]
print(a.start_time)

plt.figure()
plot_velocities(a, plt.gca())
plt.show()