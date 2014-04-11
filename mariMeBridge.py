##Mari Me Pro by Dave Girard daveg@can-con.ca
##To run, install this script to Mari scripts folder and it will put the commands in your Scripts/MariMe menu

import mari
import os
import socket
import re
import PythonQt

gui = PythonQt.QtGui

def dummyDeleter():
	allGeometry = mari.geo.list()
	for x in range(0, int(len(allGeometry))):
	    justnames = str(allGeometry[x]).split(' ')
	    regex = re.compile(r"'dummyGeo.*'")
	    matchcase = re.match(regex, justnames[0])
	    if matchcase is not None:
	        ##print justnames[0].strip('\'') 
	        mari.geo.remove(justnames[0].strip('\'') )

def createNewSceneWithDummyObject(sceneName, obj_name):
	mari.projects.create(sceneName, obj_name,[mari.ChannelInfo('channelText', 512, 512, 8, 0)], 'null')

def createLayers_ImageSetClear( image_set, color): 
    for image in image_set.imageList(): 
        image.setUniformColor( color) 

def browseForFolder():
	dirname = str(gui.QFileDialog.getExistingDirectory(0,"Select Maya Project Parent Folder for Export"))
	if dirname:
		dirname = dirname.replace( "\\", "/" ).rstrip( "/" )###Windows
		return dirname
	IDTagger(dirname) 

def importNewObjectAndMat(obj, channelname, imagepath, res, bitdepth):##update this to receive texture res and other stuff
	version = mari.app.version()
	majority = str(version.major())
	sub = str(version.minor())
	fullver = float(majority + "." + sub)
	geocol = [mari.Color( 0.5, 0.5, 0.5)]
	if fullver > 2.5:##ALREADY GETS A BASE CHANNEL SO DELETE IT
		objecty = mari.geo.load(obj) 
		mari.geo.setCurrent(objecty[0])
		node = mari.geo.current()
		#node = objecty[0]
		delAction = mari.actions.find("/Mari/Channels/Remove Channel")
		delAction.trigger()
		currentChannel = node.createChannel(channelname, res, res, bitdepth)

		if imagepath != "null":
			currentChannel.importImages(imagepath)
		else:#make an empty layer to paint on 
			layer1 = currentChannel.createPaintableLayer("Layer1") 
			createLayers_ImageSetClear( layer1.imageSet(), geocol[0]) 
			#node.setCurrentChannel(node.channel(currentChannel[0]))
	else:##ADD BASE CHANNEL
		objecty = mari.geo.load(obj) 
		mari.geo.setCurrent(objecty[0])
		node = objecty[0]
		currentChannel = node.createChannel(channelname, res, res, bitdepth)
		# Show the color channel so we can see something on the model 
		if imagepath != "null":
			currentChannel.importImages(imagepath)
		else:#make an empty layer to paint on 
			layer1 = currentChannel.createPaintableLayer("Layer1") 
			createLayers_ImageSetClear( layer1.imageSet(), geocol[0])
			#obj = mari.geo.current()
	#select through the meshes to get paint to show up:
	allGeometry = mari.geo.list()
	for x in range(0, int(len(allGeometry))):
	    mari.geo.setCurrent(allGeometry[x])

def addChannelToCurrent(channelname, imagepath, res, bitdepth):
	node = mari.geo.current()
	##imagepath = '/Users/beige/Desktop/temps/avatar.jpg'
	togettexture = node.createChannel(channelname, res, res, bitdepth)
	togettexture.importImages(imagepath)

def matnodeTagger(matnodeID):
	node = mari.geo.current()
	node.setMetadata('mariMeMatnodeID', matnodeID)

def IDTagger():
	allGeometry = mari.geo.list()
	for x in range(0, int(len(allGeometry))):
	    temper = allGeometry[x]
	    uglyCurrentGeometryName = str(temper)
	    uglyCurrentGeometryNameSolo = uglyCurrentGeometryName.split('\'')
	    temper.setMetadata('mariMeID', uglyCurrentGeometryNameSolo[1])

def projPathTagger(projPathText):
	allGeometry = mari.geo.list()
	for x in range(0, int(len(allGeometry))):
	    temper = allGeometry[x]
	    temper.setMetadata('mariMeProjectPath', projPathText)

def mayaMe(node, channeltoprocess):
	#currentGeometry = node
	
	##get metadata 
	IDDerivedName = ""
	matnodeID = ""
	projPath = ""
	
	try:
		IDDerivedName = node.metadata('mariMeID')
	except:
		pass

	try:
		matnodeID = node.metadata('mariMeMatnodeID')
	except:
		matnodeID = "null"
	
	try:
		projPath = node.metadata('mariMeProjectPath')
	except:
		projPath = browseForFolder()
		projPathTagger(projPath)
	
	#done metadata

	##node = mari.geo.current()
	currentChannel = node.currentChannel()
	if channeltoprocess != "null":
		currentChannel = channeltoprocess
	currentLayerer = currentChannel.currentLayer()
	outputPath = (projPath + "/MariMe/")
	patches = str(node.patchList())
	
	##uglyPatchList = patches.split('\'')
	finalUDIMnames = []
	nameString = str(currentChannel)
	channelnameStringTrunc = nameString.split('\'')

	##FALLBACK HERE IN CASE IT WASN'T SENT FROM MAYA'S END
	if not IDDerivedName:
		uglyCurrentGeometryName = str(node)
		uglyCurrentGeometryNameSolo = uglyCurrentGeometryName.split('\'')
		IDDerivedName = uglyCurrentGeometryNameSolo[1]

	##clean up the name so it won't screw up between filesystem or Maya
	channelnameStringTrunc[1] = re.sub('[^a-zA-Z0-9]', '', channelnameStringTrunc[1])

	regex = re.compile(r"'\d\d\d\d'")
	match = regex.findall(patches)
	finalmatchnamesCat = '.'.join(match)
	finalmatchnamesCat = finalmatchnamesCat.replace("\'","")
	finalmatchnamesList = finalmatchnamesCat.split('.')
	for n in range(0, len(finalmatchnamesList)):
		finalUDIMnames.append(finalmatchnamesList[n])

	##make a clean list of names for the final send scripts:
	# for n in range(0, len(match), 2): 
	# 	finalUDIMnames.append(uglyPatchList[n])
	
	finalUDIMnamesCat = finalmatchnamesCat
	currentChannel.exportImagesFlattened(outputPath+'/'+str(IDDerivedName)+'.'+str(channelnameStringTrunc[1])+'.$UDIM.tif')
	#print(outputPath+'/'+str(uglyCurrentGeometryNameSolo[1])+'.'+str(channelnameStringTrunc[1])+'.$UDIM.tif')
	##send the commands to Maya
	skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
	skt.connect(('localhost', 7100))
	skt.send('from mariMe import mariBridge\nmariBridge("'+str(IDDerivedName)+'", "'+str(channelnameStringTrunc[1])+'", "'+finalUDIMnamesCat+'", "'+str(projPath)+'", "'+matnodeID+'")')
	print('mariBridge("'+str(IDDerivedName)+'", "'+str(channelnameStringTrunc[1])+'", "'+finalUDIMnamesCat+'", "'+str(projPath)+'", "'+matnodeID+'")')


def sendSingler():
	currentGeometry = mari.geo.current()
	mayaMe(currentGeometry, "null")
		
def sendSinglerAllChan():
	currentGeometry = mari.geo.current()
	for chan in mari.geo.current().channelList(): 
	    ##chanstring = str(chan).split('\'')
	    ##chanstring[1]
		mayaMe(currentGeometry, chan)

def sendAller():##updated to receive all channels
	allGeometry = mari.geo.list()
	for x in range(0, len(allGeometry)):
		for chan in allGeometry[x].channelList(): 
		    ##chanstring = str(chan).split('\'')
		    ##chanstring[1]
			mayaMe(allGeometry[x], chan)
			##mayaMe(allGeometry[x], "null")


mari.menus.addAction(mari.actions.create('Maya Me (current object and current channel)', 'sendSingler()'), "MainWindow/Scripts/Mari Me")
mari.menus.addAction(mari.actions.create('Maya Me (current object and all channels)', 'sendSinglerAllChan()'), "MainWindow/Scripts/Mari Me")
##mari.menus.addAction(mari.actions.create('Maya Me (all objects)', 'sendAller()'), "MainWindow/Mari Me")
mari.menus.addAction(mari.actions.create('Maya Me (all objects and all channels)', 'sendAller()'), "MainWindow/Scripts/Mari Me")
