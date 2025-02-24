# Nuee
Nuée \nɥe\ is the French for flocking or swarm, is a 3D Simulation of bird in a group.
This project is inspired by the [Boids algorithm](https://en.wikipedia.org/wiki/Boids) wich stipulates 3 fundamental rules:
-  Separation: avoid one crowded instigable block of bird
-  Alignement: In order to have all the bird to go on the same direction we need to make them align with each other
-  Cohesion: To move towards the average position
A Really impressive algorithm for 1986.

This project is basically an a rough application of this method into a 3D environnement.


# Exemple video
<p align="center">
  <video src="exemple.mp4" width="500px"></video>
</p>

<video src="exemple.mp4" width="320" height="240" controls></video>

![video](exemple.mp4)


# Use 

### You have to install the packages
```
pip install PyQt5
pip install pyqtgraph
pip install numpy
```

### then clone this repo
```
git clone https://github.com/LopoDistrict/Nuee.git
```

### then run the main file
```
python main.py
#OR
python3 main.py
```

# Warning
This project is not totally completed. I observe with a large number of birds the crowd velocity is slow down at the contrary of a small group of birds
Moreover, the birds are flying way away from the sreen and doesnt stop (need to fix that), but for now you need to use your mouse and wheel to control your camera
