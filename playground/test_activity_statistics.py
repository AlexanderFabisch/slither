import matplotlib.pyplot as plt
from slither.core.visualization import plot_velocity_histogram

from slither.service import Service
s = Service()
activities = s.list_activities()
a = [a for a in activities if a.has_path][0]
print(a.start_time)

plt.figure()
plot_velocity_histogram(a.get_path(), plt.gca())
plt.show()
