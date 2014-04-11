##Mari Me 1.1 by Dave Girard daveg@can-con.ca
##To run, install this script to Maya scripts folder and enter these lines in the Python command line (requires that the Mari mariMeBridge.py script is install on the Mari side):
##import mariMe
##mariMe 

import maya.cmds as cmds
import maya.mel as mel
import os 
import socket
import pymel.core as pm
import re
import maya.api.OpenMaya as om2
#from datetime import datetime
import random
import time

def sendMultipler(*args):
	##GET PARAMETERS
	duped = {}
	meshID = {}
	matnodeID = ""
	meshy = {}
	appVersion = cmds.about(v=True)
	if appVersion == "Preview Release 38":
		appVersion = "2015"
	appVersion = re.search("(\d\d\d\d)", appVersion)
	appVersion = int(appVersion.group(0))
	##fullfilepath = []
	obj_namelocal = []
	textureNameUnfiltered = ""
	bitDepth = ""
	remoteHostIP = cmds.textField('mariTextFieldHost',q=True,text=1)
	channelText = cmds.textField('mariChannelText',q=True,text=1)
	fileExtension = ".obj"
	alembicStat = cmds.checkBox("mariMeBoxCheckbox12",q=1,v=1)
	updatestat = cmds.checkBox("mariMeBoxCheckbox13",q=1,v=1)
	startFrame = cmds.playbackOptions(q=1,minTime=1)
	endFrame = cmds.playbackOptions(q=1,maxTime=1)
	if alembicStat:
		fileExtension = ".abc"
		if len(cmds.ls(sl=1)) > 1:
			cmds.error("Alembic export only supports single meshes for animation.")
	#UDIMstat = cmds.checkBox('mariMeBoxCheckbox10',q=1,v=1)
	UDIMstat = 1
	##mySelection = cmds.ls( sl=True )

	smoothStat = cmds.checkBox("mariMeBoxCheckbox1",q=1,v=1)
	linuxsend = cmds.checkBox("mariMeBoxCheckbox5",q=1,v=1)
	displaceMe = cmds.checkBox("mariMeBoxCheckbox3",q=1,v=1)
	smoothIterations = cmds.intSliderGrp("mariMeSlider1",q=1,v=1)
	textureRes = cmds.intSliderGrp("mariMeSlider2",q=1,v=1)
	smoothUVs = cmds.checkBox("mariMeBoxCheckbox3",q=1,v=1)
	bitDepthCB = cmds.checkBox("mariMeBoxCheckbox6",q=1,v=1)
	bitDepthCBTwo = cmds.checkBox("mariMeBoxCheckbox7",q=1,v=1)

	if (bitDepthCB):
		bitDepth = "8"
	elif (bitDepthCBTwo):
		bitDepth = "16"
	else:
		bitDepth = "32"
	texturePath = ""
	scalarVal = cmds.checkBox("mariMeBoxCheckbox9",q=1,v=1)
	scalarString = "False"
	if (scalarVal):
		scalarString = "True"
	sceneName = cmds.textField('mariTextField',q=True,text=1)
	sendDiff = cmds.checkBox("mariMeBoxCheckbox4",q=1,v=1)
	useExistingRes = cmds.checkBox("mariMeBoxCheckbox11",q=1,v=1)
	projPath = cmds.workspace(q=True, rd=True)
	cmds.sysFile((projPath + 'MariMe'), makeDir=True)
	
	dummyGeoPath = (projPath + 'MariMe/' + "dummyGeo")
	
	##IF SEND TEXTURES IS ON, GET CHANNEL NAME FROM DROPDOWN LIST
	if (cmds.checkBox("mariMeBoxCheckbox4", q=1, value=1 )):
		textureNameUnfiltered = cmds.optionMenuGrp("textureSelect", q=1, v=1 )
		channelNameSplit = textureNameUnfiltered.split()
		channelText = channelNameSplit[0]
	
	if (smoothStat):
		duped = cmds.duplicate(rr=1)
		pm.polySmooth( kb=1, suv=1, khe=0, ksb=1, c=1, sl=4, dpe=1, ch=0)
		parentobj = cmds.ls(sl=1, o=1)
		cmds.select(parentobj, r=1)

	if (displaceMe):
		intermed = cmds.duplicate(rr=1)
		pm.polySmooth( kb=1, suv=1, khe=0, ksb=1, c=1, sl=4, dpe=1, ch=0) 
		meshy = cmds.displacementToPoly()
		cmds.delete(intermed)

	##GET THE TRANSFORM NODE IF MESH NODE IS SELECTED
	mySelection = cmds.ls( sl=True, transforms=1 )

	#IF NEW SCENE, BUILD A SINGLE QUAD TO DELETE AT END OF LOOP (WORKAROUND FOR WINDOWS NOT GETTING TAGS FOR FIRST OBJECT)	
	if not updatestat:
		mariMeDummyGeo = cmds.polyPlane(w=1111, h=1111, sx=1, sy=1)
		dummyMat = cmds.shadingNode("surfaceShader", asShader=1, n='dummyMaterial')
		cmds.select(mariMeDummyGeo[0], r=1)
		cmds.hyperShade(assign=dummyMat)
		cmds.select(mySelection, add=1)
		#FINAL MYSELECTION INCLUDES THE DUMMY GEO AS FIRST OBJECT	
		mySelection = cmds.ls( sl=True, transforms=1 )
	
	###CHECK FOR MESH ID BEFORE APPLYING IT
	for n in range(0, int(len(mySelection))):		
		if not checkForMeshID(mySelection[n]):
			meshID[n] = applyUniqueIDToMesh(mySelection[n])
		else:
			meshID[n] = checkForMeshID(mySelection[n])	
	
	if not updatestat:
		for n in range(0, 1):##EXPORT DUMMY GEO IF NOT UPDATING SCENE
			if alembicStat:
				cmds.select( mySelection[n], r=1 )
				##AbcExport -j "-frameRange 1 15 -noNormals -uvWrite -root test -file /Users/beige/Desktop/test3.abc";
				mel.eval('AbcExport -j "-frameRange '+str(startFrame)+' '+str(endFrame)+' -uvWrite -root '+mySelection[n]+' -file '+(dummyGeoPath + ".abc")+'";')
				##fullfilepath.append(projPath + "MariMe/" + meshID[n]+ ".abc")
			else:
				cmds.select( mySelection[n], r=1 )
				pm.exportSelected((dummyGeoPath + ".obj"), f=1, pr = 1, typ = "OBJexport", es = 1, op="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1")

		for n in range(1, int(len(mySelection))):##FOR ALL OBJECTS AFTER DUMMY GEO
			if alembicStat:
				cmds.select( mySelection[n], r=1 )
				##AbcExport -j "-frameRange 1 15 -noNormals -uvWrite -root test -file /Users/beige/Desktop/test3.abc";
				mel.eval('AbcExport -j "-frameRange '+str(startFrame)+' '+str(endFrame)+' -uvWrite -root '+mySelection[n]+' -file '+(projPath + "MariMe/" + meshID[n]+ ".abc")+'";')
				##fullfilepath.append(projPath + "MariMe/" + meshID[n]+ ".abc")
			else:
				cmds.select( mySelection[n], r=1 )
				pm.exportSelected((projPath + "MariMe/" + meshID[n] + ".obj"), f=1, pr = 1, typ = "OBJexport", es = 1, op="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1")
			##fullfilepath.append(projPath + "MariMe/" + meshID[n]+ ".obj")
	else:
		for n in range(0, int(len(mySelection))):##NO NEED FOR DUMMY GEO
			if alembicStat:
				cmds.select( mySelection[n], r=1 )
				##AbcExport -j "-frameRange 1 15 -noNormals -uvWrite -root test -file /Users/beige/Desktop/test3.abc";
				mel.eval('AbcExport -j "-frameRange '+str(startFrame)+' '+str(endFrame)+' -uvWrite -root '+mySelection[n]+' -file '+(projPath + "MariMe/" + meshID[n]+ ".abc")+'";')
				##fullfilepath.append(projPath + "MariMe/" + meshID[n]+ ".abc")
			else:
				cmds.select( mySelection[n], r=1 )
				pm.exportSelected((projPath + "MariMe/" + meshID[n] + ".obj"), f=1, pr = 1, typ = "OBJexport", es = 1, op="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1")
			##fullfilepath.append(projPath + "MariMe/" + meshID[n]+ ".obj")

	cmds.select(mySelection, add=1)
	
	##SOCKET STUFF
	skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
	if (linuxsend):
		skt.connect((remoteHostIP, 6100))
	else:
		skt.connect(('localhost', 6100))

	##GET MATERIAL ON SELECTED AND TAG MAT ID
	for n in range(0, int(len(mySelection))):
		mySelectionShapes = cmds.listRelatives(mySelection[n], s=1)
		try:
			textureNameUnfiltered = cmds.optionMenuGrp("textureSelect", q=1, v=1 )
			channelNameSplit = textureNameUnfiltered.split()
			shadingGroup = cmds.listSets(type=1,o=mySelectionShapes[0])
			material = cmds.listConnections(shadingGroup[0] + ".surfaceShader")
		except:
			shadingGroup = cmds.listSets(type=1,o=mySelectionShapes[0])
			material = cmds.listConnections(shadingGroup[0] + ".surfaceShader")
		
		###CHECK FOR MAT ID BEFORE APPLYING IT
		if not checkFormatnodeID(material[0]):
			matnodeID = applyUniqueIDToMat(material[0])
	
	##APPEND MESHES TO OBJ LIST FOR NEW SCENE GEO
	for n in range(0, int(len(mySelection))):
		#skt.send('obj_name.append("' + projPath + 'MariMe/' + meshID[n]+fileExtension+'")\x04')
		obj_namelocal.append('"'+projPath + 'MariMe/' + meshID[n]+fileExtension+'"')

	commandqueue = []
	
	# for n in range(0, 5):
	#     commandqueue.append('mari.geo.load ("/Users/beige/Desktop/temps/objs/voronoi_rock_'+str(n)+'.obj")')
	# commandqstring = '\n'.join(commandqueue)
	# skt.send(commandqstring+"\x04")

	##SEND WITHOUT TEXTURES	
	if (sendDiff == 0):
		if not updatestat:
			commandqueue.append("createNewSceneWithDummyObject('" + sceneName + "', '"+dummyGeoPath+fileExtension+"')")

			#SUBLOOP FOR PROPER MAT ID TAGGING OF SECONDARY GEOMETRY
			for n in range(1, int(len(mySelection))):##FOR ALL SECONDARY EXPORTED MESHES 
				mySelectionShapes = cmds.listRelatives(mySelection[n], s=1)##LOCAL VAR
				inLoopShadingGroup = cmds.listSets(type=1,o=mySelectionShapes[0])##LOCAL VAR
				inLoopMaterial = cmds.listConnections(inLoopShadingGroup[0] + ".surfaceShader")##LOCAL VAR
				inLoopMatnodeID = checkFormatnodeID(inLoopMaterial[0])
				commandqueue.append('importNewObjectAndMat('+obj_namelocal[n]+', "'+channelText+'", "null", '+str(textureRes)+', '+str(bitDepth)+')')
				commandqueue.append('matnodeTagger("'+inLoopMatnodeID+'")')
			
			
		elif updatestat:
			for n in range(0, int(len(mySelection))):##FOR ALL EXPORTED MESHES - DON'T NEED DUMMY GEO
				mySelectionShapes = cmds.listRelatives(mySelection[n], s=1)##LOCAL VAR
				inLoopShadingGroup = cmds.listSets(type=1,o=mySelectionShapes[0])##LOCAL VAR
				inLoopMaterial = cmds.listConnections(inLoopShadingGroup[0] + ".surfaceShader")##LOCAL VAR
				inLoopMatnodeID = checkFormatnodeID(inLoopMaterial[0])
				commandqueue.append('importNewObjectAndMat('+obj_namelocal[n]+', "'+channelText+'", "null", '+str(textureRes)+', '+str(bitDepth)+')')
				commandqueue.append('matnodeTagger("'+inLoopMatnodeID+'")')
				
		commandqueue.append('IDTagger()')
		commandqueue.append('projPathTagger("'+projPath+'")')		

	elif (sendDiff == 1):
		##IF CHANNEL LIST PICK ISN'T "ALL (AUTO-DETECT), SEND WITH TEXTURES USING SINGLE TEXTURE PROC:
		if textureNameUnfiltered != 'all (auto-detect)':
			##SEND THE FINAL COMMANDS TO CREATE SCENE AND LOAD MESHES AND TEXTURES
			if not updatestat:##FOR TEXTURES
				for n in range(0, 1):########SKIP FIRST MESH SINCE IT'S DUMMY GEO:
					commandqueue.append("createNewSceneWithDummyObject('" + sceneName + "', '"+dummyGeoPath+fileExtension+"')")
				# if (cmds.about(win=1)):
				# 	time.sleep(6)
				##THE FOLLOW-UP LOOP FOR OPEN SCENE:
				for n in range(1, int(len(mySelection))):###THIS USES SECOND OBJECT AND ON FOR LOOP
					#GET UNIQUE TEXTUREPATH FOR EACH MESH
					mySelectionShapes = cmds.listRelatives(mySelection[n], s=1)
					textureNameUnfiltered = cmds.optionMenuGrp("textureSelect", q=1, v=1 )
					channelNameSplit = textureNameUnfiltered.split()
					shadingGroup = cmds.listSets(type=1,o=mySelectionShapes[0])
					material = cmds.listConnections(shadingGroup[0] + ".surfaceShader")
					fileNode = cmds.listConnections(material[0] + "." + channelNameSplit[0])
					texturePath = cmds.getAttr(fileNode[0] + ".ftn")
					UDIMFileName = ""
					matchcase = ""
					if (UDIMstat):
						try:
							splitname = texturePath.split('.')
							matchcase = re.match("(\d\d\d\d)", splitname[-2])##find the match in whatever is before the file extension
						except:
							pass
						if matchcase is not None:
							splitname[-2] = '$UDIM'
							texturePath = '.'.join( splitname )##REPLACE texturePath with UDIM'ed filename
					if useExistingRes:
						try:
							allFileNodesOnChannel = findFileNodesConnectedToFileNode(fileNode[0])
							for file in allFileNodesOnChannel:
								textureResForNode = cmds.getAttr(file + '.outSizeX')
								if textureResForNode > textureRes:
									textureRes = textureResForNode ##FIND THE MAXIMUM RESOLUTION OF THE CONNECTED UDIMS AND USE THAT INSTEAD OF THE FIRST DETECTED
						except:
							pass
					commandqueue.append('importNewObjectAndMat('+obj_namelocal[n]+', "'+channelText+'", "'+texturePath+'", '+str(textureRes)+', '+str(bitDepth)+')')
					matnodeID = checkFormatnodeID(material[0])	
					commandqueue.append('matnodeTagger("'+matnodeID+'")')
					#END OLD LOOP


			##UPDATE SCENE - LOOP FOR TEXTURES 
			elif updatestat:
				for n in range(0, int(len(mySelection))):
					#GET UNIQUE TEXTUREPATH FOR EACH MESH
					mySelectionShapes = cmds.listRelatives(mySelection[n], s=1)
					textureNameUnfiltered = cmds.optionMenuGrp("textureSelect", q=1, v=1 )
					channelNameSplit = textureNameUnfiltered.split()
					shadingGroup = cmds.listSets(type=1,o=mySelectionShapes[0])
					material = cmds.listConnections(shadingGroup[0] + ".surfaceShader")
					fileNode = cmds.listConnections(material[0] + "." + channelNameSplit[0])
					texturePath = cmds.getAttr(fileNode[0] + ".ftn")
					UDIMFileName = ""
					matchcase = ""
					if (UDIMstat):
						try:
							splitname = texturePath.split('.')
							matchcase = re.match("(\d\d\d\d)", splitname[-2])##find the match in whatever is before the file extension
						except:
							pass
						if matchcase is not None:
							splitname[-2] = '$UDIM'
							texturePath = '.'.join( splitname )##REPLACE texturePath with UDIM'ed filename
					if useExistingRes:
						try:
							allFileNodesOnChannel = findFileNodesConnectedToFileNode(fileNode[0])
							for file in allFileNodesOnChannel:
								textureResForNode = cmds.getAttr(file + '.outSizeX')
								if textureResForNode > textureRes:
									textureRes = textureResForNode ##FIND THE MAXIMUM RESOLUTION OF THE CONNECTED UDIMS AND USE THAT INSTEAD OF THE FIRST DETECTED
						except:
							pass
					commandqueue.append('importNewObjectAndMat('+obj_namelocal[n]+', "'+channelText+'", "'+texturePath+'", '+str(textureRes)+', '+str(bitDepth)+')')
					matnodeID = checkFormatnodeID(material[0])	
					commandqueue.append('matnodeTagger("'+matnodeID+'")')
					#END OLD LOOP
			commandqueue.append('IDTagger()')
			commandqueue.append('projPathTagger("'+projPath+'")')
		##end - IF NAME ISN'T "ALL (AUTO-DETECT)"
		
		##LOOP FOR AUTO-DETECT CHANNELS:(UPDATE SCENE)
		if textureNameUnfiltered == 'all (auto-detect)':
			for n in range(0, int(len(mySelection))):
				##get unique texturepath for each mesh
				mySelectionShapes = cmds.listRelatives(mySelection[n], s=1)

				#SHADER PORTION FOR EACH MESH:
				shadingGroup = cmds.listSets(type=1, o=str(mySelectionShapes[0]))
				connectedShader = cmds.listConnections(shadingGroup[0] + ".surfaceShader")
				fileNodeList = findFileNodes(mySelectionShapes[0])
				##textureNodeItems = ""
				filesConnectedToShader = cmds.listConnections(connectedShader, c=1, type='file')
				##print filesConnectedToShader ##[u'VRayMtl1.color', u'pSphere12014140307125015_color_1011', u'VRayMtl1.bumpMap', u'pSphere12014140307125015_bumpMap_1011']
				channelsJustNames = []
				listChannels = []
				listChannels = filesConnectedToShader[::2]
				fileNodeForChannel = filesConnectedToShader[::-2]
				fileNodeForChannel.reverse()

				for n in range(0, int(len(listChannels)), 1): 	  
					t = (listChannels[n].split('.'))
					channelsJustNames.append(t[1])
				
				##LOAD UNIQUE MESHES INTO UNIQUE VARIABLE:
				commandqueue.append('geot'+str(n)+' = mari.geo.load('+obj_namelocal[n]+')')
				##skt.send('print geot'+str(n)+'\x04')
				##set to current (use zero list index because it's a tuple with mesh ID in [1])
				commandqueue.append('mari.geo.setCurrent(geot'+str(n)+'[0])')
				##GET RID OF THE DEFAULT "DIFFUSE" CHANNEL THAT'S CREATED FOR NEW GEO:
				commandqueue.append('delAction = mari.actions.find("/Mari/Channels/Remove Channel")')
				commandqueue.append('delAction.trigger()')

				for n in range(0, int(len(channelsJustNames))): 
					filepath = cmds.getAttr(fileNodeForChannel[n] + ".ftn")
					if useExistingRes:
						try:
							allFileNodesOnChannel = findFileNodesConnectedToFileNode(fileNode[0])
							for file in allFileNodesOnChannel:
								textureResForNode = cmds.getAttr(file + '.outSizeX')
								if textureResForNode > textureRes:
									textureRes = textureResForNode ##FIND THE MAXIMUM RESOLUTION OF THE CONNECTED UDIMS AND USE THAT INSTEAD OF THE FIRST DETECTED
						except:
							pass
					if (UDIMstat):
						splitname = filepath.split('.')
						splitname[-2] = '$UDIM'
						filepath = '.'.join( splitname )##REPLACE texturePath with UDIM'ed filename
					commandqueue.append('addChannelToCurrent("'+channelsJustNames[n]+'", "'+filepath+'", '+str(textureRes)+', '+str(bitDepth)+')')
		##END LOOP FOR AUTO-DETECT CHANNELS

	##CLEAN UP SMOOTH MESH AND DISPLACE MESH TEMPS
	if (smoothStat):
		cmds.delete(duped)
	if (displaceMe):
		cmds.delete(meshy)
	if not updatestat:
		commandqueue.append('dummyDeleter()')
	##CLEAN UP DUMMY STUFF AT ALL COSTS
	try:
		cmds.delete(mariMeDummyGeo)
		cmds.delete('dummyMaterial*')
	except:
		pass
			
	##JOIN ALL COMMANDS INTO MULTILINE QUEUE :
	commandqstring = '\n'.join(commandqueue)
	print commandqstring
	##SEND MULTILINE COMMAND QUEUE AND EVAL AFTER ALL COMMANDS TO THE MARI SIDE (this is where the magic happens)
	skt.send(commandqstring+"\x04")

def fastFixUVs(*args):
	from itertools import izip

	# Get a list of all meshes that have UVs out of range

	shapes = cmds.ls(sl=1, dag=1, leaf=1, shapes=1, long=1)
	meshes = cmds.ls(shapes, long=1, type="mesh")
	for mesh in meshes:
		
		# Get the uvs
		uvs = om2.MFnMesh(om2.MGlobal.getSelectionListByName(mesh).getDependNode(0)).getUVs()
		
		# This can get you the bounding box from the above uvs list:   
		#boundingBox = (min(uvs[0]), max(uvs[0]), min(uvs[1]), max(uvs[1]))
		# by using the bounding box you could for fit it into the box in every case:)
		
		# Do the scaling of the values in the list
		for i, (u, v) in enumerate(izip(*uvs)):
			uvs[0][i] = (u * 0.9999) + 0.00001
			uvs[1][i] = (v * 0.9999) + 0.00001
		   
		# Assign the uvs (NOT UNDOABLE, but probably the fastest way)
		# You could convert the list into a list that's usable by the mesh node from pymel those commands DO support undo.
		# Or you could convert the list to a 'mel' format.
		om2.MFnMesh(om2.MGlobal.getSelectionListByName(mesh).getDependNode(0)).setUVs(uvs[0], uvs[1])

def getMeshWithUVsOutRange(meshShapes, minU=0.0, maxU=1.0, minV=0.0, maxV=1.0):

	# Get a list of all meshes that have UVs out of range
	outsideOfRange = []
	for mesh in meshShapes:
		uvs = om2.MFnMesh(om2.MGlobal.getSelectionListByName(mesh).getDependNode(0)).getUVs()
		if any((u, v) for (u, v) in zip(uvs[0], uvs[1]) if u <= minU or u >= maxU or v <= minV or v >= maxV):
			outsideOfRange.append(mesh)
	
	return outsideOfRange
		
def UVRangeCheck(*args):
	# Get all mesh shapes nodes from the selection (note: gets any in the children hierarchy as well)
	shapes = cmds.ls(sl=1, dag=1, leaf=1, shapes=1, long=1)
	meshes = cmds.ls(shapes, long=1, type="mesh")
	
	outsideOfRange = getMeshWithUVsOutRange(meshes)

	# Do something with our filtered result
	if not outsideOfRange:
		cmds.warning("You're safe. Everything in range!")
	else:
		cmds.select(outsideOfRange, r=1)
		cmds.warning("This mesh has UVs that sit on the border so it will create empty UDIMs: "+ outsideOfRange[0])
		
def commandportButtonFlip(*args):
	cmds.commandPort(name=":7100", sourceType="python")
	if cmds.commandPort(":7100", q=1):
		cmds.button('buttonnameyname', e=1, bgc=[0.4,0.4,0.4])
	else:
		cmds.error('Failed to open port for some reason.')
		cmds.button('buttonnameyname', e=1, bgc=[0.4,1.0,0.4])

def openMariMeFolder(*args):
	basedir = cmds.workspace(q=1, rd=1)
	if (cmds.about(win=1)):
		s = "MariMe"
		t = cmds.workspace(q=1, rd=1)
		os.startfile(t+s)
	elif (cmds.about(mac=1)):
		os.system("open \"" + basedir + "MariMe\" &")
	elif (cmds.about(linux64=1)): 
		os.system("xterm -e \"" + basedir + "MariMe\" &")

def stripAllMariMeIDs(*args):
	pass

def checkFormariMeProjectPath(meshname):
	test=mel.eval('attributeExists "mariMeProjectPath" '+meshname+'')
	if (test):
		eyeDee = cmds.getAttr(meshname+".mpp")
		return eyeDee

def applyUniqueIDToMat(matNode):
	#matNodeClean = re.sub('[^a-zA-Z0-9\n]', '', str(matNode))
	typeTest = cmds.ls(matNode, showType=1)
	matnodeType = typeTest[1]
	identifierStamp = str(random.uniform(1, 10))
	identifierStamp = re.sub(r'\.', "", identifierStamp)

	cmds.addAttr(matNode, longName='MariMeMatID', shortName='mmi', dataType='string', hidden=0)
	cmds.setAttr(matNode+".mmi", (matnodeType+'.'+identifierStamp), type='string', lock=1)
	finalID = (matnodeType+'.'+identifierStamp)
	return finalID

def checkFormatnodeID(matNode):
	test=mel.eval('attributeExists "MariMeMatID" '+matNode+'')
	if (test):
		eyeDee = cmds.getAttr(matNode+".mmi")
		return eyeDee

def applyUniqueIDToMesh(meshnameRAW):
	meshnameClean = re.sub('[^a-zA-Z0-9\n]', '', str(meshnameRAW))
	#identifierStamp = cmds.date(format='YYYYYYMMDDhhmmss')
	identifierStamp = str(random.uniform(1, 10))
	identifierStamp = re.sub(r'\.', "", identifierStamp)
	cmds.addAttr(meshnameRAW, longName='MariMeID', shortName='mid', dataType='string', hidden=0)
	cmds.setAttr(meshnameRAW+".mid", (meshnameClean+identifierStamp), type='string', lock=1)
	finalID = (meshnameClean+identifierStamp)
	return finalID

def checkForMeshID(meshname):
	test=mel.eval('attributeExists "MariMeID" '+meshname+'')
	if (test):
		eyeDee = cmds.getAttr(meshname+".mid")
		return eyeDee

def mariBridge(name, channelname, finalUDIMnames, projectPath, matnodeID):
	##populate the list of mesh IDs
	appVersion = cmds.about(v=True)
	if appVersion == "Preview Release 38":
		appVersion = "2015"
	appVersion = re.search("(\d\d\d\d)", appVersion)
	appVersion = int(appVersion.group(0))
	#allnodes = cmds.ls(type="transform")
	#meshToSelect = {}##container for the actual single transform node name, not the ID
	# for n in range(0, len(allnodes)):
	# 	try:
	# 		if name in checkForMeshID(allnodes[n]):
	# 			meshToSelect[0] = allnodes[n]##get mesh from matching existing IDs by scanning all scene Nodes
	# 	except:
	# 		pass
	finalUDIMnamesList = finalUDIMnames.split('.')

	##take MatNodeID and split it ([0] is material type and [1] is the ID): phong.1245151
	splitMatNodeID = []
	matnodeType = ""
	allMatNodesofInputType = ""
	newlambertlist = []

	if matnodeID != "null":
		splitMatNodeID = matnodeID.split('.')
		matnodeType = splitMatNodeID[0]
		matnodeID = splitMatNodeID[1]
		allMatNodesofInputType = cmds.ls(exactType=matnodeType)
		#print '499:' + matnodeID
	
	##get the path from what's embedded in the Mari object:
	outputPath = (projectPath + "/MariMe/")
	
	##nameStringTrunc = ['0','1']
	##nameStringTrunc[1] = name
	matchedMat = ""
	listOfFileNodes = []
	lastfilenode = ""

	#build all the texture nodes for UDIMs if they exist
	if appVersion < 2015:##IMPORT ALL UDIM FILES
		#print '511'
		for uv in range(0, len(finalUDIMnamesList)):
			singleUDIM = finalUDIMnamesList[uv]
			newFileNodeUDIM = cmds.shadingNode("file", asTexture=1,n=name+"_"+channelname+"_"+str(singleUDIM))
			listOfFileNodes.append(newFileNodeUDIM) 
			checkerTwoDs = cmds.shadingNode("place2dTexture", asUtility=1, n=name+"_"+channelname+"_"+str(singleUDIM)+"_2DT")
			pm.setAttr((newFileNodeUDIM + ".fileTextureName"), (outputPath+name+"."+channelname+"."+finalUDIMnamesList[uv]+".tif") )###this needs to use proper UDIM values and no
			cmds.connectAttr((checkerTwoDs + ".outUV"), (newFileNodeUDIM + ".uv"))
	else:##IMPORT TWO FILES MAX AND SET IT TO UDIM NAME LATER
		for uv in range(0, 2):
			singleUDIM = finalUDIMnamesList[uv]
			newFileNodeUDIM = cmds.shadingNode("file", asTexture=1,n=name+"_"+channelname+"_"+str(singleUDIM))
			listOfFileNodes.append(newFileNodeUDIM) 
			checkerTwoDs = cmds.shadingNode("place2dTexture", asUtility=1, n=name+"_"+channelname+"_"+str(singleUDIM)+"_2DT")
			pm.setAttr((newFileNodeUDIM + ".fileTextureName"), (outputPath+name+"."+channelname+"."+finalUDIMnamesList[uv]+".tif") )###this needs to use proper UDIM values and no
			cmds.connectAttr((checkerTwoDs + ".outUV"), (newFileNodeUDIM + ".uv"))

	if listOfFileNodes > 1:
		#if appVersion < 2015:##NEED TO DO AUTO-TILEME TO SEE TILED TEXTURES
		lastfilenode = autoTileMeWithInput(listOfFileNodes)##retun the parent node of the UDIM tree to Maya for plugging into existing shader
		#elif appVersion > 2014:
		# 	lastfilenode = listOfFileNodes[0]
		# 	print '515: ' + lastfilenode
	else:
		lastfilenode = listOfFileNodes[0]

	##if there aren't tagged materials to update, make new ones and connect a new material to the ID'ed mesh: 
	# if matnodeID == "null":##the files aren't to be updated - make a new material and connect that to the mesh
	# 	newMat = cmds.shadingNode("phong", asShader=1, n=(name))
	# 	cmds.connectAttr((lastfilenode[0] + ".outColor"), (newMat + ".color"), f=1)
	# 	cmds.select(meshToSelect[0], r=1)
	# 	cmds.hyperShade(assign=newMat)
	
	#else:
	#MAKE A NEW SET OF UDIMs AND ATTACH IT TO THE PARENT MATERIAL + ."channelname"
	for n in range(0, len(allMatNodesofInputType)):
		if matnodeID in checkFormatnodeID(allMatNodesofInputType[n]):##found a match to the material
			##create new file nodes with UDIM textures
			matchedMat = allMatNodesofInputType[n]
			# allparentConnects = cmds.listConnections(oldfilenode, d=1, s=1, p=1)##just replace all connections for that file node
	 		try:
	 			cmds.connectAttr((lastfilenode[0] + ".outColor"), (matchedMat + "." + channelname), f=1)
 			except:
				cmds.connectAttr((lastfilenode[0] + ".outAlpha"), (matchedMat + "." + channelname), f=1)

def autoTileMeWithInput(listOfFileNodes):
	appVersion = cmds.about(v=True)
	if appVersion == "Preview Release 38":
		appVersion = "2015"
	appVersion = re.search("(\d\d\d\d)", appVersion)
	appVersion = int(appVersion.group(0))

	if appVersion < 2015:##MANUALLY MAKE TILES
		mySelection = listOfFileNodes
		maxNummy = len(mySelection)
		for i in range(0, int(maxNummy), 1): 
			longFileNamer = cmds.getAttr(mySelection[i] + ".ftn")
			bufferNamer = longFileNamer.split('.')
			longNumber = re.search("(..$)", bufferNamer[-2])##longNumber has both U and V info
			justVNumber = re.search("(^.)", longNumber.group(0))##justUNumber.group(0) now contains V offset
			justUNumber = re.search("(.$)", longNumber.group(0))##justVNumber.group(0) now contains V offset
			unpadUInt = justUNumber.group(0)
			unpadVInt = justVNumber.group(0)

			twoDeeConnections = cmds.listConnections(mySelection[i], type="place2dTexture", d=False, s=True)
			##cmds.setAttr((twoDeeConnections[0] + ".translateFrameU") (unpadUInt - 1))
			pm.setAttr(twoDeeConnections[0] + '.translateFrameU', (int(unpadUInt) - 1) )
			pm.setAttr(twoDeeConnections[0] + '.translateFrameV', int(unpadVInt) )
			pm.setAttr(twoDeeConnections[0] + '.wrapU', 0 )
			pm.setAttr(twoDeeConnections[0] + '.wrapV', 0 )
	
		##connect them now
		for n in range(0, int(maxNummy - 1), 1):
			cmds.connectAttr((mySelection[n] + ".outColor"), (mySelection[n+1] + ".defaultColor"))
		cmds.select(mySelection[maxNummy - 1], r=1)
		lastnode = cmds.ls(sl=1)
		print 'returning: ' + lastnode[0]
		return lastnode 

		##print ("parent texture to connect to shader is " + mySelection[maxNummy - 1] + ". It's selected.")
		##mel.eval("graphnetwork")
		
	else:##IMPORT A SINGLE TEXTURE AND JUST SET IT TO UDIM
		mel.eval('setAttr "'+listOfFileNodes[0]+'.uvTilingMode" 3;')
		mel.eval('generateUvTilePreview '+listOfFileNodes[0])
		cmds.select(listOfFileNodes[0], r=1)
		lastnode = cmds.ls(sl=1)
		return lastnode

def autoTileMe(*args):
	mySelection = cmds.ls( sl=True )

	maxNummy = len(mySelection)
	for i in range(0, int(maxNummy), 1): 
		longFileNamer = cmds.getAttr(mySelection[i] + ".ftn")
		bufferNamer = longFileNamer.split('.')
		longNumber = re.search("(..$)", bufferNamer[-2])##longNumber has both U and V info
		justVNumber = re.search("(^.)", longNumber.group(0))##justUNumber.group(0) now contains V offset
		justUNumber = re.search("(.$)", longNumber.group(0))##justVNumber.group(0) now contains V offset
		unpadUInt = justUNumber.group(0)
		unpadVInt = justVNumber.group(0)

		twoDeeConnections = cmds.listConnections(mySelection[i], type="place2dTexture", d=False, s=True)
		##cmds.setAttr((twoDeeConnections[0] + ".translateFrameU") (unpadUInt - 1))
		
		pm.setAttr(twoDeeConnections[0] + '.translateFrameU', (int(unpadUInt) - 1) )
		pm.setAttr(twoDeeConnections[0] + '.translateFrameV', int(unpadVInt) )
		pm.setAttr(twoDeeConnections[0] + '.wrapU', 0 )
		pm.setAttr(twoDeeConnections[0] + '.wrapV', 0 )

	##connect them now
	for n in range(0, int(maxNummy - 1), 1):
		cmds.connectAttr((mySelection[n] + ".outColor"), (mySelection[n+1] + ".defaultColor"))
	cmds.select(mySelection[maxNummy - 1], r=1)
	print ("parent texture to connect to shader is " + mySelection[maxNummy - 1] + ". It's selected.")
	mel.eval("graphnetwork")


def betterUVChecker(*args):
	mySelection = cmds.ls( sl=True )
	newMat = cmds.shadingNode('lambert', asShader=1, n='ChubbyChecker')
	for n in range(0, int(len(mySelection))):
		cmds.select(mySelection[0], r=1)
		cmds.hyperShade(assign=newMat)
	checkerText = cmds.shadingNode('file', asTexture=1,n='ChubbyCheckerFile')
	checkerTwoDs = cmds.shadingNode('place2dTexture', asUtility=1, n='ChubbyCheckerText')
	##get path for download
	homescriptpathy = mel.eval('getenv "MAYA_SCRIPT_PATH"')
	splitScriptPaths = homescriptpathy.split(':')
	#os.system("/usr/bin/touch " + splitScriptPaths[2] + "/gabitboot")
	fileResulter = ""
	if (cmds.about(win=1)):
		splitScriptPaths = homescriptpathy.split(';')
		fileResulter = os.path.exists(splitScriptPaths[2] + "/ppp_uvchecker.png")
	else:
		fileResulter = os.path.exists(splitScriptPaths[2] + "/ppp_uvchecker.png")

	if fileResulter:
		pm.setAttr((checkerText + '.fileTextureName'), (splitScriptPaths[2] + '/ppp_uvchecker.png') )
		cmds.connectAttr((checkerTwoDs + ".outUV"), (checkerText + ".uv"))
		cmds.connectAttr((checkerText + ".outColor"), (newMat + ".color"), f=1)
		cmds.setAttr(checkerTwoDs + ".repeatU"), 1
		cmds.setAttr(checkerTwoDs + ".repeatV"), 1

	if not fileResulter:
		import urllib
		resultD = cmds.confirmDialog(t='UV Checker mat missing',m='Download UV checker JPEG?',button=['Yes','No'],defaultButton='Yes',cancelButton='No',dismissString='No')
		if (resultD == 'Yes'):
			fullpathy = splitScriptPaths[2] + '/ppp_uvchecker.png'
			urllib.urlretrieve('http://www.can-con.ca/tumblrpics/ppp_uvchecker.png', fullpathy)
			pm.setAttr((checkerText + '.fileTextureName'), (splitScriptPaths[2] + '/ppp_uvchecker.png') )
			cmds.connectAttr((checkerTwoDs + ".outUV"), (checkerText + ".uv"))
			cmds.connectAttr((checkerText + ".outColor"), (newMat + ".color"), f=1)
			cmds.setAttr(checkerTwoDs + ".repeatU"), 1
			cmds.setAttr(checkerTwoDs + ".repeatV"), 1

		else:
			cmds.error("You need the colour PNG UV checker mat to use this.")



def justSaveOBJsPy(*args):
	testers = cmds.pluginInfo( 'objExport', query=True, loaded=True )
	if testers == False:
		cmds.loadPlugin( 'objExport')
	mySelection = cmds.ls( sl=True )
	projPath = cmds.workspace( q=True, rd=True )
	cmds.sysFile(str(projPath) + 'MariMe', makeDir=True )
	pm.exportSelected((projPath + "MariMe/" + mySelection[0] + ".obj"), f=1, pr = 1, typ = "OBJexport", es = 1, op="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1")	

def doTextureAsDiffuseMariPy(*args):
	##FIND FILE NODE FROM MENU PROC
	mySelection = cmds.ls( sl=True )
	mySelectionShapes = cmds.listRelatives(s=1)
	textureNameUnfiltered = cmds.optionMenuGrp("textureSelect", q=1, v=1 )
	channelNameSplit = textureNameUnfiltered.split()
	shadingGroup = cmds.listSets(type=1,o=mySelectionShapes[0])
	material = cmds.listConnections(shadingGroup[0] + ".surfaceShader")

	global storedMaterialmari
	typeTest = cmds.nodeType(material)

	global surfshade
	if typeTest != "surfaceShader":
		storedMaterialmari = material[0]
		#textureFileNode = textureName
		fileNode = cmds.listConnections(material[0] + "." + channelNameSplit[0])
		surfshade = cmds.shadingNode('surfaceShader', asShader=1)
		cmds.select( mySelection )
		cmds.hyperShade( assign=surfshade)
		cmds.connectAttr(fileNode[0] + '.outColor', surfshade + '.outColor', f=1 )
	elif typeTest == "surfaceShader":##restore the global variable mat
		cmds.select(mySelection[0], r=1)
		##print storedMaterialmari
		cmds.hyperShade(assign=storedMaterialmari)
		cmds.delete(surfshade)

def renameWithFilenameMari(*args):
	mySelection = cmds.ls(exactType = "file")
	county = len(mySelection)

	for i in range(0, int(county), 1):
		try:
			filename = cmds.getAttr(mySelection[i] + ".ftn")
			filed = os.path.basename(filename)
			namesansext = filed.split('.')
			cmds.rename( mySelection[i], namesansext[0] )
		except:
			pass
	buildTextureMenusMariPy()

def moveUVTiler(*args):
	if cmds.window('moveUVTilerWindow', query=True,exists=True):
		cmds.deleteUI('moveUVTilerWindow',window=True)
	moveUVTilerWindow = cmds.window('moveUVTilerWindow', widthHeight=(240, 240), menuBar=False, title="UV Tiler", resizeToFitChildren=1)
	cmds.columnLayout(adjustableColumn=True, columnAttach=('both', 10), rowSpacing=5)
	cmds.separator( height=8, style='none' )
	cmds.gridLayout( numberOfColumns=3, cellWidthHeight=(80, 80) )
	cmds.text(l="")
	cmds.button(l='move UVs\nup one\ntile', command='cmds.polyEditUV(uValue=0, vValue=1)')
	cmds.text(l="")
	cmds.button(l='move UVs\nleft one\ntile', command='cmds.polyEditUV(uValue=-1, vValue=0)')
	cmds.text(l="")
	cmds.button(l='move UVs\nright one\ntile', command='cmds.polyEditUV(uValue=1, vValue=0)')
	cmds.text(l="")
	cmds.button(l='move UVs\ndown one\ntile', command='cmds.polyEditUV(uValue=0, vValue=-1)')
	cmds.text(l="")
	cmds.setParent( '..' )
	cmds.columnLayout(adjustableColumn=True, columnAttach=('both', 10), rowSpacing=5)
	cmds.button(w=80, h=20, label="Select shell from UV", command='import maya.mel as mel\nmel.eval("polySelectBorderShell 0")')
	button5 = cmds.button(w=80, h=20, label="Test UV shells", command=UVRangeCheck)
	button6 = cmds.button(w=80, h=20, label="Scale UVs by 0.9999 to avoid edge", command=fastFixUVs)
	cmds.separator( height=8, style='none' )
	cmds.showWindow(moveUVTilerWindow)


def sliderSnapper(*args):
	textureRes = cmds.intSliderGrp("mariMeSlider2", q=True, v=True)
	if (textureRes > 512) and (textureRes < 768):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=512)
	if (textureRes > 768) and (textureRes < 1024):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=1024)
	if (textureRes > 1024) and (textureRes < 1538):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=1024)
	if (textureRes > 1538) and (textureRes < 2048):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=2048)
	if (textureRes > 2048) and (textureRes < 3072):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=2048)
	if (textureRes > 3072) and (textureRes < 4096):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=4096)
	if (textureRes > 4096) and (textureRes < 6144):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=4096)
	if (textureRes > 6144) and (textureRes < 8192):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=8192)
	if (textureRes > 8192) and (textureRes < 12288):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=8192)
	if (textureRes > 12288) and (textureRes < 16384):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=16384)
	if (textureRes > 16384) and (textureRes < 24576):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=16384)
	if (textureRes > 24576) and (textureRes < 32768):
		cmds.intSliderGrp("mariMeSlider2", e=True, v=32768)
		
def findFileNodes(*args):
	mySelection = cmds.ls( sl=True )
	mySelectionShapes = cmds.listRelatives( mySelection[0], s=True )
	se = pm.listConnections(mySelectionShapes[0], c=True, type='shadingEngine')
	fn = pm.listHistory(se, type='file')
	names = [node.name() for node in fn]
	return names

def findFileNodesConnectedToFileNode(fileNode):
	fn = pm.listHistory(fileNode, type='file')
	names = [node.name() for node in fn]
	return names

##NEW PROCEDURE WITH CHANNEL LISTING AND UPDATING FOR EMBED 
def buildTextureMenusMariPy(*args):
	if cmds.optionMenuGrp("textureSelect", exists=True):
		cmds.deleteUI('textureSelect')
	fileNodeList = {}
	cmds.optionMenuGrp("textureSelect", parent='shaderPresetLayoutMari')
	cmds.menuItem(l="Select a used channel to send")
	
	##GET THE TRANSFORM NODE IF MESH NODE IS SELECTED
	mySelection = cmds.ls( sl=True )
	for n in range(0, int(len(mySelection))):
		typeTest = cmds.ls(mySelection[n], dag=1, showType=1)
		if typeTest[1] == 'mesh':	
			mySelection[n] = cmds.listRelatives(p=1)
	   
	if (len(mySelection) == 0):
		cmds.error("You need to select a mesh and run this again.")
	else:
		mySelectionShapes = cmds.listRelatives( mySelection[0], s=True )
		sGroupTemp = cmds.listSets(type=1, o=str(mySelectionShapes[0]))
		tempy = cmds.listConnections(sGroupTemp[0] + ".surfaceShader")
		##fileNodeList = {}
		fileNodeListParentChannels = {}
		fileNodeList = findFileNodes(mySelectionShapes[0])
		textureNodeItems = ""
		
		conny = cmds.listConnections(tempy, c=1, type='file')
		channelsJustNames = []
		listChannels = []
		listChannels = conny[::2]
		
		##print listChannels
		for n in range(0, int(len(listChannels)), 1): 	  
			t = (listChannels[n].split('.'))
			channelsJustNames.append(t[1])
		
		##print channelsJustNames
		##for textureNodeItems in fileNodeList:
		##cmds.menuItem(l='all (auto-detect)')
		for n in range(0, int(len(channelsJustNames))):
			if (textureNodeItems != "<done>"):
				cmds.menuItem(l=(channelsJustNames[n]+' ('+fileNodeList[n]+')'))

def testTextureRes(*args):
	textureNameUnfiltered = cmds.optionMenuGrp("textureSelect", q=1, v=1 )
	textureNameSplit = textureNameUnfiltered.split()
	textureName = re.sub("^.","", textureNameSplit[1])
	textureName = re.sub(".$","", textureName)
	textureResX = int(cmds.getAttr(textureName + '.outSizeX'))
	textureResY = int(cmds.getAttr(textureName + '.outSizeY'))
	possibleReses = [8, 512, 1024, 2048, 4096, 8192, 16384, 32768]
	totalbadcount = 0
	if (textureResY or textureResX) not in possibleReses:
		cmds.warning(textureName+" has a bad resolution: " + str(textureResX) + " x " + str(textureResY)+". It's selected.")
		totalbadcount += 1
		cmds.select(textureName, r=1)
	if totalbadcount == 0:
		cmds.warning("Textures are proper resolution for Mari")

###PROC FOR ENABLING/DISABLING TEXTURE RES SLIDER:
def textureSliderFlipper(*args):
	flipstat = cmds.checkBox('mariMeBoxCheckbox11', q=1, v=1)
	cmds.intSliderGrp('mariMeSlider2', e=1, en=(not flipstat))

###PROC FOR ENABLING/DISABLING TEXTURE ELEMENTS:
def textureEnabler(*args):
	buildTextureMenusMariPy()
	flipstat = cmds.checkBox('mariMeBoxCheckbox4', q=1, v=1)
	cmds.checkBox('mariMeBoxCheckbox10', e=1, v=0, en=int(flipstat))
	cmds.checkBox('mariMeBoxCheckbox11', e=1, v=int(flipstat), en=int(flipstat))
	cmds.checkBox('mariMeBoxCheckbox10', e=1, v=int(flipstat), en=int(flipstat))
	cmds.intSliderGrp('mariMeSlider2', e=1, en=(not flipstat))
	cmds.optionMenuGrp("textureSelect", e=1, en=int(flipstat))
	cmds.textField('mariChannelText',e=1,en=int(not flipstat))

###GUI:
def mariMe(*args):
	windowWidth = 400
	buttonHeight = 22
	windowHeight = 520
	testSel = cmds.ls( sl=True )
	mySelection = {}
	if (len(testSel) == 0):
		mySelection = 'sceneName'
	elif (len(testSel) > 0):
		##mySelection = testSel[0]
		mySelection = re.sub('[^a-zA-Z0-9\n]', '', str(testSel[0]))	
	##elif (len(mySelection) > 0):
	##	mySelection = cmds.ls( sl=True )
	commandportStatus = cmds.commandPort(":7100", q=1)
	testersABC = cmds.pluginInfo( 'objExport', query=True, loaded=True )
	if not testersABC:
		try:
			cmds.loadPlugin( 'AbcExport')
		except:
			pass
	testers = cmds.pluginInfo( 'objExport', query=True, loaded=True )
	if not testers:
		cmds.loadPlugin( 'objExport')
	if cmds.window('mariMewindow', query=True,exists=True):
		cmds.deleteUI('mariMewindow',window=True)
	mariMewindow = cmds.window('mariMewindow', widthHeight=(400, 320), menuBar=True, title="Mari Me", rtf=1)

	cmds.columnLayout(adjustableColumn=True, columnAttach=('both', 10), rowSpacing=5)
	cmds.separator( height=8, style='none' )
	cmds.text(label='MAKE SURE TO ENABLE MARI COMMAND PORT 6100\nAND NO MATERIALS ARE MAYA LAMBERTS')
	cmds.separator( height=4, style='none' )
	cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[(1, 80), (2, 100), (3, 100), (4, 20)] )
	cmds.text(label='Scene name:')
	cmds.textField("mariTextField", width=90, text='scene')
	cmds.text(label='Channel name:')
	cmds.textField("mariChannelText", width=int(windowWidth), text="color")
	cmds.setParent( '..' )

	cmds.separator( height=1, style='single' )
	cmds.text(label='Mesh format:')

	cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 320), (2, 60)] )
	cmds.checkBox("mariMeBoxCheckbox12", label='Alembic animated mesh export (time slider range)', value=False )
	##cmds.button(w=40, h=18, label="Settings", command='import maya.mel as mel\nmel.eval("unifiedRenderGlobalsWindow")')
	cmds.setParent( '..' )

	cmds.separator( height=1, style='single' )
	
	cmds.text(label='Single smooth mesh options:')
	##cmds.separator( height=4, style='none' )
	cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 200), (2, 200)] )
	cmds.checkBox("mariMeBoxCheckbox1", label='Smooth mesh before send', cc='cmds.checkBox("mariMeBoxCheckbox3", e=True, v=False)\ncmds.checkBox("mariMeBoxCheckbox2", e=True, v=True)', value=False )
	cmds.checkBox("mariMeBoxCheckbox2", label='Smooth UVs', value=False )
	cmds.setParent( '..' )
	cmds.intSliderGrp("mariMeSlider1",  field=True, label='Smooth value', minValue=1, maxValue=6, fieldMinValue=1, fieldMaxValue=6, value=2 )
	cmds.checkBox("mariMeBoxCheckbox3", cc='cmds.checkBox("mariMeBoxCheckbox1", e=True, v=False)', label='Send tesselated and displaced mesh', value=False )
	cmds.separator( height=1, style='single' )
	
	##TEXTURE LIST STUFF
	cmds.rowColumnLayout( numberOfColumns=5, columnWidth=[(1, 170), (2, 120), (3, 40), (4, 40), (5, 40)])
	cmds.checkBox("mariMeBoxCheckbox4", cc=textureEnabler, label='Send texture from mesh', value=False )
	cmds.text(label='	 Bit depth:')
	cmds.checkBox("mariMeBoxCheckbox6",  cc="cmds.checkBox('mariMeBoxCheckbox8', e=1, v=0)\ncmds.checkBox('mariMeBoxCheckbox7', e=1, v=0)", label='8', en=1, value=False )
	cmds.checkBox("mariMeBoxCheckbox7",  cc="cmds.checkBox('mariMeBoxCheckbox6', e=1, v=0)\ncmds.checkBox('mariMeBoxCheckbox8', e=1, v=0)", label='16', en=1, value=True )
	cmds.checkBox("mariMeBoxCheckbox8",  cc="cmds.checkBox('mariMeBoxCheckbox7', e=1, v=0)\ncmds.checkBox('mariMeBoxCheckbox6', e=1, v=0)", label='32', en=1, value=False )
	
	cmds.checkBox("mariMeBoxCheckbox9", ann='created channels are created as scalar, not gamma-corrected sRGB', label='New channels are scalar', en=1, value=False )
	cmds.checkBox("mariMeBoxCheckbox10", ann='Send the associated tiles for the selected file node.', label='send UDIM files', en=0, value=False )
	cmds.setParent( '..' )
	
	##cmds.separator( height=6, style='none' )
	cmds.text(label='If send textures on, pick channel to be sent to Mari as colour\nMust be Mari-compatible format (512, 1024, etc) or they won\'t load:')
	
	##cmds.separator( height=6, style='none' )
	cmds.columnLayout("shaderPresetLayoutMari", rs=1, adjustableColumn=False)
	##mySelection = cmds.ls( sl=True )
	mySelectionShapes = {}

	if (len(mySelection) > 0):
		try:
			mySelectionShapes = cmds.listRelatives(mySelection[0], s=True)
			typeTest = cmds.ls(mySelectionShapes[0], showType=True )
			if (typeTest[1] == "mesh"):
				buildTextureMenusMariPy()
		except:
			pass

	cmds.setParent( '..' )	
	##cmds.separator( height=6, style='none' )
	cmds.columnLayout(columnAttach=('both', 40), cal=('center'), rowSpacing=3, columnWidth=420)
	button1 = cmds.button(w=80, h=22, label="Refresh textures attached to object", command=buildTextureMenusMariPy)
	button2 = cmds.button(w=80, h=22, label="Rename file nodes with filename", command=renameWithFilenameMari)
	button3 = cmds.button(w=80, h=22, label="Toggle channel as diffuse", command=doTextureAsDiffuseMariPy)
	button4 = cmds.button(w=80, h=22, label="Test texture resolution for Mari conformity", command=testTextureRes)

	if commandportStatus:
		pass
	else:
		button5 = cmds.button('buttonnameyname', w=80, h=22, label="Enable Maya command port to receive changes", bgc=[0.8,0.4,0.4], command=commandportButtonFlip)
	cmds.setParent( '..' )	

	cmds.intSliderGrp("mariMeSlider2",  field=True, label='Mari texture res:', cc=sliderSnapper, dc=sliderSnapper, minValue=512, maxValue=32768, fieldMinValue=512, fieldMaxValue=32768, value=4096 )
	cmds.checkBox("mariMeBoxCheckbox11", label='Use existing texture res', cc=textureSliderFlipper, en=0, value=False )

	cmds.separator( height=1, style='single' )
	##cmds.separator( height=6, style='none' )
	cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 300), (2, 100)] )
	cmds.checkBox("mariMeBoxCheckbox5",  label='Send to remote host (needs same paths):', value=False )
	cmds.textField("mariTextFieldHost", width=300, text="10.0.1.18")
	##setParent ('..')
	#cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 300), (2, 100)] )
	
	cmds.setParent( '..' )
	cmds.columnLayout(rowSpacing=3, columnWidth=420)

	cmds.checkBox("mariMeBoxCheckbox13", label='Send objects to current scene (default makes new scene)', value=False )

	cmds.setParent( '..' )
	button4 = cmds.button(w=150, h=30, label="Mari Me", bgc=[0.2,0.25,0.2], command=sendMultipler)

	cmds.menu( label='Utilities', tearOff=False )
	cmds.menuItem( label='UV Tile Tools', c=moveUVTiler )

	cmds.menuItem( label='Just save OBJ', ann="take the settings and just write an OBJ with them, don't send to Mari", c=justSaveOBJsPy )
	cmds.menuItem( label='Open Mari Me Folder', c=openMariMeFolder )
	cmds.menuItem( label='Auto Tile Me (select tiled file nodes)', ann="set up a tiled texture network for selected file UDIMs from Mari", c=autoTileMe)
	##cmds.menuItem( label='stripAllMariMeIDs', ann="stripAllMariMeIDs", c=stripAllMariMeIDs)
	
	
	cmds.menuItem( label='Better UV Checker', c=betterUVChecker )

	cmds.separator( height=16, style='none' )
	
	cmds.setParent( '..' )

	cmds.showWindow(mariMewindow)

mariMe()
