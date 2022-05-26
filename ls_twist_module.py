#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module_name: ls_twist_module.py
-
Primary Author: Victor Rodriguez
Primary Author e-mail: victor24rt@gmail.com
Date: 21/04/2022
-
Copyright (c) La Salle Campus Barcelona 2022. All rights reserved
"""

import pymel.core as pm

import logging
logger = logging.getLogger(__name__) 
logger.setLevel(logging.DEBUG)

class RigBaseModule(object):
    def __init__(self, side, module_name, debug):
        """
        
        Prepares the base structure for a rig module

        Args:
            side (str): rig side where the module will be placed. Valid sides: ["l", "C"]
            module_name (str): global name for the module
            debug (bool): if True iser info will be displayed
        """

        #input data
        self.side = side
        self.module_name = module_name
        self.debug = debug

        #module data
        self._nd = NodeCreator(side, module_name, debug)

        #Output Data
        self.module_rig_group = ""
        self.module_skel_group = ""
        self.module_controls_group = ""

    def prepare(self):
        """
        Creates the groups that will be usually nedded for any kind of rigging module
        """
        self.module_rig_group = self._nd.create(node_type='transform', token='Rig', suffix="grp")
        self.module_skel_group = self._nd.create(node_type='transform', token='Skel', suffix="grp")
        self.module_controls_group = self._nd.create(node_type='transform', token='Ctl', suffix="grp")

class NodeCreator():
    def __init__(self, side, description, debug):
        """
        Initializes the node creator with some simple information

        Args:
            side (str): rig side where the module will be placed. Valid sides: ["l","C","R",""]
            description (str): base name of the node creator, all the nodes will be using this basename
            debug (bool): if True iser info will be displayed
        """

        if not isinstance(side, str) or side not in ["L","C","R", ""]:
            raise ValueError("'side' must be on type string. Accepted values are ['L', 'C', 'R'', '']")

        if not isinstance(description, str):
            raise TypeError("'description' must be of type string")

        if not isinstance(debug, bool):
            raise TypeError("'debug' must be of type boolean")

        if side:
            side = side + "_"
        self.side = side

        self.description = description
        
        # node suffix mapping
        self._node_types = {
            "decomposeMatrix" : "DCM",
            "joint" : "JNT",
            "composeMatrix" : "CMP",
            "motionPath" : "MPA",
            "multDoubleLin" : "MDL",
            "transform" : "TRN",
            "locator" : "LOC",
            "multMatrix" : "MTX",
            "decomposeMatrix" : "DCMTX",
            "composeMatrix" : "CMTX",
            "multDoubleLinear" : "MDL"
        }

    def create(self, node_type, side=None, description=None, token='', suffix=None):
        """
            Creates a given node based on side, node_type and tokens
        """
        if side is None:
            side = self.side
        else:
            if not isinstance(side, str) or side not in ["L","C","R", ""]:
                raise ValueError("'side' must be on type string. Accepted values are ['L', 'C', 'R'', '']")
            
            if side:
                side = side +  "_"

        description = description or self.description

        if not suffix:
            suffix = self._node_types.get(node_type, "UNK")

        name = side + description + token + "_" + suffix

        node = pm.createNode(node_type, name = name)

        return node

class AdvancedTwist(RigBaseModule):
    def __init__(self, side, module_name, debug, curve, start_trn, end_trn, aim_axis, num_outputs=5): 
        super(AdvancedTwist, self).__init__(side, module_name, debug) 

        self._valid_axis = "X Y Z -X -Y -Z".split()

        aim_axis = aim_axis.upper()

        if aim_axis not in self._valid_axis:
            raise ValueError("aim axis not recognised")

        self._input_data = {
            'curve':curve,
            'start_trn': start_trn,
            'end_trn': end_trn,
            'aim_axis': aim_axis,
            'num_outputs' : num_outputs

        }

        self._module_data = {

        }

        self._output_data = {
            'start_trn': start_trn,     
            'end_trn': end_trn,
            'inputs_trn': self._nd.create(node_type='transform', token='Inputs'),
            'outputs_trn' : self._nd.create(node_type='transform', token='Outputs'),
            'output_transforms' : list(),
            'output_joints': list(),
            'decomp_mtx_rotate' : self._nd.create(node_type="decomposeMatrix", token = "DecomposeRotate")


        }


    def prepare(self):
        super(AdvancedTwist, self).prepare()
        # we will need to delete the temp nodes that we create

    def create(self):
        """
        Put all the logic together to create the twisting tranforms
        """

        assert self.module_rig_group, '"prepare" the module or at least assign a transform to "self.module_rig_group"'

        
        self._create_inputs_and_outputs()
        
        self._attach_xforms_to_curve()
               
        self._aim_constraints()


    def _create_inputs_and_outputs(self):
        inputs = self._output_data.get('inputs_trn')
        pm.addAttr(inputs, ln="worldUpObject", at="matrix")  
        pm.addAttr(inputs, ln="worldUpObjectEnd", at="matrix")

        outputs = self._output_data.get('outputs_trn')
        pm.addAttr(outputs, ln="outputMatrix", at='matrix', multi=True) 

        self._input_data.get("start_trn").worldMatrix >> inputs.worldUpObject
        self._input_data.get("end_trn").worldMatrix >> inputs.worldUpObjectEnd        
        self._input_data.get("start_trn").translate >> self._input_data['curve'].controlPoints[0]
        self._input_data.get("end_trn").translate >> self._input_data['curve'].controlPoints[2]
        
        mult_mtx_offset = self._nd.create("multMatrix", token = "Offset")
        decomp_mtx_offset = self._nd.create("decomposeMatrix", token = "DecomposeOffset")
        comp_mtx = self._nd.create("composeMatrix", token = "Compose")
        
        self._input_data.get("end_trn").worldMatrix[0] >> mult_mtx_offset.matrixIn[0]
        self._input_data.get("start_trn").worldInverseMatrix[0] >> mult_mtx_offset.matrixIn[1]
        mult_mtx_offset.matrixSum >> decomp_mtx_offset.inputMatrix
        
        decomp_mtx_offset.outputQuatX >> comp_mtx.inputQuatX
        decomp_mtx_offset.outputQuatW >> comp_mtx.inputQuatW
        
        pm.setAttr(comp_mtx.useEulerRotation, 0)
        
        comp_mtx.outputMatrix >> self._output_data.get("decomp_mtx_rotate").inputMatrix       
        

            
            
        

    def _attach_xforms_to_curve(self):
        percent_increment = 1.0 / (self._input_data['num_outputs'] - 1)
        axis = self._input_data['aim_axis'].replace("-", "")
        axis_index = self._valid_axis.index(axis)
        negative_axis = (self._valid_axis.index(self._input_data['aim_axis']) > 2) 

        inputs = self._output_data.get('inputs_trn')
        outputs = self._output_data.get('outputs_trn')
        

        for i in range(self._input_data['num_outputs']):
                number = str(i).zfill(2)
                mpath_base = self._nd.create("motionPath", side=self.side, token='Orient_{}'.format(number))

                mpath_base.frontAxis.set(axis_index)
                mpath_base.inverseFront.set(negative_axis)
                mpath_base.upAxis.set(2)
                mpath_base.fractionMode.set(True)
                mpath_base.uValue.set(percent_increment * i)

                self._input_data['curve'].worldSpace >> mpath_base.geometryPath

                comp_mtx_base = self._nd.create("composeMatrix", token="base_orientation_{}".format(number))
                mpath_base.allCoordinates >> comp_mtx_base.inputTranslate
                mpath_base.rx >> comp_mtx_base.inputRotateX
                mpath_base.ry >> comp_mtx_base.inputRotateY
                mpath_base.rz >> comp_mtx_base.inputRotateZ
                
                mult_mtx_extractTwist = self._nd.create("multMatrix", token="multMtx_extractTwist_{}".format(number))
                    
                loc_comp = pm.spaceLocator(n="loc_twist_{}".format(number))
                pm.setAttr("{}.overrideEnabled".format(loc_comp), True)
                pm.setAttr("{}.overrideColor".format(loc_comp), 17)
                
                mpath_base.allCoordinates >> loc_comp.translate

    
   
    def _aim_constraints(self):
        num = range(self._input_data['num_outputs'])              
              
        for i in num:   
            percent_increment = 1.0 / (self._input_data['num_outputs'] - 1)
            mult_dbl = self._nd.create("multDoubleLinear", token = "increment_perct")
            
            pm.setAttr(mult_dbl.input2, percent_increment * i)
            self._output_data.get("decomp_mtx_rotate").outputRotateX >> mult_dbl.input1
            
            number = str(i).zfill(2)
            number_next = str(i+1).zfill(2)
            number_last = str(i-1).zfill(2)           
                       
            if i != num[-1]:
                aim_con = pm.aimConstraint("loc_twist_{}".format(number_next), "loc_twist_{}".format(number), aim=(1,0,0), wut="none")
                mult_dbl.output >> aim_con.offsetX

                                
            else:
                aim_con_rev = pm.aimConstraint("loc_twist_{}".format(number_last), "loc_twist_{}".format(number), aim=(-1,0,0), wut="none")
                mult_dbl.output >> aim_con_rev.offsetX
            
                
            
            
            
            
        
                