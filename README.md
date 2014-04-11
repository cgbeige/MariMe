MariMe by Dave Girard
=====================

A set of Python scripts for Maya and Mari to send and receive textured meshes

To view the various workflows and usage, just watch the Mari Me videos on my blog: http://polygonspixelsandpaint.tumblr.com/tagged/marime

When you send meshes from Maya to Mari with Mari Me, the script tags your materials in Maya and uses that as an identifier in Mari. Avoid using Lambert materials. There is a bug in Maya that doesn't correctly ID these for whatever reason. Any other material type is fine. Auto-tiled materials for V-Ray look bad in viewport 2 for Maya <2015 but render fine. 
