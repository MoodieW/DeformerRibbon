
'''
    File name: deformRibbonToLocs.py
    Author: Wayne Moodie
    Date created: 4/18/2018
    Email : moodiewayne@gmail.com
    Date last modified: 4/30/2018
    Python Version: 2.7
	
	
'''
from functools import partial
from pymel.core import *


    
def sineRibbonLocUI():
    
    def updateName(value, *args):
     
        rib.name = value
        
    def updateNum(value, *args):
     
        rib.bndJnts = value    

    
    #Create a variable for the window name
    winName = 'proceduralRibbon'
    winTitle = 'Deformer Ribbon'
    #Delete the window if it exists
    if window(winName, exists=True):
        deleteUI(winName, window=True)
    #Build the main window
    window(winName, title=winTitle, rtf=True)
    columnLayout(adjustableColumn=True)
    #Create the columnLayout
    columnLayout(adjustableColumn=True)

    #Build tab
    rib = sineRibbonLoc('Ribbon', 7)

    
    columnLayout(adjustableColumn=True)
    text(label='Name The Ribbon')
    textField('nameField', pht ='Name Here Please', cc = updateName)
    text(label='Number of Bind Joints')
    intField('jointsField', minValue=3, value=10, cc = updateNum)
    setParent( '..' )
    setParent( '..' )
    #Build tab
    columnLayout(adjustableColumn=True)
    button(label='Place Locators', rs= True, h = 50, c =  rib.createTargs)

  
  
    button(label='Create the ribbon', h = 50 , c  =  rib.createRibbon)
   

    #Show the window
    showWindow(winName)
    window(winName, edit=True, width=260, height=100)
    
    




class sineRibbonLoc():

    ''' Creates a procedural setup of the sine ribbon inspired by Jorn-Harald Paulsen. 
    The user needs to define Number of Controls,How many bind joints and the name of the
    ribbon. Run the CreateTargs function andplace the locator at the desired start andend positions. 
   
    For better results please use odd numbers for controls  '''
    
    def __init__(self, name = 'test', bndJnts = 5):
        
        '''User needed inputs '''
        
        self.bndJnts = int(bndJnts)
        self.name = str(name)
  
        
    def createTargs(self, *args):
    
        '''set target locations for ribbon'''
        
        #creates invis target 
        self.spans = self.bndJnts
        self.topTar = spaceLocator(n = self.name+'_Front_Targ')
        
        self.topTar.hide()
        move(8, y = True)
        select(cl = True)
        self.botTar =spaceLocator(n = self.name+'_Back_Targ')
        self.botTar.hide()
        move(4, y = True)
        aimConstraint(self.topTar ,self.botTar)
        aimConstraint(self.botTar , self.topTar)
        
        #creates user's locators
        self.topLocator = spaceLocator(n ='startTarget')
        move(8, y = True )
        rotate(90, y = True )
        select(cl = True)
        self.bottomLocator = spaceLocator(n = 'endTarget')
        move(4, y = True)
        rotate(90, y = True )
        
        parent(self.botTar,self.bottomLocator)
        parent(self.topTar,self.topLocator)
        select(cl =True)
    
    def createRibbon(self, *args): 
        
        '''Ribbon creation with driver joints setup'''
        
        #setupCurves
        realTarg = nurbsSquare(nr =(1,0,0))
        select('topnurbsSquare1','bottomnurbsSquare1')
        loftList = ls(sl=True)
        parent(w=True)
        xform(cp= True)
        delete(realTarg)
        rotate(180, y = True)
        parentConstraint(self.topTar ,loftList[0], mo = False )
        parentConstraint(self.botTar ,loftList[1], mo = False )
                   
        #store vectors for later use
        self.tailVec = self.bottomLocator.getTranslation()
        self.headVec = self.topLocator.getTranslation()
        posVec =  self.headVec - self.tailVec
        self.mag = posVec.length()
        
        #create targets for surface
        i=0
        while i < 2:
            loftTarg = curve(p=[(0, 0, 1), (0, 0, -1)], k=[0, 1], d=1)
            scale(.5,.5,.5)
            if i == 0:
                move(self.mag,0,0)
            loftList.append(loftTarg)
            i+=1
        
        #create our real surfaces
        
        loft(loftList[2], loftList[3], c=0, ch=1, d=3,
             ss=self.spans, rsn=True, ar=1, u=1, rn=0, po=0)
        xform(cp= True)
        self.ribbon = ls(sl=True)
        rename(self.ribbon[0] ,self.name+'_Ribbon')
        rotate(90,90,0),move(self.mag/-2,0,0), makeIdentity(a= True)
        delete(ch = True)
        select(cl=True)
        
        '''set up blendshape group'''
        
        self.blendGrp = []
        increment = -2.25
        deformers = ['Twist','Sine', 'Wire', 'Squash']
        #create blendShpe Group and translate them
        for i in deformers:
            
            blnd = duplicate(self.ribbon, n= self.name+'_blend_'+i)
            select(blnd),move(increment,18,0)
            increment+=1.5
            self.blendGrp.append(blnd)
            
        self.blendShapes = group(self.blendGrp, n= self.name+'_Blendshapes_Grp')  
        
        #create Dummy taret surface
        
        self.rotateTarg = loft(loftList[0], loftList[1], c=0, ch=1, d=3,
                               ss=self.spans, rsn=True, ar=1, u=1, rn=0, po=0)
        
        xform(cp= True)
        rename(ls(sl=True),self.name+'_Ribbon_RotTarg')
        delete(ch = True)
        select(cl=True)

        #Create Rotatation follicle Target

        self.rotTarg = createNode('follicle', n = self.name+'_FOL_RotateTarget')
       
        self.rotateTarg[0].local         >>  self.rotTarg.inputSurface
        self.rotateTarg[0].worldMatrix   >>  self.rotTarg.inputWorldMatrix
        self.rotTarg.outRotate           >>  self.rotTarg.getParent().rotate
        self.rotTarg.outTranslate        >>  self.rotTarg.getParent().translate
        self.rotTarg.getParent().inheritsTransform.set(False)
        self.rotTarg.parameterU.set(.5)
        self.rotTarg.parameterV.set(.5)
       
        #attachs to rotation target
        decompose = createNode('decomposeMatrix',n = self.name+'_decomposeMatrix')
        self.rotTarg.worldMatrix[0]  >>   decompose.inputMatrix
        decompose.outputTranslate    >>   self.ribbon[0].translate
        decompose.outputRotate       >>   self.ribbon[0].rotate
        
        self.rotTarg.worldMatrix[0]  //   decompose.inputMatrix
        decompose.outputTranslate    //   self.ribbon[0].translate
        decompose.outputRotate       //   self.ribbon[0].rotate
        
        delete(loftList, self.name+'_decomposeMatrix*',
               self.name+'_Ribbon_RotTarg')
               
               
    
        
        '''setup The controlers with their attributes and clean up dummy targets'''
        
        self.startCtrl = spaceLocator(n = self.name+'_Front_CTRL')
        self.startGRP = group(n =self.name+'_start_CTRL_GRP')
        self.midCtrl = spaceLocator(n = self.name+'_Mid_CTRL')
        self.midGRP = group(n =self.name+'_mid_CTRL_GRP')
        self.endCtrl = spaceLocator(n = self.name+'_End_CTRL')
        self.endGRP = group(n =self.name+'_end_CTRL_GRP')
        
        self.startGRP.translate.set(self.headVec)
        self.endGRP.translate.set(self.tailVec)

        decompose = createNode('decomposeMatrix',n = self.name+'_decomposeMatrix')
        self.rotTarg.worldMatrix[0] >>  decompose.inputMatrix
        decompose.outputRotate  >>  self.startGRP.rotate
        decompose.outputRotate  >>  self.endGRP.rotate
        decompose.outputRotate  >>  self.midGRP.rotate
        
        decompose.outputRotate  //  self.startGRP.rotate
        decompose.outputRotate  //  self.endGRP.rotate
        decompose.outputRotate  //  self.midGRP.rotate
         
        delete(decompose,self.rotTarg.getParent())
           
        select( self.startCtrl,self.endCtrl,self.midGRP)
        pointConstraint(mo = False)
        select(cl=True)
        
        ''' Adds our attributes for later use '''
        #Front And Back Control attributes creation
        select(self.name+'_End_CTRL', self.name+'_Front_CTRL')
        addAttr(ln="TWIST", en="Twist", at="enum", nn="---------------",hidden =False,k = True)
        addAttr(ln="twist", at = 'float',hidden =False,k = True)
        
        #Mid Control attributes creation
        select(self.name+'_Mid_CTRL')
        addAttr(ln="ROLL", en="Roll", at="enum", nn="---------------",hidden =False,k = True)
        addAttr(ln="Roll", at = 'float',hidden =False,k = True)
        addAttr(ln="Roll_Offset", at = 'float',hidden =False,k = True)
        addAttr(ln="Sine", en="Sine", at="enum", nn="---------------",hidden =False,k = True)
        addAttr(ln="Amplitude", at = 'float',hidden =False,k = True)
        addAttr(ln="Sine_Offset", at = 'float',hidden =False,k = True)
        addAttr(ln="Sine_Twist", at = 'float',hidden =False,k = True)
        addAttr(ln="Sine_falloffPosition", at = 'float',hidden =False,k = True)
        addAttr(ln='volumeSep',nn='---------------',at="enum",en='Volume',k=True)
        addAttr(ln='volume',at="float",min=-1,max=1,k=True)
        addAttr(ln='volumeMultiplier',at="float",min=1,dv=3,k=True)
        addAttr(ln='startDropoff',at="float",min=0, max=1, dv=1,k=True)
        addAttr(ln='endDropoff',at="float",min=0, max=1, dv=1, k=True)
        addAttr(ln='volumeScale',at="float",min=self.mag*-0.9, max=self.mag*2,k=True)
        addAttr(ln='volumePosition',min=self.mag*-1,max=self.mag,at="float",k=True)
        select(cl=True)
        
        #cleanup
        delete(self.topLocator ,self.bottomLocator)
        
    
        
        
        ''' Creates Follicle Grp '''
        
        select(cl=True)
        #setUp ratis and the follicle group
        i=0
        ratio = 1.0 /self.spans
        self.fol_grp = group(n=self.name+'_FOL_GRP') 
        self.jntToBeScaleList = []
        while i < self.spans:
            
            # creates Follicles and attachs them to the nurbs surface
            
            fol = createNode('follicle', n = self.name+'_'+str(i)+'_FOL_Shape')
            bndJnt = joint(n=self.name+'_'+str(i)+'_FOL_BND', rad = .1)
            grp = group(n = self.name+'_'+str(i)+'_FOL_SRT')
            ctrl = circle(n = self.name+'_'+str(i)+'_Ctrl',r = .5)
            xform(ro = (90,0,0))
            makeIdentity(apply=True, t=1, r=1, s=1, n=0)
            ctrl[0].setParent(grp)
            bndJnt.setParent(ctrl[0])
            fol.getParent().rename(self.name+'_'+str(i)+'_FOL')
            
            #attaching
            
            self.ribbon[0].local         >>  fol.inputSurface
            self.ribbon[0].worldMatrix   >>  fol.inputWorldMatrix
            fol.outRotate                >>  fol.getParent().rotate
            fol.outTranslate             >>  fol.getParent().translate
            fol.getParent().inheritsTransform.set(False)
            
            #placement
            
            offset = ratio * i
            fol.parameterU.set(.5)
            fol.parameterV.set(ratio/2+offset)
            parent(fol.getParent(),self.fol_grp)
            select(cl = True)
            
            self.jntToBeScaleList.append(grp)
            i+=1    
   
        #squash follicle setup
        select(self.blendGrp[3])
        squahBlndShp =ls(sl=True)
        select(cl = True)
        i=0
        ratio = 1.0 /self.spans
        self.squashFolGrp = group(n=self.name+'_Squash_FOL_GRP')
        
        while i<self.spans:
            # creates Follicles and attachs them to the nurbs surface
            squashFol = createNode('follicle', n = self.name+'_'+str(i)+'_Squash_FOL_Shape')
            squashTFM=fol.getParent().rename(self.name+'_'+str(i)+'_FOL')
            
            #attaching
            
            squahBlndShp[0].local        >>  squashFol.inputSurface
            squahBlndShp[0].worldMatrix  >>  squashFol.inputWorldMatrix
            squashFol.outRotate          >>  squashFol.getParent().rotate
            squashFol.outTranslate       >>  squashFol.getParent().translate
            squashFol.getParent().inheritsTransform.set(False)
            
            #placement
            
            offset = ratio * i
            squashFol.parameterU.set(0)
            squashFol.parameterV.set(ratio/2+offset)
            parent(squashFol.getParent(),self.squashFolGrp)
            select(cl = True)
            
            
            i+=1  
            
        
        
    
        
        '''setup the deformors'''
        
        
        noTfmGrp = group(n= self.name+'_NO_TFM_GRP')
        select(cl = True)
        deformerGrp = group(n= self.name+'_Deformer_GRP')
        deformers = []
        #twist setup
        select(self.blendGrp[0])
        
        self.twistHandle,self.twistDeform = nonLinear(type = 'twist')
        deformers.append(self.twistDeform)
        rename(self.twistHandle, self.name+'_Twist')
        rename(self.twistDeform, self.name+'_TwistDeform')
        twistPlusMinStart = createNode('plusMinusAverage', n= self.name+'_start_twist_plusMin')
        twistPlusMinEnd = createNode('plusMinusAverage', n= self.name+'_end_twist_plusMin')
        
        #connect to controls
        self.startCtrl.twist          >>   twistPlusMinStart.input1D[0]
        self.midCtrl.Roll             >>   twistPlusMinStart.input1D[1]
        self.midCtrl.Roll_Offset      >>   twistPlusMinStart.input1D[2]
        self.endCtrl.twist            >>   twistPlusMinEnd.input1D[0]
        self.midCtrl.Roll             >>   twistPlusMinEnd.input1D[1]
        self.midCtrl.Roll_Offset      >>   twistPlusMinEnd.input1D[2]
        twistPlusMinStart.output1D    >>   self.twistHandle.startAngle
        twistPlusMinEnd.output1D      >>   self.twistHandle.endAngle
        

        '''Wire setup'''
        select(self.blendGrp[2])
        wireBlndShp =ls(sl=True)
        
        #Find the position to draw the curve
        
        wireGeoBbox = wireBlndShp[0].getBoundingBox()
        BBoxMinX = wireGeoBbox[0][0]
        BBoxMaxX = wireGeoBbox[1][0]
        midX = (BBoxMaxX + BBoxMinX)/2
        BBoxMinY = wireGeoBbox[0][1]
        BBoxMaxY = wireGeoBbox[1][1]
        midY = (BBoxMaxY + BBoxMinY)/2
        
        #creates Clusters
        
        select(cl =True)
        wireCrv = curve(p=[(midX, BBoxMinY, 0), (midX, midY, 0),
                           (midX, BBoxMaxY, 0)], k=[0, 0, 4, 4], 
                            d=2, n= self.name+'_wireDef')
        
        select(wireCrv.cv[0:1])
        clustHandleBot = cluster(n = self.name+'_botClust')
        
       
        clustHandleBot[1].scalePivot.set(midX, BBoxMinY, 0)
        clustHandleBot[1].rotatePivot.set(midX, BBoxMinY, 0)
        
        select(wireCrv.cv[1:2])
        clustHandleTop = cluster(n = self.name+'_topClust')
        clustHandleTop[1].scalePivot.set(midX, BBoxMaxY, 0)
        clustHandleTop[1].rotatePivot.set(midX, BBoxMaxY, 0)
        
        wire(wireBlndShp ,w =wireCrv, n = self.name+'_wireDFM')
        
        self.endCtrl.translate >> clustHandleTop[1].translate
        self.startCtrl.translate >> clustHandleBot[1].translate
        
        select(wireCrv.cv[1])
        clustHandleMid = cluster(n = self.name+'_midClust')
        self.midCtrl.translate >> clustHandleMid[1].translate
        #set wieghts
        percent(clustHandleBot[0], wireCrv.cv[1], v=0.5)
        percent(clustHandleTop[0], wireCrv.cv[1], v=0.5)
        
        
        xform(cp = True)
        select(cl= True)
        
        blendShape(self.blendGrp[2], self.ribbon,
                   w=(0, 1), n = self.name+"_BlendTarget" )
                   
        blendShape(self.blendGrp[0],self.blendGrp[1], self.blendGrp[2],
                   w=[(0, 1), (1, 1)], n = self.name+"_onWireBlnd" )
                   
        select(self.blendGrp[2])
        reorderDeformers(self.name+'_wireDFM' ,self.name+"_onWireBlnd")
        
        #Sine Setup
        select(self.blendGrp[1])
        self.sineHandle,self.sineDeform = nonLinear(type = 'sine')
        rename(self.sineHandle, self.name+'_Sine')
        rename(self.sineDeform, self.name+'_SineDeform')
        self.sineHandle.dropoff.set(1)
        
        sineTyOffset = createNode('addDoubleLinear', n = self.name+'_Sine_translateOffset_Adl')
        sineSyOffset = createNode('addDoubleLinear', n = self.name+'_Sine_scaleOffset_Adl')
        sineSyOffset.input2.set(self.mag/2)
        sineTyOffset.input2.set(midY)
        
        
        self.midCtrl.Amplitude             >>   self.sineHandle.amplitude
        self.midCtrl.Sine_Offset           >>   self.sineHandle.offset
        self.midCtrl.Sine_Twist            >>   self.sineDeform.rotateY
        self.midCtrl.Sine_falloffPosition  >>   sineTyOffset.input1
        self.midCtrl.Sine_falloffPosition  >>   sineSyOffset.input1
        sineSyOffset.output                >>   self.sineDeform.scaleY
        sineTyOffset.output                >>   self.sineDeform.translateY
        
        
        
        '''setup Squash'''
        
        select(self.blendGrp[3])
        squashSurface = ls(sl=True)
        
        self.squashHandle,self.squashDeform = nonLinear(type = 'squash')
        rename(self.squashHandle, self.name+'_Squash')
        rename(self.squashDeform, self.name+'_SquashDeform')
        
        #Create the additional squash Scale to the Joints
        squashTxOut = []
        for i in self.squashFolGrp.getChildren():
            squashTxOut.append(i)
        
        #Connect Squash scale
        i= 0
        while i < self.spans:
            
            adl = createNode('addDoubleLinear', n = self.name+'_Fol_'+str(i)+'_Tx_Adl')
            mdlSquash = createNode('multDoubleLinear', n = self.name+'_volume_MDL')
            adl.input2.set(-1.75)
            
            squashTxOut[i].tx               >>  adl.input1
            adl.output                      >>  mdlSquash.input1
            self.midCtrl.volumeMultiplier   >>  mdlSquash.input2
            
            mdlSquash.output                >>  self.jntToBeScaleList[i].scaleX
            mdlSquash.output                >>  self.jntToBeScaleList[i].scaleY
            mdlSquash.output                >>  self.jntToBeScaleList[i].scaleZ
        
            i+=1
            
        self.midCtrl.volumeMultiplier.set(1)    
        #connect Attrs
        syOffsetVal = self.mag/2
        tyOffset = createNode('addDoubleLinear', n = self.name+'_translateOffset_Adl')
        syOffset = createNode('addDoubleLinear', n = self.name+'_scaleOffset_Adl')
        mdl = createNode('multDoubleLinear', n = self.name+'_volume_MDL')
        mdl.input2.set(-1)
        tyOffset.input2.set(midY)
        syOffset.input2.set(syOffsetVal)
        
        
        self.midCtrl.volume         >>   mdl.input1
        mdl.output                  >>   self.squashDeform.factor
        self.midCtrl.startDropoff   >>   self.squashDeform.startSmoothness
        self.midCtrl.endDropoff     >>   self.squashDeform.endSmoothness
        self.midCtrl.volumeScale    >>   syOffset.input1
        syOffset.output             >>   self.squashDeform.scaleY
        self.midCtrl.volumePosition >>   tyOffset.input1
        tyOffset.output             >>   self.squashDeform.translateY
        
        
        
        ###CLEANUP###
        
        parent(self.twistDeform, self.sineDeform, self.squashDeform, deformerGrp)
        select(self.name+'_wireDef*')
        self.miscGrp = group(n = self.name+'_Misc_GRP')
        select(cl=True)
        
        select(self.name+'_*Clust*')
        self.clustGrp = group(n = self.name+'_Cluster_GRP')
        select(cl=True)
        
        #Non Transform Grp
        
        parent(self.name+'_Blendshapes_Grp', self.name+'_FOL_GRP', self.name+'_Deformer_GRP',self.squashFolGrp,
               self.name+'_Cluster_GRP', self.name+'_Misc_GRP',  self.name+'_NO_TFM_GRP')
        select(cl=True)
        
        #Transform Grp
        
        select(self.name+'_Ribbon' , self.name+'_start_CTRL_GRP',
               self.name+'_mid_CTRL_GRP', self.name+'_end_CTRL_GRP')
               
        transformGrp = group(n =self.name+'_TFM_GRP')
        hide(self.clustGrp ,self.miscGrp ,self.squashFolGrp, self.blendShapes,deformerGrp)
        #scale
        
        for i in self.fol_grp.getChildren():
            scaleConstraint(transformGrp,i)
        



   
sineRibbonLoc()
