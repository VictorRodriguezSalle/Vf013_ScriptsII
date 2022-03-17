#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import maya.cmds as cmds
from cgitb import enable
from functools import partial

class ColorMapping(dict):
    def __init__(self):
        self['data']= {
            'gray':[0,(0.4,0.4,0.4)],
            'black':[1,(0,0,0)],
            'darkGray':[2,(.35,.35,.35)],
            'lightGray':[3,(.43,.43,.43)],
            'burgundy':[4,(.54,0,.11)],
            'darkBlue':[5,(0,0,.31)],
            'blue':[6,(0,0,1)],
            'darkGreen':[7,(0,.22,0.07)],
            'purple':[8,(.11,0,.2)],
            'pink':[9,(.74,0,.75)],
            'midBrown':[10,(.47,.22,.15)],
            'darkBrown':[11,(.19,.1,.09)],
            'rust':[12,(.53,.09,0)],
            'red':[13,(1,0,0)],
            'green':[14,(0,1,0)],
            'cobalt':[15,(0,.16,.54)], 
            'white':[16,(1,1,1)],
            'yellow':[17,(1,1,0)],
            'turquoise':[18,(.31,.83,1)],
            'springGreen':[19,(.18,1,.56)],
            'lightPink':[20,(1,.62,.62)],
            'sandyBrown':[21,(.87,.62,.39)],
            'paleYellow':[22,(1,1,.27)],
            'jade':[23,(0,.55,.25)],
            'lightbrown':[24,(.56,.34,.13)],
            'olive':[25,(.56,.58,.11)],
            'appleGreen':[26,(.33,.58,.12)],
            'seaGreen':[27,(.13,.58,.29)],
            'teal':[28,(.13,.57,.56)],
            'cerulean':[29,(.14,.32,.57)],
            'darkViolet':[30,(.36,.07,.57)],
            'eggPlant':[31,(.57,.11,.34)]
        }         

    def get_rgb(self, name):
        return self['data'][name][1]

    def get_index(self, name):
        return self['data'][name][0]

    def get_rgb_from_index(self, idx):
        for c, data in self['data'].items():
            if data[0] == idx:
                return data[1]

    def get_color_from_index(self, idx):
        for c, data in self['data'].items():
            if data[0] == idx:
                return c

    def get_all_color_names(self):
        return [k for k,v in sorted(self['data'].items(), key=lambda item: item[1])]



#using clases with interfaces
class myWindow:
    def __init__(self):
        self.window_title = "My fancy Window" 
        self.window_name = "myFancyWindow"
        self.widgets = dict()
        self.colors = ColorMapping()

        self.create()

    def create(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)

        self.widgets["window"] = cmds.window(
            self.window_name,
            title = self.window_title,
            sizeable=True,
            mnb = False,
            mxb = False,
            toolbox = True,
        )

        #main layout
        cmds.frameLayout("")
        self.widgets['slider'] = cmds.colorIndexSliderGrp("slider",
            label = "Control Color:", 
            min=0, 
            max=31,
            cw3 = (100, 30, 72), 
            enable = True,
            cc = partial(self.getIndexColor)
        )

        self.widgets['buttons_layout'] = cmds.shelfLayout(spacing=10)
        self.populate_buttons()
        

        cmds.showWindow(self.widgets['window'])


    def populate_buttons(self):
        for color in self.colors.get_all_color_names():
            idx = self.colors.get_index(color)


            cmds.button(l="", bgc=self.colors.get_rgb_from_index(idx), c=partial(self.addColorView, color))
            cmds.popupMenu()
            cmds.menuItem(l='viewport', c=partial(self.addColorView, color))
            cmds.menuItem(l='outliner', c=partial(self.addColorOut, color))
            cmds.menuItem(l='both', c=partial(self.addColor, color))   

    def addColorView(self, color, *args):
        for i in cmds.ls(sl=True):
            cmds.setAttr("{}.overrideEnabled".format(i), True)
            cmds.setAttr("{}.overrideColor".format(i), self.colors.get_index(color))

    def addColorOut(self, color, *args):
        for i in cmds.ls(sl=True):
            cmds.setAttr("{}.useOutlinerColor".format(i), True)
            cmds.setAttr("{}.outlinerColor".format(i), *self.colors.get_rgb(color))

    def addColor(self, color, *args):
        for i in cmds.ls(sl=True):
            cmds.setAttr("{}.overrideEnabled".format(i), True)
            cmds.setAttr("{}.overrideColor".format(i), self.colors.get_index(color))
            cmds.setAttr("{}.useOutlinerColor".format(i), True)
            cmds.setAttr("{}.outlinerColor".format(i), *self.colors.get_rgb(color))

    def setIndexColor(self, shpColor):
        '''Sets the color of a shape using Maya's Index colors.
        @shpColor(int): Index number of the color we want to set.
        '''
        
        # Save the selection
        selection = cmds.ls(sl=True) 
        i = 0

        # CHANGE SHAPE COLOR
        for obj in selection:
            # Verify and save the shapes in a list
            if cmds.nodeType(selection[i]) == "transform":
                shapeList = cmds.listRelatives(selection[i], c=1, s=1, f=1)
            else:
                shapeList.append(selection[i])
            # Change the selected shapes colors
            for shape in shapeList:
                cmds.setAttr("{}.overrideEnabled".format(shape), True)
                cmds.setAttr("{}.overrideRGBColors".format(shape), False)
                cmds.setAttr("{}.overrideColor".format(shape), shpColor)
            i = i+1

    def getIndexColor(self, *args):
        '''This function gets the slider value of the Index color and passes 
        it onto setIndexColor() function.
        @slider(str): String with the full name of the Index Color slider.
        '''
        
        value = cmds.colorIndexSliderGrp("slider", query=True, value=True)
        value = value - 1
        print(value)
        setIndexColor(value)

myWin = myWindow()