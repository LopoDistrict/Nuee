import sys
import numpy as np
from PyQt5 import QtCore, QtWidgets
import pyqtgraph.opengl as gl
from random import uniform
from PyQt5.QtCore import QTimer

class Bird():
    def __init__(self, x, y, z):
        self.bird_x = x
        self.bird_y = y
        self.bird_z = z

        self.bird_velocity = 12  # Speed of bird recommended between 2 and 8
        self.threshold = 0.3  # 0 <- less separated -- more separated +inf 
        # Recommended between 0 - 1

        # Random normalized direction
        self.bird_facing_x, self.bird_facing_y, self.bird_facing_z = self.random_normalized_direction()

        self.box_size_birds = [
            (-300, -300, 300), #1e point upper carre
            (-300, 300, 300),
            (300, 300, 300), #...
            (300, -300, 300), #4e point
            (-300, -300,-300), #1e point sub-carre
            (-300, 300, -300),
            (300, 300, -300), #...
            (300, -300, -300), #4e point
        ]

    def random_normalized_direction(self):
        """Generate a random uniform direction."""
        vec = np.array([uniform(-0.1, 0.1), uniform(-0.1, 0.1), uniform(-0.1, 0.1)])
        return vec / np.linalg.norm(vec)

    def close_random_facing(self):
        """A bit alteration the facing direction while maintaining normalization."""
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
        """Move in the facing direction, but stay within the box."""
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
        self.resize(800, 800)
        self.setWindowTitle("Nuee")

        self.bird_array = []
        self.bird_objects = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_birds)
        self.timer.start(50)

        self.bird_movement_timer = QTimer()  # Separate timer for moving the bird
        self.bird_movement_timer.timeout.connect(self.move_bird_towards_box)

        # Taille de la boite en matrix 
        # Les 3 premiers sont le carré sup
        self.box_size_birds = [
            (-300, -300, 300), #1e point upper carre
            (-300, 300, 300),
            (300, 300, 300), #...
            (300, -300, 300), #4e point
            (-300, -300,-300), #1e point sub-carre
            (-300, 300, -300),
            (300, 300, -300), #...
            (300, -300, -300), #4e point
        ]

    def show_box(self):
        box1 = gl.GLLinePlotItem(pos=np.array([[-300, -300, 300], [-300, 300, 300], [300, 300, 300], [300, -300, 300], [-300, -300, 300]]),
                                color=(1, 1, 1, 0.2), width=2, antialias=True)

        box2 = gl.GLLinePlotItem(pos=np.array([[-300, -300, -300], [-300, 300, -300], [300, 300, -300], [300, -300, -300], [-300, -300, -300]]),
                                color=(1, 1, 1, 0.2), width=2, antialias=True)

        box3 = gl.GLLinePlotItem(pos=np.array([[-300, -300, 300], [-300, -300,-300], [-300, 300, 300], [-300, 300, -300], [300, 300, 300], [300, 300, -300], [300, -300, 300], [300, -300, -300]]),
                                color=(1, 1, 1, 0.2), width=2, antialias=True)
        self.view.addItem(box3)
        self.view.addItem(box1)
        self.view.addItem(box2)

    def steer_away_from_boundary(self, bird):
        """Steer the bird away from boundaries only if close."""
        margin = 50  # Distance from the boundary where steering starts
        force_strength = 0.1  # Adjusted steering force for smoother turns

        steering_force = np.array([0.0, 0.0, 0.0])

        # Check X boundaries
        if bird.bird_x < self.box_size_birds[0][0] + margin:
            steering_force[0] = force_strength
        elif bird.bird_x > self.box_size_birds[3][0] - margin:
            steering_force[0] = -force_strength

        # Check Y boundaries
        if bird.bird_y < self.box_size_birds[0][1] + margin:
            steering_force[1] = force_strength
        elif bird.bird_y > self.box_size_birds[3][1] - margin:
            steering_force[1] = -force_strength

        # Check Z boundaries
        if bird.bird_z < self.box_size_birds[0][2] + margin:
            steering_force[2] = force_strength
        elif bird.bird_z > self.box_size_birds[3][2] - margin:
            steering_force[2] = -force_strength

        # Apply the steering force
        if np.linalg.norm(steering_force) > 0:
            steering_force /= np.linalg.norm(steering_force)
            bird.bird_facing_x += steering_force[0] * force_strength
            bird.bird_facing_y += steering_force[1] * force_strength
            bird.bird_facing_z += steering_force[2] * force_strength
            
            # Normalize direction
            direction = np.array([bird.bird_facing_x, bird.bird_facing_y, bird.bird_facing_z])
            direction /= np.linalg.norm(direction)
            bird.bird_facing_x, bird.bird_facing_y, bird.bird_facing_z = direction

    def is_moving_away_from_boundary(self, bird):
        """Check if the bird is moving away from the boundary."""
        margin = 50
        dead_zone = 100  # Distance from the boundary where steering stops entirely

        # Check if the bird is far enough from the boundary
        if (bird.bird_x > self.box_size_birds[0][0] + dead_zone and
            bird.bird_x < self.box_size_birds[3][0] - dead_zone and
            bird.bird_y > self.box_size_birds[0][1] + dead_zone and
            bird.bird_y < self.box_size_birds[3][1] - dead_zone and
            bird.bird_z > self.box_size_birds[0][2] + dead_zone and
            bird.bird_z < self.box_size_birds[3][2] - dead_zone):
            return True  # Bird is far from any boundary

        # Check X boundaries
        if bird.bird_x < self.box_size_birds[0][0] + margin:
            return bird.bird_facing_x > 0  # Moving right (away from left boundary)
        elif bird.bird_x > self.box_size_birds[3][0] - margin:
            return bird.bird_facing_x < 0  # Moving left (away from right boundary)

        # Check Y boundaries
        if bird.bird_y < self.box_size_birds[0][1] + margin:
            return bird.bird_facing_y > 0  # Moving up (away from bottom boundary)
        elif bird.bird_y > self.box_size_birds[3][1] - margin:
            return bird.bird_facing_y < 0  # Moving down (away from top boundary)

        # Check Z boundaries
        if bird.bird_z < self.box_size_birds[0][2] + margin:
            return bird.bird_facing_z > 0  # Moving forward (away from back boundary)
        elif bird.bird_z > self.box_size_birds[3][2] - margin:
            return bird.bird_facing_z < 0  # Moving backward (away from front boundary)

        return True  # Not near any boundary

    def check_if_coords_in_box(self, x, y, z):
        """Check if a given coordinate is outside the box: defined by self.box_size_birds."""
        if x < self.box_size_birds[0][0] or x > self.box_size_birds[3][0]:
            return (True, "x")
        elif y < self.box_size_birds[0][1] or y > self.box_size_birds[3][1]:
            return (True, "y")
        elif z < self.box_size_birds[0][2] or z > self.box_size_birds[3][2]:
            return (True, "z")
        else:
            return (False, None)
           
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

    def align_bird_and_wait(self, bird):
        """Adjust the bird's direction to steer away from boundaries."""
        steering_force = self.steer_away_from_boundary(bird)

        if np.linalg.norm(steering_force) > 0:
            # Gradually adjust the bird's direction using the steering force
            bird.bird_facing_x += steering_force[0] * 0.1
            bird.bird_facing_y += steering_force[1] * 0.1
            bird.bird_facing_z += steering_force[2] * 0.1

            # Normalize the direction vector
            direction = np.array([bird.bird_facing_x, bird.bird_facing_y, bird.bird_facing_z])
            direction /= np.linalg.norm(direction)
            bird.bird_facing_x, bird.bird_facing_y, bird.bird_facing_z = direction

    def move_bird_towards_box(self, bird):
        """Move the bird back into the box."""
        deviation_face = self.check_if_coords_in_box(bird.bird_x, bird.bird_y, bird.bird_z)
        if deviation_face[0]:
            match deviation_face[1]:
                case "x":
                    if bird.bird_x < self.box_size_birds[0][0]:
                        bird.bird_x = self.box_size_birds[0][0] + 1
                    else:
                        bird.bird_x = self.box_size_birds[3][0] - 1
                case "y":
                    if bird.bird_y < self.box_size_birds[0][1]:
                        bird.bird_y = self.box_size_birds[0][1] + 1
                    else:
                        bird.bird_y = self.box_size_birds[3][1] - 1
                case "z":
                    if bird.bird_z < self.box_size_birds[0][2]:
                        bird.bird_z = self.box_size_birds[0][2] + 1
                    else:
                        bird.bird_z = self.box_size_birds[3][2] - 1

    def update_birds(self):
        """Update birds movements and adjust their directions."""
        avg_facing = self.get_average_facing()

        for i, bird in enumerate(self.bird_array):
            # Only steer if close to the boundary
            if not self.is_moving_away_from_boundary(bird): 
                self.steer_away_from_boundary(bird)

            # Align with the flock's average direction
            deviation = np.linalg.norm(np.array([bird.bird_facing_x, bird.bird_facing_y, bird.bird_facing_z]) - avg_facing)
            if deviation > bird.threshold:
                bird.set_average_facing(avg_facing)  # Too off-center, fully align
            else:
                bird.close_random_facing()  # Choose a random close direction

            # Move the bird
            bird.move()

            # Update the bird's position in the visualization
            x, y, z = bird.bird_x, bird.bird_y, bird.bird_z
            bird_parts = self.bird_objects[i]
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
    repr.show_box()
    repr.show()
    sys.exit(app.exec_())