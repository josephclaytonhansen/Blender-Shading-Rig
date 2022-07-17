import math
import bpy
import json
from bpy.app.handlers import persistent

from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,)
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )

from bpy.utils import register_class

bl_info = {
    'name': 'Cel-Shaded Character Studio',
    'category': 'All',
    'author': 'Joseph Hansen',
    'version': (0, 1, 1),
    'blender': (3, 0, 0),
    'location': '',
    'description': 'Character shading studio for 2D, hand-drawn, anime, cartoon, and NPR styles'
}

def distance(p1, p2):
    #calculate 3D distance
    d = math.sqrt(
        (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2
        )
    return d

def convert_full_eframes_array_to_edit_seperated_array(edits, light_rot, eframes, all_edits):
    splits_array_empty_pos = {}
    splits_array_light_rot = {}
    used_potentials = []
    
    for x in range(0, len(all_edits)):

        working_saep = []
        working_salr = []

        for y in range(0, len(edits)):
            if all_edits[x] == edits[y]:
                working_saep.append(eframes[y])
                working_salr.append(light_rot[y])
                
                if g.debug:
                    print(working_saep)
                    print(working_salr)
                    
                if all_edits[x] not in used_potentials:
                    used_potentials.append(all_edits[x])
        
            if working_saep != []:
                splits_array_empty_pos[all_edits[x]] = working_saep
            if working_salr != []:
                splits_array_light_rot[all_edits[x]] = working_salr

    c = [splits_array_empty_pos, splits_array_light_rot, used_potentials]
    return c

class Globals():
    #experimental - store names in array so they can be changed 
    edit_names = ["EditA", "EditB", "EditC", "EditD", "EditE", "EditF", "EditG", "EditH"]

    edit_groups = ["Group.002", "Group.003", "Group.005", "Group.006", "Group.008", "Group.009", "Group.010", "Group.011"]
    
    edit_groups2 = ["EC_A", "EC_B", "EC_C", "EC_D", "EC_E", "EC_F", "EC_G", "EC_H"]
    edit_indices = [0,1,2,3,4,5,6,7]
    rotate_groups = ["Edit.013", "Edit.014","Edit.012", "Edit.011", "Edit.015","Edit.008", "Edit.009","Edit.010"]
    
    influence_groups = ["Group", "Group.001", "Group.002", "Group.003", "Group.004","Group.005", "Group.006", "Group.007"]
    
    debug = False
    
    jump = 0
    
    active_light = None
    
    #store global variables
    try:
        active_point = [
        #currently the light is hard-coded
            round(bpy.data.objects["Area"].rotation_euler[0],2),
            round(bpy.data.objects["Area"].rotation_euler[1],2),
            round(bpy.data.objects["Area"].rotation_euler[2],2)
            ]
    except:
        active_point = [0.0,0.0,0.0]
    try:
        #hardcoded light
        light_rot_array = json.loads(bpy.data.lights["Area"]["light_rot"])
        distances = [0] * len(light_rot_array)
        empty_pos_array = json.loads(bpy.data.lights["Area"]["empty_pos"])
        eframe_edit_names = eval(bpy.data.lights["Area"]["edit_names"])
        inverse_distances = [0] * len(light_rot_array)
        multiplied_distances = [0] * len(light_rot_array)
        print("Successfully loaded e-frame data")

    except Exception as e:
        light_rot_array = []
        empty_pos_array = []
        distances = []
        inverse_distances = []
        multiplied_distances = []
        eframe_edit_names = []
        print(e)
        
    total_inverse_distances = 0
    working_multiplier = 0
    final_pos = []
    placeable = True
    placeable_text = "Current: Placement"
    
    bound_lights = {}
    
    #for depsgraph filtering- if a light isn't bound, there's no point in trying to run the do_depsgraph_update (it doesn't work) 
    light_is_bound = False
    
    #adding the all_ dicts, for multi-object support
    all_edit_names = {}
    all_light_rot_arrays = {}
    all_empty_pos_arrays = {}
    all_eframe_edit_names = {}
    
    run_c = True
    c = None
        

g = Globals()
#instantiate global variables

def load_handler(dummy):
    if g.placeable:
        for edit in g.edit_names:
                bpy.data.objects[edit].hide_select = False

bpy.app.handlers.load_post.append(load_handler)

def filter_callback(self, object):
    if object.type == "EMPTY" and object.name in g.edit_names:
        return object.name in self.my_collection.objects.keys() 

def filter_mesh(self, object):
    return object.type == 'MESH'

def filter_light(self, object):
    return object.type == 'LIGHT'

def update_individual_parameters(ob):
    for i in g.edit_indices:
            if bpy.data.scenes["Scene"].empty_objects.name == g.edit_names[i]:
                bpy.data.scenes["Scene"].sharpness = bpy.data.node_groups["EDIT_SHADING_INNER"].nodes[g.edit_groups[i]].inputs[5].default_value
                bpy.data.scenes["Scene"].escale = bpy.data.node_groups[g.edit_groups2[i]].nodes["Value"].outputs[0].default_value
                bpy.data.scenes["Scene"].estretch = bpy.data.node_groups[g.edit_groups2[i]].nodes["Math.003"].inputs[1].default_value
                bpy.data.scenes["Scene"].erotate = bpy.data.node_groups[g.rotate_groups[i]].nodes["Mapping.001"].inputs[2].default_value[0] * 62.8
                bpy.data.scenes["Scene"].mask = bpy.data.node_groups[g.rotate_groups[i]].nodes["ColorRamp"].color_ramp.elements[1].position * 10
                bpy.data.scenes["Scene"].epinch = bpy.data.node_groups[g.rotate_groups[i]].nodes["Value"].outputs[0].default_value
                bpy.data.scenes["Scene"].einfluence = bpy.data.node_groups["Shading"].nodes[g.influence_groups[i]].inputs[2].default_value
                
def do_depsgraph_update(dummy):
    bpy.data.node_groups["EDIT_SHADING"].nodes["Group.011"].inputs[2].default_value = bpy.data.scenes["Scene"].scale
    bpy.data.node_groups["EDIT_SHADING"].nodes["Group.011"].inputs[3].default_value = bpy.data.scenes["Scene"].coords
    bpy.data.node_groups["EDIT_SHADING"].nodes["Group.011"].inputs[4].default_value = bpy.data.scenes["Scene"].threshold
    bpy.data.node_groups["Shading"].nodes["Mix"].inputs[0].default_value = bpy.data.scenes["Scene"].direction
    bpy.data.node_groups["Setup"].nodes["Value"].outputs[0].default_value = bpy.data.scenes["Scene"].edit_strength
    
    #set active light and check if light is bound
    
    if "bound_light" in bpy.data.scenes["Scene"].edit_object:
        if bpy.data.scenes["Scene"].edit_object["bound_light"] != None:
            g.light_is_bound = True
            g.active_light = bpy.data.objects[bpy.data.objects[bpy.data.scenes["Scene"].edit_object.name]["bound_light"]]
            g.active_light_name = bpy.data.objects[bpy.data.scenes["Scene"].edit_object.name]["bound_light"]
        else:
            g.light_is_bound = False
            g.active_light = None
            g.active_light_name = ""
    else:
        g.light_is_bound = False
        g.active_light = None
        g.active_light_name = ""
        
    #depsgraph filtering- this should run only when valid
    if g.light_is_bound:
    
        #If an edit is selected, the active edit should be that edit
        #This clears with a BUG
        
        #BUG: If the field is empty, selection doesn't work 
        
        selected = "EMPTY" in [obj.type for obj in bpy.context.selected_objects]
        if bpy.context.active_object.type == "EMPTY" and g.placeable and bpy.data.scenes["Scene"].auto_select and selected:
            if bpy.data.scenes["Scene"].empty_objects != bpy.context.active_object:
                update_individual_parameters(bpy.data.scenes["Scene"].empty_objects)
            bpy.data.scenes["Scene"].empty_objects = bpy.context.active_object
        
        collection = bpy.data.scenes["Scene"].my_collection
        #when the depsgraph updates, get the active light_rotation 
        #represented as a "point" for ease of distance calculations.

        g.active_point = [
            round(g.active_light.rotation_euler[0],2),
            round(g.active_light.rotation_euler[1],2),
            round(g.active_light.rotation_euler[2],2)
            ]  

        #Preview
        
        i = -1
        
        #experimental- get WDMs
        if g.run_c:
            g.c = convert_full_eframes_array_to_edit_seperated_array(g.eframe_edit_names, g.light_rot_array, g.empty_pos_array, g.edit_names)
            g.run_c = False
        
        all_light_rot = g.c[1]
        all_empty_pos = g.c[0]
        edit_list = g.c[2]
        
        for edit in edit_list:
        
            l = len(all_light_rot[edit])
            distances = [0] * l
            inverse_distances = [0] * l
            multiplied_distances = [0] * l
            
            i = -1
            
            for point in all_light_rot[edit]:
                i += 1

                distances[i] = distance(g.active_point, point)
                inverse_distances[i] = round((1/distances[i]),6)
            
            y = -1
            for point in all_light_rot[edit]:
                y += 1
                total_inverse_distances = sum(inverse_distances)
                working_multiplier = 100 / total_inverse_distances
                
                multiplied_distances[y] = inverse_distances[y] * working_multiplier
                
                if g.debug:
                    print("\n", edit)
                    print(multiplied_distances)
                
            #WDM (everything above this) clears
            
            #LERP
            final_pos = [0,0,0]

            entry_index = -1

            for entry in all_empty_pos[edit]:
                entry_index += 1
                axis_index = -1

                for axis in entry:
                    axis_index += 1
                    final_pos[axis_index] += round((round((multiplied_distances[entry_index] /100),2) * axis),6)
                    
            g.final_pos = final_pos

            if g.debug:
                print("Placeable: ", g.placeable, "\nFinal pos: ", g.final_pos)
            
            if not g.placeable and g.final_pos != [0,0,0]:
                bpy.data.objects[edit].location = g.final_pos
            elif g.placeable and g.final_pos != [0,0,0]:
                if bpy.data.scenes["Scene"].empty_objects.name != edit:
                    bpy.data.objects[edit].location = g.final_pos
            #end LERP
            #LERP clears
        

bpy.app.handlers.depsgraph_update_post.append(do_depsgraph_update)   
bpy.app.handlers.frame_change_post.append(do_depsgraph_update)

class BindLight(Operator):
    """Bind a light to an object- this light will affect edits for this object only"""
    bl_idname = "wm.bind_light"
    bl_label = "Bind light"
    
    def execute(self,context):
        if bpy.data.scenes["Scene"].edit_object != None:
            if bpy.data.scenes["Scene"].bound_light != None:
                bpy.data.objects[bpy.data.scenes["Scene"].edit_object.name]["bound_light"] = str("" + bpy.data.scenes["Scene"].bound_light.name + "")
                bpy.data.objects[bpy.data.scenes["Scene"].edit_object.name].data.update()
            else:
                self.report({'WARNING'}, "No light set")
        else:
            self.report({'WARNING'}, "No object set")
        return{'FINISHED'}

class UnBindLight(Operator):
    """Un-bind a light from this object- e-frames for this object will be deleted"""
    bl_idname = "wm.un_bind_light"
    bl_label = "Un-bind light"
    
    def execute(self, context):
        bpy.data.objects["Roundcube"]["bound_light"] = None
        bpy.data.objects[bpy.data.scenes["Scene"].edit_object.name].data.update()
        return {'FINISHED'}

class AddEFrame(Operator):
    """Add e-frame, a relationship between light angle and edit position"""
    bl_idname = "wm.add_eframe"
    bl_label = "Add e-frame"

    def execute(self, context):
        
        #experimental
        g.eframe_edit_names.append(bpy.data.scenes["Scene"].empty_objects.name)
        
        g.light_rot_array.append([

        round(bpy.data.objects[g.active_light_name].rotation_euler[0],6),
        round(bpy.data.objects[g.active_light_name].rotation_euler[1],6),
        round(bpy.data.objects[g.active_light_name].rotation_euler[2],6)
        ])
        
        if g.debug:
        
            print(bpy.data.scenes["Scene"].empty_objects.name)
            print(bpy.data.objects[bpy.data.scenes["Scene"].empty_objects.name])
            print(bpy.data.objects[bpy.data.scenes["Scene"].empty_objects.name].location)
        
        g.empty_pos_array.append([
        round(bpy.data.objects[bpy.data.scenes["Scene"].empty_objects.name].location[0],4),
        round(bpy.data.objects[bpy.data.scenes["Scene"].empty_objects.name].location[1],4),
        round(bpy.data.objects[bpy.data.scenes["Scene"].empty_objects.name].location[2],4)
        ])
        #by adding to the end of both arrays, we know that 
        #corresponding rotation and position values will share
        #an index between arrays
        g.distances.append(0)
        g.inverse_distances.append(0)
        g.multiplied_distances.append(0)
        #the distances array also needs a new entry. Since the
        #distances are dynamically calculated, we can leave
        #this blank for now. 
        #Same for the inverses
        
        #save e-frames to e-frame light

        bpy.data.objects[g.active_light_name]["light_rot"] = str(json.loads(str(g.light_rot_array)))
        bpy.data.objects[g.active_light_name]["empty_pos"] = str(json.loads(str(g.empty_pos_array)))
        bpy.data.objects[g.active_light_name]["edit_names"] = str(g.eframe_edit_names)
        bpy.context.view_layer.depsgraph.update()
        
        g.all_edit_names[bpy.data.scenes["Scene"].edit_object.name] = g.edit_names
        g.all_light_rot_arrays[bpy.data.scenes["Scene"].edit_object.name] = g.light_rot_array
        g.all_empty_pos_arrays[bpy.data.scenes["Scene"].edit_object.name] = g.empty_pos_array
        g.all_eframe_edit_names[bpy.data.scenes["Scene"].edit_object.name] = g.eframe_edit_names
        
        #we're storing the all_ dicts locally- they're not saved in custom properties, and we're not doing anything with them (yet)
        print(g.all_edit_names, g.all_light_rot_arrays, g.all_empty_pos_arrays, g.all_eframe_edit_names)
        
        g.run_c = True
        
        return {'FINISHED'}

class SetSmoothness(Operator):
    bl_idname = "wm.set_edit_smoothness"
    bl_label = "Set"
    def execute(self,context):
        
        for i in g.edit_indices:
            if bpy.data.scenes["Scene"].empty_objects.name == g.edit_names[i]:
                bpy.data.node_groups["EDIT_SHADING_INNER"].nodes[g.edit_groups[i]].inputs[5].default_value = bpy.data.scenes["Scene"].sharpness
        
        return {'FINISHED'}

class SetScale(Operator):
    bl_idname = "wm.set_edit_scale"
    bl_label = "Set"
    def execute(self,context):
        
        for i in g.edit_indices:
            if bpy.data.scenes["Scene"].empty_objects.name == g.edit_names[i]:
                bpy.data.node_groups[g.edit_groups2[i]].nodes["Value"].outputs[0].default_value = bpy.data.scenes["Scene"].escale
        
        return {'FINISHED'}
    

class SetStretch(Operator):
    bl_idname = "wm.set_edit_stretch"
    bl_label = "Set"
    def execute(self,context):
        
        for i in g.edit_indices:
            if bpy.data.scenes["Scene"].empty_objects.name == g.edit_names[i]:
                bpy.data.node_groups[g.edit_groups2[i]].nodes["Math.003"].inputs[1].default_value = bpy.data.scenes["Scene"].estretch
        
        return {'FINISHED'}
    

class SetRotate(Operator):
    bl_idname = "wm.set_edit_rotate"
    bl_label = "Set"
    def execute(self,context):
        
        for i in g.edit_indices:
            if bpy.data.scenes["Scene"].empty_objects.name == g.edit_names[i]:
                bpy.data.node_groups[g.rotate_groups[i]].nodes["Mapping.001"].inputs[2].default_value[0]= bpy.data.scenes["Scene"].erotate / 62.8
        
        return {'FINISHED'}

class SetMask(Operator):
    bl_idname = "wm.set_edit_mask"
    bl_label = "Set"
    def execute(self,context):
        
        for i in g.edit_indices:
            if bpy.data.scenes["Scene"].empty_objects.name == g.edit_names[i]:
                bpy.data.node_groups[g.rotate_groups[i]].nodes["ColorRamp"].color_ramp.elements[1].position = bpy.data.scenes["Scene"].mask / 10
        
        return {'FINISHED'}

class SetPinch(Operator):
    bl_idname = "wm.set_edit_pinch"
    bl_label = "Set"
    def execute(self,context):
        
        for i in g.edit_indices:
            if bpy.data.scenes["Scene"].empty_objects.name == g.edit_names[i]:
                bpy.data.node_groups[g.rotate_groups[i]].nodes["Value"].outputs[0].default_value = bpy.data.scenes["Scene"].epinch
        
        return {'FINISHED'}
    
class SetInfluence(Operator):
    bl_idname = "wm.set_edit_influence"
    bl_label = "Set"
    def execute(self,context):
        
        for i in g.edit_indices:
            if bpy.data.scenes["Scene"].empty_objects.name == g.edit_names[i]:
                bpy.data.node_groups["Shading"].nodes[g.influence_groups[i]].inputs[2].default_value = bpy.data.scenes["Scene"].einfluence
        
        return {'FINISHED'}


class SetName(Operator):
    bl_idname = "wm.set_edit_name"
    bl_label = "Rename"
    def execute(self,context):
        working_index = g.edit_names.index(bpy.data.scenes["Scene"].empty_objects.name)
        if bpy.data.scenes["Scene"].ename not in g.edit_names:
            g.edit_names[working_index] = bpy.data.scenes["Scene"].ename
            bpy.data.scenes["Scene"].empty_objects.name = bpy.data.scenes["Scene"].ename
            if g.debug:
                print(g.edit_names)
        else:
            if g.debug:
                print()
            self.report({'ERROR'}, "Edit name already in use")
        
        return {'FINISHED'}

class ClearEFrame(Operator):
    """Clear all relationships between light angle and empty position"""
    bl_idname = "wm.no_eframe"
    bl_label = "Clear all"
    def execute(self, context):
        count = len(g.light_rot_array)
        g.light_rot_array = []
        g.empty_pos_array = []
        g.eframe_edit_names = []
        bpy.data.objects["Area"]["light_rot"] = str(json.loads(str(g.light_rot_array)))
        bpy.data.objects["Area"]["empty_pos"] = str(json.loads(str(g.empty_pos_array)))
        bpy.data.objects["Area"]["edit_names"] = str(g.eframe_edit_names)
        bpy.context.view_layer.depsgraph.update()
        self.report({'INFO'}, str(count) + " E-Frames cleared")
        g.run_c = True
        return {'FINISHED'}

class ClearIndivEFrame(Operator):
    """Clear e-frames from the active edit"""
    bl_idname = "wm.del_eframe"
    bl_label = "Clear active"
    def execute(self, context):
        if g.debug:
            print(g.eframe_edit_names)
        dels = []
        i = -1
        for entry in g.eframe_edit_names:
            i += 1
            if entry == bpy.data.scenes["Scene"].empty_objects.name:
                #remove these entries and corresponding ones from light_rot and empty_pos
                dels.append(i)
        
        dels = set(dels)
        if g.debug:
            print(dels)
        
        r_edit_names = [ value for (j, value) in enumerate(g.eframe_edit_names) if j not in set(dels) ]
        r_empty_pos = [ value for (k, value) in enumerate(g.empty_pos_array) if k not in set(dels) ]
        r_light_rot = [ value for (l, value) in enumerate(g.light_rot_array) if l not in set(dels) ]
        
        g.eframe_edit_names = r_edit_names
        g.empty_pos_array = r_empty_pos
        g.light_rot_array = r_light_rot
        
        bpy.data.objects["Area"]["light_rot"] = str(json.loads(str(g.light_rot_array)))
        bpy.data.objects["Area"]["empty_pos"] = str(json.loads(str(g.empty_pos_array)))
        bpy.data.objects["Area"]["edit_names"] = str(g.eframe_edit_names)
        bpy.context.view_layer.depsgraph.update()
        
        self.report({'INFO'}, "E-frames cleared from " + str(bpy.data.scenes["Scene"].empty_objects.name))
        g.run_c = True
        return {'FINISHED'}

class TogglePreview(Operator):
    """Toggle between realtime preview and placement"""
    bl_idname = "wm.toggle"
    bl_label = "Toggle Preview"
    def execute(self, context):
        g.placeable = not g.placeable
        if g.placeable:
            g.placeable_text = "Current: Placement"
            for edit in g.edit_names:
                bpy.data.objects[edit].hide_select = False
        else:
            g.placeable_text = "Current: Preview All"
            for edit in g.edit_names:
                bpy.data.objects[edit].hide_select = True
        return {'FINISHED'}
    
class OBJECT_PT_EFramePanel(Panel):
    bl_label = "E-Frames Management"
    bl_idname = "OBJECT_PT_eframe_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "CSC Studio"
    bl_context = "objectmode"   


    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        

        icons = ["HOOK", "TRASH", "UV_SYNC_SELECT", "META_ELLIPSOID", "SHADING_BBOX", "IMAGE_ALPHA", "FORCE_CHARGE", "UV", "DECORATE_KEYFRAME",
        "SHARPCURVE","SHADING_BBOX","FORCE_CHARGE", "DRIVER_ROTATIONAL_DIFFERENCE", "FIXED_SIZE", "HOLDOUT_ON", "SYNTAX_OFF", "LINKED", "UNLINKED"]
        
        layout = self.layout
        scene = context.scene
        subcolumn = layout.column()
        subrow = layout.row(align=True)
        subrow.operator("wm.add_eframe")
        subrow = layout.row(align=True)
        subrow.operator("wm.toggle", icon = icons[2], depress = not g.placeable, text = g.placeable_text)
        
        layout.separator()

        subrow = layout.row(align=True)
        
        if "bound_light" in bpy.data.scenes["Scene"].edit_object:
            if bpy.data.scenes["Scene"].edit_object["bound_light"] != None:
                subrow.operator("wm.un_bind_light", icon = icons[16])
                subrow.prop(scene, "edit_object")
            else:
                subrow.operator("wm.bind_light", icon = icons[16])
                subrow.prop(scene, "bound_light", icon = "LIGHT")
                subrow = layout.row(align=True)
                subrow.label(text="Object")
                subrow.prop(scene, "edit_object")
        else:
            subrow.operator("wm.bind_light", icon = icons[16])
            subrow.prop(scene, "bound_light", icon = "LIGHT")
            subrow = layout.row(align=True)
            subrow.label(text="Object")
            subrow.prop(scene, "edit_object")
        
        layout.separator()
        
        subrow = layout.row(align=True)
        subrow.label(text="Edits collection")
        subrow.prop(scene, "my_collection")
        
        if scene.my_collection:
            subrow = layout.row(align=True)
            subrow.label(text="Active edit")
            subrow.prop(scene, "empty_objects", icon = "EMPTY_DATA")
            
        subrow = layout.row(align=True)
        subrow.prop(scene, "auto_select")
        
        layout.separator()
        
        subrow = layout.row(align=True)
        subrow.label(icon=icons[1])
        subrow.operator("wm.del_eframe")    
        subrow.operator("wm.no_eframe")
        
        
class OBJECT_PT_EFrameParamPanel(Panel):
    bl_label = "E-Frames Parameters"
    bl_idname = "OBJECT_PT_eframe_param_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "CSC Studio"
    bl_context = "objectmode"   


    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        icons = ["HOOK", "TRASH", "UV_SYNC_SELECT", "META_ELLIPSOID", "SHADING_BBOX", "IMAGE_ALPHA", "FORCE_CHARGE", "UV", "DECORATE_KEYFRAME",
        "SHARPCURVE","SHADING_BBOX","FORCE_CHARGE", "DRIVER_ROTATIONAL_DIFFERENCE", "FIXED_SIZE", "HOLDOUT_ON", "SYNTAX_OFF"]
        
        layout = self.layout
        scene = context.scene
        
        subrow = layout.row(align=True)
        subrow.prop(scene, "show_up")
        subrow = layout.row(align=True)
        subrow.prop(scene, "advanced")
        
        if bpy.data.scenes["Scene"].show_up:
            subrow = layout.row(align=True)
            subrow.label(icon = icons[3])
            subrow.prop(scene, "edit_strength")
            
            subrow = layout.row(align=True)
            subrow.label(icon=icons[4])
            subrow.prop(scene, "scale")
            

            subrow = layout.row(align=True)
            subrow.label(icon=icons[5])
            subrow.prop(scene, "threshold")
            
            if bpy.data.scenes["Scene"].advanced:
                
                subrow = layout.row(align=True)
                subrow.label(icon = icons[6], text = "Direction")
                subrow.prop(scene, "direction")
            
                subrow = layout.row(align=True)
                subrow.label(icon = icons[7], text = "Coordinates")
                subrow.prop(scene, "coords")
            
        if bpy.data.scenes["Scene"].empty_objects != None:
            col = layout.column()
            subrow = layout.row(align=True)
            subrow.label(text = "Individual controls")
            
            if bpy.data.scenes["Scene"].advanced:
                subrow = layout.row(align=True)
                subrow.label(icon = icons[8])
                subrow.prop(scene, "sharpness")
                subrow.operator("wm.set_edit_smoothness")
            
            subrow = layout.row(align=True)
            subrow.label(icon = icons[9])
            subrow.prop(scene, "epinch")
            subrow.operator("wm.set_edit_pinch")
            
            subrow = layout.row(align=True)
            subrow.label(icon = icons[10])
            subrow.prop(scene, "escale")
            subrow.operator("wm.set_edit_scale")
            
            subrow = layout.row(align=True)
            subrow.label(icon=icons[11])
            subrow.prop(scene, "einfluence")
            subrow.operator("wm.set_edit_influence")
            
            if bpy.data.scenes["Scene"].advanced:
                
                subrow = layout.row(align=True)
                subrow.label(icon = icons[12])
                subrow.prop(scene, "erotate")
                subrow.operator("wm.set_edit_rotate")
                
            subrow = layout.row(align=True)
            subrow.label(icon = icons[13])
            subrow.prop(scene, "estretch")
            subrow.operator("wm.set_edit_stretch")
            
            if bpy.data.scenes["Scene"].advanced:
            
                subrow = layout.row(align=True)
                subrow.label(icon=icons[14])
                subrow.prop(scene, "mask")
                subrow.operator("wm.set_edit_mask")
            
                subrow = layout.row(align=True)
                subrow.label(icon = icons[15])
                subrow.prop(scene, "ename")
                subrow.operator("wm.set_edit_name")
        

def register():
    register_class(OBJECT_PT_EFramePanel)
    register_class(OBJECT_PT_EFrameParamPanel)
    register_class(BindLight)
    register_class(UnBindLight)
    register_class(AddEFrame)
    register_class(ClearEFrame)
    register_class(ClearIndivEFrame)
    register_class(TogglePreview)
    register_class(SetSmoothness)
    register_class(SetScale)
    register_class(SetName)
    register_class(SetStretch)
    register_class(SetRotate)
    register_class(SetMask)
    register_class(SetPinch)
    register_class(SetInfluence)

    
    bpy.types.Scene.my_collection = PointerProperty(
        name="",
        type=bpy.types.Collection)
    bpy.types.Scene.empty_objects = PointerProperty(
        name="",
        type=bpy.types.Object,
        poll=filter_callback)
        
    bpy.types.Scene.edit_object = PointerProperty(
        name="",
        type=bpy.types.Object,
        poll=filter_mesh)
        
    bpy.types.Scene.bound_light = PointerProperty(
        name="",
        type=bpy.types.Object,
        poll=filter_light)
        
    bpy.types.Scene.edit_strength = FloatProperty(name = "Edits Strength", max = 99, min = -99, default = 50)
    
    bpy.types.Scene.auto_select = BoolProperty(name = "Selected edit to active", default = True)
    
    bpy.types.Scene.show_up = BoolProperty(name = "Show universal parameters", default = True)
    bpy.types.Scene.advanced = BoolProperty(name = "Show advanced parameters", default = True)

    bpy.types.Scene.sharpness = FloatProperty(name = "Smooth", max = 1, min = 0, default = 1)
    
    bpy.types.Scene.direction = IntProperty(name = "Light | Shadow", max = 1, min = 0, default = 0)
    bpy.types.Scene.coords = IntProperty(name = "Object | UV ", max = 1, min = 0, default = 0)
    bpy.types.Scene.scale = FloatProperty(name = "Edits Scale", max = 10, min = 0, default = 0)
    bpy.types.Scene.threshold = FloatProperty(name = "Threshold", max = 10, min = 0, default = 0.1)
    bpy.types.Scene.mask = FloatProperty(name = "Mask", max = 10, min = 1, default = 7.5)
    bpy.types.Scene.escale = FloatProperty(name = "Scale", max = 10, min = .01, default = 1)
    bpy.types.Scene.estretch = FloatProperty(name = "Stretch", max = 10, min = .01, default = 1)
    bpy.types.Scene.erotate = IntProperty(name = "Rotate", max = 180, min = -180, default = 0)
    bpy.types.Scene.epinch = FloatProperty(name = "Pinch", max = 1, min = 0.1, default = 1)
    bpy.types.Scene.einfluence = FloatProperty(name = "Direction", max = 1, min = 0, default = 1)
    bpy.types.Scene.ename = StringProperty(name = "")

def unregister():
    from bpy.utils import unregister_class
    unregister_class(OBJECT_PT_EFramePanel)
    unregister_class(OBJECT_PT_EFrameParamPanel)
    unregister_class(BindLight)
    unregister_class(UnBindLight)
    unregister_class(AddEFrame)
    unregister_class(ClearEFrame)
    unregister_class(ClearIndivEFrame)
    unregister_class(TogglePreview)
    unregister_class(SetSmoothness)
    unregister_class(SetScale)
    unregister_class(SetName)
    unregister_class(SetStretch)
    unregister_class(SetRotate)
    unregister_class(SetMask)
    unregister_class(SetPinch)
    unregister_class(SetInfluence)
    unregister_class(eframesPreferences)
    
    del bpy.types.Scene.my_collection
    del bpy.types.Collection.empty_objects
    del bpy.types.Scene.edit_object
    del bpy.types.Scene.bound_light
    del bpy.types.Scene.edit_strength
    del bpy.types.Scene.auto_select
    del bpy.types.Scene.show_up
    del bpy.types.Scene.sharpness
    del bpy.types.Scene.mask
    del bpy.types.Scene.escale
    del bpy.types.Scene.ename
    del bpy.types.Scene.estretch
    del bpy.types.Scene.erotate
    del bpy.types.Scene.epinch
    del bpy.types.Scene.advanced
    del bpy.types.Scene.edirection

    if do_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(do_depsgraph_update)
        
    if do_depsgraph_update in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(do_depsgraph_update)
        
if __name__ == "__main__":
    register()