bl_info = {
    "name": "Vertex Overlap",
    "description": "Blender N-panel add-on that alerts you to overlapping vertices in real-time.",
    "author": "Shawn Shipley",
    "version": (1, 0, 1),
    "blender": (4, 2, 0),
    "category": "3D View",
    "doc_url": "https://github.com/shawnshipley/vertex-overlap",
    "support": "Community"
}

from .vertex_overlap import *

def register():
    vertex_overlap.register()

def unregister():
    vertex_overlap.unregister()

if __name__ == "__main__":
    register()