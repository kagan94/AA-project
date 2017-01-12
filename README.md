# SINGLE LINE IMAGE FORMATION USING TSP

! I suggest to put this img on the poster:
http://wiki.evilmadscience.com/s3/eggbot/tspart/mona-quartet.jpg
source - http://wiki.evilmadscientist.com/TSP_art

# How the project works
  It takes a PNG image as input.
  Convert it into grayscale.
  Then the program run "weighted voronoi stippling" algorithm to convert the image to points.
  Then the program run "Lin-kernighan TSP heuristic to travel accross the stippled points to find the shortest path among those points and create a final image in the form of a single line connecting all the points. 

We used "Weighted Voronoi Stippling" to get stipped image.
(source: http://www.saliences.com/projects/npr/stippling/index.html)

# Example of processed image
![](http://clip2net.com/clip/m527982/93189-clip-317kb.jpg)

# Preview of the application
![](http://clip2net.com/clip/m527982/5cff1-clip-122kb.png)
