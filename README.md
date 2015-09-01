# Handwriting
A small script that converts images into gcode for use in a handwriting machine

This uses a combination of PIL, numpy, and OpenCV2 to first detect edges in the image, specifically highlight those edges, vectorize the edges, and create gcode that follows the vectors.

Photos in action:

![Photo](http://i.imgur.com/5n2pR9E.jpg)
![Photo](http://i.imgur.com/8OyD6DH.jpg)
![Photo](http://i.imgur.com/J7W776o.jpg)