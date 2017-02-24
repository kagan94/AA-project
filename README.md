# SINGLE LINE IMAGE FORMATION USING TSP

! I suggest to put this img on the poster:
http://wiki.evilmadscience.com/s3/eggbot/tspart/mona-quartet.jpg
source - http://wiki.evilmadscientist.com/TSP_art

# How the project works
  * It takes a PNG image as input.
  * Convert it into grayscale.
  * Then the program run "weighted voronoi stippling" algorithm to convert the image to points.
  * Then the program run "Lin-kernighan TSP heuristic to travel accross the stippled points to find the shortest path among those points   and create a final image in the form of a single line connecting all the points. 

We used "Weighted Voronoi Stippling" to get stipped image.
(source: http://www.saliences.com/projects/npr/stippling/index.html)

# Example of processed image
![](https://raw.githubusercontent.com/kagan94/AA-project/master/src/1.png)

# Preview of the application
![](https://raw.githubusercontent.com/kagan94/AA-project/master/src/2.png)
