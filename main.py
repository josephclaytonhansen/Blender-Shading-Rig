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
    
    controller_index = 0
    
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
    
    ready_for_eframes = False
    #Eventually this will be True when the object is set, the edits are spawned, the nodes are set up, and the light is assigned.
    #Right now, it's just when the light is assigned. 
    ready_for_light_bind = False
    show_spawn_edits_button = False
    objects_with_edits = []
    mesh_selected = False
    
    light_bindings = {}

g = Globals()
#instantiate global variables

#edit management status determination
def determine_edit_state():
    selected = "MESH" in [obj.type for obj in bpy.context.selected_objects]
    if not selected:
        print("No mesh selected")
        g.mesh_selected = False
    else:
        g.mesh_selected = True
        selected_mesh = bpy.context.selected_objects[0]
        #first check- is selected mesh ready for edits?
        if selected_mesh.name in g.objects_with_edits:
            #now we check if selected mesh has a bound light
            if selected_mesh.name in g.light_bindings:
                #if both of these true, everything is good to go
                g.ready_for_eframes = True
                g.ready_for_light_bind = False
                g.show_spawn_edits_button = False
            else:
                #light has not been bound
                g.ready_for_eframes = False
                g.ready_for_light_bind = True
                g.show_spawn_edits_button = False
        else:
            #in this case, we need to Add Edits to object
            g.objects_with_edits.append(selected_mesh.name)
            g.show_add_edits_button = True
            g.ready_for_eframes = False
            g.ready_for_light_bind = False
        
        print("Ready for e-frames? ", g.ready_for_eframes, "Ready for light bind? ", g.ready_for_light_bind, "Ready for edits? ", g.show_spawn_edits_button)


#create light object
def add_light_edit_controller():
    g.light_bindings[bpy.context.selected_objects[0].name] = "bound"
    print(g.light_bindings)
    dg = bpy.context.evaluated_depsgraph_get() 
    dg.update()
    
    if g._ready_for_light_bind:
        g.controller_index+=1
        #currently light names are incremental- this is not a good idea, eventually the name should incorporate the edit target object
        light_data = bpy.data.lights.new(name="Light_EditController"+str(g.controller_index), type='AREA')
        light_data.energy = 200

        light_object = bpy.data.objects.new(name="Light_EditController"+str(g.controller_index), object_data=light_data)

        bpy.context.collection.objects.link(light_object)

        add_storage_properties_to_light(light_object, bpy.context.selected_objects[0])

        dg = bpy.context.evaluated_depsgraph_get() 
        dg.update()

#prep light for storage
def add_storage_properties_to_light(light, obj):
    light["edit_names"] = "[]"
    light["empty_pos"] = "[]"
    light["light_rot"] = "[]"
    light["binding"] = str(obj.name)

#on load- fix the selection bug
def load_handler(dummy):
    if g.placeable:
        for edit in g.edit_names:
                bpy.data.objects[edit].hide_select = False

bpy.app.handlers.load_post.append(load_handler)

#this is for the collection field
def filter_callback(self, object):
    if object.type == "EMPTY" and object.name in g.edit_names:
        return object.name in self.my_collection.objects.keys() 

#this is a getter function for the individual parameters
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
    
    #experimental- determine edit status
    determine_edit_state()
    
    bpy.data.node_groups["EDIT_SHADING"].nodes["Group.011"].inputs[2].default_value = bpy.data.scenes["Scene"].scale
    bpy.data.node_groups["EDIT_SHADING"].nodes["Group.011"].inputs[3].default_value = bpy.data.scenes["Scene"].coords
    bpy.data.node_groups["EDIT_SHADING"].nodes["Group.011"].inputs[4].default_value = bpy.data.scenes["Scene"].threshold
    bpy.data.node_groups["Shading"].nodes["Mix"].inputs[0].default_value = bpy.data.scenes["Scene"].direction
    bpy.data.node_groups["Setup"].nodes["Value"].outputs[0].default_value = bpy.data.scenes["Scene"].edit_strength
    
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
    #For now, the light is hard-coded
    g.active_point = [
        round(bpy.data.objects["Area"].rotation_euler[0],2),
        round(bpy.data.objects["Area"].rotation_euler[1],2),
        round(bpy.data.objects["Area"].rotation_euler[2],2)
        ]  

    #Preview
    
    i = -1
    
    #experimental- get WDMs
    c = convert_full_eframes_array_to_edit_seperated_array(g.eframe_edit_names, g.light_rot_array, g.empty_pos_array, g.edit_names)
    
    all_light_rot = c[1]
    all_empty_pos = c[0]
    edit_list = c[2]
    
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


class AddLightController(Operator):
    bl_idname = "wm.add_key_light_controller"
    bl_label = "Add key light for edits" 
    
    def execute(self, context):
        add_light_edit_controller()
        return {'FINISHED'}

class AddEFrame(Operator):
    """Add e-frame, a relationship between light angle and edit position"""
    bl_idname = "wm.add_eframe"
    bl_label = "Add e-frame"

    def execute(self, context):
        
        #experimental
        g.eframe_edit_names.append(bpy.data.scenes["Scene"].empty_objects.name)
        
        g.light_rot_array.append([
        #currently the light is hard-coded
        round(bpy.data.objects["Area"].rotation_euler[0],6),
        round(bpy.data.objects["Area"].rotation_euler[1],6),
        round(bpy.data.objects["Area"].rotation_euler[2],6)
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
        #hardcoded light
        bpy.data.lights["Area"]["light_rot"] = str(json.loads(str(g.light_rot_array)))
        bpy.data.lights["Area"]["empty_pos"] = str(json.loads(str(g.empty_pos_array)))
 
        bpy.data.lights["Area"]["edit_names"] = str(g.eframe_edit_names)
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
    bl_label = "Clear all e-frames"
    def execute(self, context):
        count = len(g.light_rot_array)
        g.light_rot_array = []
        g.empty_pos_array = []
        g.g.eframe_edit_names = []
        
        self.report({'INFO'}, str(count) + " E-Frames cleared")
        return {'FINISHED'}

class ClearIndivEFrame(Operator):
    """Clear e-frames from the active edit"""
    bl_idname = "wm.del_eframe"
    bl_label = "Clear e-frames from this edit"
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
        
        self.report({'INFO'}, "E-frames cleared from " + str(bpy.data.scenes["Scene"].empty_objects.name))
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
        "SHARPCURVE","SHADING_BBOX","FORCE_CHARGE", "DRIVER_ROTATIONAL_DIFFERENCE", "FIXED_SIZE", "HOLDOUT_ON", "SYNTAX_OFF"]
        
        layout = self.layout
        scene = context.scene
        
        if g.ready_for_eframes:
            subcolumn = layout.column()
            subrow = layout.row(align=True)
            subrow.operator("wm.add_eframe")
            subrow = layout.row(align=True)
            subrow.operator("wm.toggle", icon = icons[2], depress = not g.placeable, text = g.placeable_text)
            
            layout.separator()
            
            col = layout.column()
            subrow = layout.row(align=True)
            subrow.label(text="Edits collection")
            subrow.prop(scene, "my_collection")
            
            col.enabled = True if scene.my_collection else False
            subrow = layout.row(align=True)
            subrow.label(text="Active edit")
            subrow.prop(scene, "empty_objects")
            
            subrow = layout.row(align=True)
            subrow.prop(scene, "auto_select")
            
            layout.separator()
            
            subrow = layout.row(align=True)
            subrow.operator("wm.del_eframe", icon = icons[1])
            
            subrow = layout.row(align=True)
            subrow.operator("wm.no_eframe", icon = icons[1])
        
        else:
            subrow = layout.row(align=True)
            subrow.operator("wm.add_key_light_controller")
        
        
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
        
        if g.ready_for_eframes:
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
    register_class(AddLightController)

    
    bpy.types.Scene.my_collection = PointerProperty(
        name="",
        type=bpy.types.Collection)
    bpy.types.Scene.empty_objects = PointerProperty(
        name="",
        type=bpy.types.Object,
        poll=filter_callback)
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
    unregister_class(AddLightController)
    
    del bpy.types.Scene.my_collection
    del bpy.types.Collection.empty_objects
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