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

def distance(p1, p2):
    #calculate 3D distance
    d = math.sqrt(
        (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2
        )
    return d

def filter_callback(self, object):
    if object.type == "EMPTY":
        return object.name in self.my_collection.objects.keys() 

class Globals():
    #store global variables
    active_point = [
        round(bpy.data.objects["Area"].rotation_euler[0],2),
        round(bpy.data.objects["Area"].rotation_euler[1],2),
        round(bpy.data.objects["Area"].rotation_euler[2],2)
        ]
    try:
        light_rot_array = json.loads(bpy.data.objects["test"]["light_rot"])
        distances = [0] * len(light_rot_array)
        empty_pos_array = json.loads(bpy.data.objects["test"]["empty_pos"])
        inverse_distances = [0] * len(light_rot_array)
        multiplied_distances = [0] * len(light_rot_array)
    except:
        light_rot_array = []
        empty_pos_array = []
        distances = []
        inverse_distances = []
        multiplied_distances = []
    total_inverse_distances = 0
    working_multiplier = 0
    final_pos = []
    placeable = False
    placeable_text = "Current: Realtime Preview"

g = Globals()
#instantiate global variables

def do_depsgraph_update(dummy):
    collection = bpy.data.scenes["Scene"].my_collection
    #when the depsgraph updates, get the active light_rotation 
    #represented as a "point" for ease of distance calculations.
    #For now, the light is hard-coded
    g.active_point = [
        round(bpy.data.objects["Area"].rotation_euler[0],2),
        round(bpy.data.objects["Area"].rotation_euler[1],2),
        round(bpy.data.objects["Area"].rotation_euler[2],2)
        ]  

    
    #cycle through the light_rotation array to see if the current
    #rotation matches any entry 
    i = -1
    for entry in g.light_rot_array:
        print(entry)
        i +=1
        #get distances from active point to other points:
        g.distances[i] = round(distance(g.active_point, entry),6)
        #invert distances:
        try:
            g.inverse_distances[i] = round((1/distance(g.active_point, entry)),6)
        except:
            g.inverse_distances[i] = 0
        
        #calculate sum of total inverse distances:
        g.total_inverse_distances = sum(g.inverse_distances)
        #divide 100 by that, and multiply each distance by the result:
        g.working_multiplier = 100 / g.total_inverse_distances
        g.multiplied_distances[i] = g.inverse_distances[i] * g.working_multiplier
    
    
    #LERP testing
    final_pos = [0,0,0]

    entry_index = -1

    for entry in g.empty_pos_array:
        entry_index += 1
        axis_index = -1

        for axis in entry:
            axis_index += 1
            final_pos[axis_index] += round((round((g.multiplied_distances[entry_index] /100),2) * axis),6)
    g.final_pos = final_pos
    print(g.placeable, g.final_pos)
    if not g.placeable:
        bpy.data.objects["test"].location = g.final_pos
    #end LERP
    
    #save globals to a custom property
    bpy.data.objects["test"]["light_rot"] = str(json.loads(str(g.light_rot_array)))
    bpy.data.objects["test"]["empty_pos"] = str(json.loads(str(g.empty_pos_array)))

bpy.app.handlers.depsgraph_update_post.append(do_depsgraph_update)   
bpy.app.handlers.frame_change_post.append(do_depsgraph_update)

class AddEFrame(Operator):
    """Add relationship between light angle and empty position"""
    bl_idname = "wm.add_eframe"
    bl_label = "Add EFrame"

    def execute(self, context):
        g.light_rot_array.append([
        round(bpy.data.objects["Area"].rotation_euler[0],4),
        round(bpy.data.objects["Area"].rotation_euler[1],4),
        round(bpy.data.objects["Area"].rotation_euler[2],4)
        ])
        g.empty_pos_array.append([
        round(bpy.data.objects["test"].location[0],4),
        round(bpy.data.objects["test"].location[1],4),
        round(bpy.data.objects["test"].location[2],4)
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
        return {'FINISHED'}

class ClearEFrame(Operator):
    """Clear all relationships between light angle and empty position"""
    bl_idname = "wm.no_eframe"
    bl_label = "Clear EFrames"
    def execute(self, context):
        g.light_rot_array = []
        g.empty_pos_array = []
        g.distances = []
        g.inverse_distances = []
        g.multiplied_distances = []
        return {'FINISHED'}

class RemoveLast(Operator):
    """Clear all relationships between light angle and empty position"""
    bl_idname = "wm.no_eframe"
    bl_label = "Clear EFrames"
    def execute(self, context):
        g.light_rot_array = []
        g.empty_pos_array = []
        g.distances = []
        g.inverse_distances = []
        g.multiplied_distances = []
        return {'FINISHED'} 

class TogglePreview(Operator):
    """Toggle empty between realtime preview and placement"""
    bl_idname = "wm.toggle"
    bl_label = "Toggle Preview"
    def execute(self, context):
        g.placeable = not g.placeable
        if g.placeable:
            g.placeable_text = "Current: Placement"
        else:
            g.placeable_text = "Current: Realtime Preview"
        return {'FINISHED'}

class ClearLast(Operator):
    """Remove most recent eframe"""
    bl_idname = "wm.clear_recent"
    bl_label = "Delete Last"
    def execute(self, context):
        g.light_rot_array.pop()
        g.empty_pos_array.pop()
        g.distances.pop()
        g.inverse_distances.pop()
        g.multiplied_distances.pop()
        
        return {'FINISHED'}
    
class OBJECT_PT_EFramePanel(Panel):
    bl_label = "EFrames"
    bl_idname = "OBJECT_PT_eframe_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Animation"
    bl_context = "objectmode"   


    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        subcolumn = layout.column()
        subrow = layout.row(align=True)
        subrow.operator("wm.add_eframe", icon = "HOOK")
        subrow.operator("wm.no_eframe", icon = "TRASH")
        subrow = layout.row(align=True)
        subrow.operator("wm.toggle", icon = "UV_SYNC_SELECT", depress = not g.placeable, text = g.placeable_text)
        subrow = layout.row(align=True)
        subrow.operator("wm.clear_recent", icon = "TRACKING_CLEAR_BACKWARDS")
        
        col = layout.column()
        col.prop(scene, "my_collection")
        
        col = layout.column()
        col.enabled = True if scene.my_collection else False
        col.prop(scene, "empty_objects")

def register():
    from bpy.utils import register_class
    register_class(OBJECT_PT_EFramePanel)
    register_class(AddEFrame)
    register_class(ClearEFrame)
    register_class(ClearLast)
    register_class(TogglePreview)
    
    bpy.types.Scene.my_collection = PointerProperty(
        name="Edits Collection",
        type=bpy.types.Collection)
    bpy.types.Scene.empty_objects = PointerProperty(
        name="Edit Empty",
        type=bpy.types.Object,
        poll=filter_callback)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(OBJECT_PT_EFramePanel)
    unregister_class(AddEFrame)
    unregister_class(ClearEFrame)
    unregister_class(ClearLast)
    unregister_class(TogglePreview)
    
    del bpy.types.Scene.my_collection
    del bpy.types.Collection.empty_objects

    if do_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(do_depsgraph_update)
        
    if do_depsgraph_update in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(do_depsgraph_update)
if __name__ == "__main__":
    register()

    


