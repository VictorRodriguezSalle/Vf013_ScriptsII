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
logger = logging.getLogger(__name__)  #en vez de usar file con el path, en el name ponemos el nombre del archivo
logger.setLevel(logging.DEBUG)

class RigBaseModule():
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
            raise ValueError("'side' must be on type string. Accepted values are ['L', "C', 'R'', '']")

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
            "transform" : "TRN"
        }

    def create(self, node_type, side=None, description=None, token='', suffix=None):
        """
            Creates a given node based on side, node_type and tokens
        """
        if side is None:
            side = self.side
        else:
            if not isinstance(side, str) or side not in ["L","C","R", ""]:
                raise ValueError("'side' must be on type string. Accepted values are ['L', "C', 'R'', '']")
            
            if side:
                side = side +  "_"

        description = description or self.description

        #if suffix is not None: Es lo mismo
        if not sufix:
            suffix = self._node_types.get(node_type, "UNK")

        name = side + description + token + "_" + suffix
        #para python 3:
        name = f"{side}{description}{token}_{suffix}"

        node = pm.createNode(node_type, name = name)

        return node

class AdvancedTwist(RigBaseModule):
    def __init__(self, side, module_name, debug, curve, start_trn, end_trn, aim axis, num_outputs=5): #le pone 5 outputs
        super().__init__(side, module_name, debug) #para python 3 
        super(AdvancedTwist, self).__init__(side, module_name, debug) #para python 2 

        self._valid_axis = "x y z X Y Z".split()

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
            'curve':curve,
            'start_trn': start_trn,     
            'end_trn': end_trn,
            'inputs_trn': self._nd.create(node_type='transform', token='Inputs')
            'outputs_trn' : self._nd.create(node_type='transform', token='Outputs')
            'output_transforms' : list(),
            'output_joints': list(),

        }


    def prepare(self)
        super(AdvancedTwist, self).prepare() #si queremos añadir mas cosas
        # we will need to delete the temp nodes that we create

    def create(self):
        """
        Put all the logic together to create the twisting tranforms
        """

        assert self.module_controls_group, '"prepare" the module or at least assign \
                                            a transform to "self.modules_rig_group"'
        #es una buena forma de comprobar si una variable esta vacia
        #el assert le pasas algo como argument, si el condicional es False, te printeara lo que hayas puesto despues de assert

    def _create_inputs_and_outputs(self):
        inputs = self._output_data.get('inputs_trn')
        pm.addAttr(inputs, ln="wordlUpObject", at="matrix")  #ln es long name
        pm.addAttr(inputs, ln="wordlUpObjectEnd", at="matrix")

        outputs = self._output_data.get('outputs_trn')
        pm.addAttr(outputs, ln="outputMatrix", at='matrix', multi=True)  #al poner el multi podemos ir añadiendo todos los atributos que queramos, tantos joints o trn como queramos

        self._input_data.get("start_trn").worldMatrix >> inputs.worldUpObject
        self._input_data.get("end_trn").worldMatrix >> inputs.worldUpObjectEnd

    def _attach_xforms_to_curve(self):
        percent_increment = 1.0 / self._input_data['num_outputs'] - 1)
        axis = self._input_data["aim_axis"].replace("-", "")
        axis_index = self._valid_index.index(axis)
        negative_axis = (self._valid_index.index(self._input_data['aim_axis']) > 2)  #hacemos una boleana, miramos si es negativo o no

        inputs = self._output_data.get('inputs_trn')
        outputs = self._output_data.get('outputs_trn')
        

        for i in range(self._input_data['num_outputs']):
                number = str(i).zfill(2)
                mpath_base = self._nd.create("motionPath", side=self.side, tokn='Orient_{]'.format)

                mpath_base.frontAxis.set(axis_index)
                mpath_base.inverseFront.set(negative_axis)
                mpath_base.upAxis.set(2)
                mpath_base.fractionMode.set(True) #esto es el parameter length del atributo de motion path
                mpath_base.uValue.set(percent_increment * i)

                self.-_input_data['curve'].worldSpace >> mpath_base.geometryPath

                comp_mtx_base = self._nd.create("composeMatrix", token="base_orientation_{}".format(number))
                mpath_base.allCoordinates >> comp_mtx_base.inputTranslate
                mpath_base.rx >> comp_mtx_base.inputRotateX
                mpath_base.ry >> comp_mtx_base.inputRotateY
                mpath_base.rz >> comp_mtx_base.inputRotateZ
                
                mult_mix_extractTwist = self._md.create("multMatrix", token="multMix_extractTwuist_{}".format(number))
                

    

#    def _create_twist_calculator(self):
#        percent_increment = 1.0 / self._input_data['num_outputs'] - 1)
#        axis = self._input_data["aim_axis"].replace("-", "")

#        inputs = self._output_data.get('inputs_trn')
#        outputs = self._output_data.get('outputs_trn')
        

#        inv_mtx_parent = self._nd.create("inverseMatrix", token="end_extractTwist")
 




