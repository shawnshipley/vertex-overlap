import bpy
import bmesh
from bpy.app.handlers import persistent

def check_overlapping_verts(context):
    total_overlaps = 0
    
    # Get all selected objects that are in Edit mode
    selected_objects = [obj for obj in context.selected_objects 
                       if obj.type == 'MESH' and obj.mode == 'EDIT']
    
    threshold = context.scene.vertex_overlap.overlap_threshold
    
    for obj in selected_objects:
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        overlap_count = 0
        # Create a dictionary to store vertex positions
        vert_positions = {}
        
        for vert in bm.verts:
            if not vert.is_valid:
                continue
                
            # Round the coordinates based on threshold
            # This ensures vertices within threshold distance are considered the same
            pos = tuple(round(coord / threshold) for coord in vert.co)
            
            if pos in vert_positions:
                overlap_count += 1
            else:
                vert_positions[pos] = True
                    
        total_overlaps += overlap_count
        
    context.scene.vertex_overlap.overlapping_verts = total_overlaps

@persistent
def check_mode_change(dummy):
    context = bpy.context
    # Toggle
    if context.scene.vertex_overlap.overlap_checking_enabled:
    # Toggle
        if context.mode == 'EDIT_MESH' and context.selected_objects:
            check_overlapping_verts(context)
        else:
            context.scene.vertex_overlap.overlapping_verts = 0

class OverlapVertexCheckerPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_overlap_vertex_checker"
    bl_label = "Vertex Overlap"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Edit"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.vertex_overlap  # Get the property group
        
        row = layout.row()
        status = "" if props.overlap_checking_enabled else "(disabled)"
        row.prop(props, "overlap_checking_enabled", text=f"Real-time Checking {status}")

        row = layout.row()
        row.prop(props, "overlap_threshold")
        
        row = layout.row()
        row.operator("object.check_overlapping_verts", text="Check Overlaps")
        
        row = layout.row()
        row.label(text=f"Overlapping Vertices: {props.overlapping_verts}")
        
        row = layout.row()
        row.operator("object.merge_overlapping_verts")

class CheckOverlappingVertsOperator(bpy.types.Operator):
    bl_idname = "object.check_overlapping_verts"
    bl_label = "Check for Overlaps"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Check for overlapping vertices (only available in Edit Mode)"

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and 
                context.active_object.type == 'MESH' and 
                context.active_object.mode == 'EDIT')

    def execute(self, context):
        check_overlapping_verts(context)
        self.report({'INFO'}, f"Found {context.scene.vertex_overlap.overlapping_verts} overlapping vertices")
        return {'FINISHED'}

class MergeOverlappingVertsOperator(bpy.types.Operator):
    bl_idname = "object.merge_overlapping_verts"
    bl_label = "Merge Vertices"

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and 
                context.active_object.type == 'MESH' and 
                context.active_object.mode == 'EDIT')

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=context.scene.vertex_overlap.overlap_threshold)
        check_overlapping_verts(context)
        return {'FINISHED'}

class VertexOverlapProperties(bpy.types.PropertyGroup):
    overlap_threshold: bpy.props.FloatProperty(
        name="Overlap Threshold",
        description="Threshold distance for overlapping vertices",
        default=0.0001,
        min=0.0,
        precision=4
    )
    
    overlapping_verts: bpy.props.IntProperty(
        name="Overlapping Vertices",
        default=0
    )
    
    overlap_checking_enabled: bpy.props.BoolProperty(
        name="Enable Overlap Checking",
        description="Toggle real-time checking of overlapping vertices",
        default=False
    )

CLASSES =  [VertexOverlapProperties,
            OverlapVertexCheckerPanel,
            CheckOverlappingVertsOperator,
            MergeOverlappingVertsOperator,
            ]

def register():
    for cls in CLASSES:
        try:
            bpy.utils.register_class(cls)
        except:
            print(f"{cls.__name__} already registred")

    bpy.types.Scene.vertex_overlap = bpy.props.PointerProperty(type=VertexOverlapProperties)
    bpy.app.handlers.depsgraph_update_post.append(check_mode_change)

def unregister():
    for cls in reversed(CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass

    del bpy.types.Scene.vertex_overlap
    bpy.app.handlers.depsgraph_update_post.remove(check_mode_change)
