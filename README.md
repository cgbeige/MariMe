Mari Me by Dave Girard
======================

A set of Python scripts for Maya and Mari to send and receive textured meshes

To install, put the mariMe.py script in your Maya script folder and the mariMeBridge.py in your Mari Scripts folder (~/Mari/Scripts on Mac/Linux, for example) and relaunch apps.

Enter this in the Python command line of Maya to bring up the Mari ME GUI:

import mariMe
mariMe

In Mari, you need to enable the command port in the Scripts panel of the preferences to get it to accept the commands from Maya. If you want to have Maya automatically open the Python commandport to receive the changes, you can put this in your userSetup.mel file in your scripts folder:

evalDeferred("commandPort -name \":7100\" -sourceType \"python\";");

To view the various workflows and usage of the scripts, just watch the Mari Me videos on my blog: http://polygonspixelsandpaint.tumblr.com/tagged/marime

When you send meshes from Maya to Mari with Mari Me, the script tags your materials in Maya and uses that as an identifier in Mari. Avoid using Lambert materials. There is a bug in Maya that doesn't correctly ID these for whatever reason. Any other material type is fine. Auto-tiled materials for V-Ray look bad in viewport 2 for Maya <2015 but render fine. 

If you want to have a bunch of new channel template settings for The standard V-Ray Material, replace the [AddNewChannel] text within your Mari.ini file with the text in the AddNewChannel-VRayMtl.txt file. DON'T REPLACE THE WHOLE FILE - COPY AND PASTE THE TEXT INTO THE RELEVANT SPOT. This will add a bunch of V-Ray Mtl specific presets to your new channel settings in Mari.
