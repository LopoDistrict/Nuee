import sys
import numpy as np
from PyQt5 import QtCore, QtWidgets
import pyqtgraph.opengl as gl
from random import uniform
from PyQt5.QtCore import QTimer



#the main problem in this script is that they dont respect the screen 
# they go throught
class Bird():
    def __init__(self, x, y, z):
        self.bird_x = x
        self.bird_y = y
        self.bird_z = z

        self.bird_velocity = 6 #speed of bird recommanded between 2 and 8
        self.threshold = 0.3  # 0 <- less separated -- more separated +inf 
        #recommended between 0 - 1

        # Random normalized direction
        self.bird_facing_x, self.bird_facing_y, self.bird_facing_z = self.random_normalized_direction()

    def random_normalized_direction(self):
        """Generate a random uniform direction."""
        vec = np.array([uniform(-0.1, 0.1), uniform(-0.1, 0.1), uniform(-0.1, 0.1)])
        return vec / np.linalg.norm(vec)

    def close_random_facing(self):
        """a bit alteration the facing direction while maintaining normalization."""
        self.bird_facing_x += uniform(-0.1, 0.1)
        self.bird_facing_y += uniform(-0.1, 0.1)
        self.bird_facing_z += uniform(-0.1, 0.1)

        # Normalize
        vec = np.array([self.bird_facing_x, self.bird_facing_y, self.bird_facing_z])
        vec /= np.linalg.norm(vec)
        self.bird_facing_x, self.bird_facing_y, self.bird_facing_z = vec

    def set_average_facing(self, avg_facing):
        """Forcefully set the bird's facing direction to the flock's average."""
        self.bird_facing_x, self.bird_facing_y, self.bird_facing_z = avg_facing

    def move(self):
        """Move in the facing direction."""
        self.bird_x += self.bird_facing_x * self.bird_velocity
        self.bird_y += self.bird_facing_y * self.bird_velocity
        self.bird_z += self.bird_facing_z * self.bird_velocity


class Representation(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.view = gl.GLViewWidget()
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)
        self.resize(1920, 1080)
        self.setWindowTitle("Nuee")

        self.bird_array = []
        self.bird_objects = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_birds)
        self.timer.start(50)

    def create_bird(self, x, y, z):
        """Create a bird represented by a double triangle."""
        bird = Bird(x, y, z)
        self.bird_array.append(bird)

        # Create the two connected triangles
        bird_parts = {
            "triangle_1": gl.GLLinePlotItem(pos=np.array([[x, y, z], [x - 1, y + 1, z], [x + 1, y + 1, z], [x, y, z]]),
                                            color=(0, 1, 0, 1), width=2, antialias=True),
            "triangle_2": gl.GLLinePlotItem(pos=np.array([[x, y, z], [x - 1, y - 1, z], [x + 1, y - 1, z], [x, y, z]]),
                                            color=(0, 1, 0, 1), width=2, antialias=True)
        }

        # Add to scene
        for part in bird_parts.values():
            self.view.addItem(part)

        self.bird_objects.append(bird_parts)

    def get_average_facing(self):
        """Calculate the average normalized facing direction."""
        if not self.bird_array:
            return np.array([0, 0, 0])

        avg = np.mean([[b.bird_facing_x, b.bird_facing_y, b.bird_facing_z] for b in self.bird_array], axis=0)
        return avg / np.linalg.norm(avg)  

    def update_birds(self):
        """Update birds movements and adjust their directions."""
        avg_facing = self.get_average_facing()

        for i, bird in enumerate(self.bird_array):
            deviation = np.linalg.norm(np.array([bird.bird_facing_x, bird.bird_facing_y, bird.bird_facing_z]) - avg_facing)

            if deviation > bird.threshold:
                bird.set_average_facing(avg_facing)  # Too off-center, fully align
            else:
                bird.close_random_facing()  # Choose a random close direction

            bird.move()

            x, y, z = bird.bird_x, bird.bird_y, bird.bird_z
            bird_parts = self.bird_objects[i]

            # Update triangle positions
            bird_parts["triangle_1"].setData(pos=np.array([[x, y, z], [x - 1, y + 1, z], [x + 1, y + 1, z], [x, y, z]]))
            bird_parts["triangle_2"].setData(pos=np.array([[x, y, z], [x - 1, y - 1, z], [x + 1, y - 1, z], [x, y, z]]))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    repr = Representation()
    print("Pro Tip: use you mouse to drag around the seen")
    print("use your mouse wheel click to move around")
    bird_num = int(input("How many entities do you want (the more = the best): "))
    for _ in range(bird_num):
        repr.create_bird(uniform(-10, 10), uniform(-10, 10), uniform(-10, 10))

    repr.show()
    sys.exit(app.exec_())
