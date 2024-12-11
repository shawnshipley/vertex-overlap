import bpy
import bmesh
from bpy.app.handlers import persistent

def check_overlapping_verts(context):
    obj = context.active_object
    if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        overlap_count = 0
        visited = set()

        for vert in bm.verts:
            if vert.is_valid:
                pos = tuple(round(coord, 6) for coord in vert.co)
                if pos in visited:
                    overlap_count += 1
                else:
                    visited.add(pos)
        context.scene.overlapping_verts = overlap_count
    else:
        context.scene.overlapping_verts = 0

@persistent
def check_mode_change(dummy):
    context = bpy.context
    if context.active_object and context.active_object.type == 'MESH':
        if context.active_object.mode == 'EDIT':
            check_overlapping_verts(context)

class OverlapVertexCheckerPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_overlap_vertex_checker"
    bl_label = "Vertex Overlap"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Edit"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        row.prop(scene, "overlap_threshold")
        
        row = layout.row()
        row.operator("object.check_overlapping_verts", text="Check Overlaps")
        
        row = layout.row()
        row.label(text=f"Overlapping Vertices: {scene.overlapping_verts}")
        
        row = layout.row()
        row.operator("object.merge_overlapping_verts")

class CheckOverlappingVertsOperator(bpy.types.Operator):
    bl_idname = "object.check_overlapping_verts"
    bl_label = "Check for Overlaps"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        check_overlapping_verts(context)
        self.report({'INFO'}, f"Found {context.scene.overlapping_verts} overlapping vertices")
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
        bpy.ops.mesh.remove_doubles(threshold=context.scene.overlap_threshold)
        check_overlapping_verts(context)
        return {'FINISHED'}

CLASSES =  [OverlapVertexCheckerPanel,
            CheckOverlappingVertsOperator,
            MergeOverlappingVertsOperator,
            ]

def register():
    for cls in CLASSES:
        try:
            bpy.utils.register_class(cls)
        except:
            print(f"{cls.__name__} already registred")

    bpy.types.Scene.overlap_threshold = bpy.props.FloatProperty(
        name="Overlap Threshold",
        description="Threshold distance for overlapping vertices",
        default=0.001,
        min=0.0,
        precision=4
    )

    bpy.types.Scene.overlapping_verts = bpy.props.IntProperty(
        name="Overlapping Vertices",
        default=0
    )

    bpy.app.handlers.depsgraph_update_post.append(check_mode_change)

def unregister():
    for cls in reversed(CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass

    del bpy.types.Scene.overlap_threshold
    del bpy.types.Scene.overlapping_verts
    bpy.app.handlers.depsgraph_update_post.remove(check_mode_change)
