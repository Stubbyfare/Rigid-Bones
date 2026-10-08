bl_info = {
    "name": "Rigid-Bones",
    "blender": (5, 2, 2),
    "category": "Rigging",
    "version": (1, 0, 0),
    "author": "Stubbyfare",
    "description": "Add rigid bodies to rigs in Blender 5.2.2",
    "location": "3D Viewport > Sidebar > Rigid-Bones",
}

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty

from .operators import (
    RIGIDG_OT_add_rigid_body,
    RIGIDG_OT_remove_rigid_body,
    RIGIDG_OT_bake_simulation,
)
from .ui import RIGIDG_PT_panel


class RigidBonesProperties(bpy.types.PropertyGroup):
    mass: FloatProperty(
        name="Mass",
        description="Mass of the rigid body",
        default=1.0,
        min=0.001,
        soft_max=1000.0,
    )

    friction: FloatProperty(
        name="Friction",
        description="Friction of the rigid body",
        default=0.5,
        min=0.0,
        max=1.0,
    )

    restitution: FloatProperty(
        name="Restitution",
        description="Bounce/elasticity of the rigid body",
        default=0.0,
        min=0.0,
        max=1.0,
    )

    use_collision: BoolProperty(
        name="Use Collision",
        description="Enable collision for this bone",
        default=True,
    )

    enabled: BoolProperty(
        name="Enable Rigid Body",
        description="Toggle the rigid body simulation",
        default=True,
    )

    collision_shape: EnumProperty(
        name="Collision Shape",
        description="Shape of the collision object",
        items=[
            ("BOX", "Box", "Box collision shape"),
            ("SPHERE", "Sphere", "Sphere collision shape"),
            ("CAPSULE", "Capsule", "Capsule collision shape"),
            ("CYLINDER", "Cylinder", "Cylinder collision shape"),
        ],
        default="BOX",
    )

    frame_start: IntProperty(
        name="Frame Start",
        description="Simulation start frame",
        default=1,
        min=0,
    )

    frame_end: IntProperty(
        name="Frame End",
        description="Simulation end frame",
        default=250,
        min=0,
    )


classes = (
    RigidBonesProperties,
    RIGIDG_OT_add_rigid_body,
    RIGIDG_OT_remove_rigid_body,
    RIGIDG_OT_bake_simulation,
    RIGIDG_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.rigid_bones_props = bpy.props.PointerProperty(
        type=RigidBonesProperties
    )


def unregister():
    if hasattr(bpy.types.Scene, "rigid_bones_props"):
        del bpy.types.Scene.rigid_bones_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
