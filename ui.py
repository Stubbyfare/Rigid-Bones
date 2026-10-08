import bpy


class RIGIDG_PT_panel(bpy.types.Panel):
    bl_label = "Rigid-Bones"
    bl_idname = "RIGIDG_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rigid-Bones"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.rigid_bones_props

        layout.label(text="Rigid Body Rigging", icon="RIGID_BODY")
        layout.separator()

        if context.active_object is None or context.active_object.type != "ARMATURE":
            layout.label(text="Select an armature", icon="INFO")
            return

        box = layout.box()
        box.label(text="Rigid Body Settings")
        box.prop(props, "mass")
        box.prop(props, "friction")
        box.prop(props, "restitution")
        box.prop(props, "collision_shape")
        box.prop(props, "enabled")

        layout.separator()

        box = layout.box()
        box.label(text="Tools")
        row = box.row(align=True)
        row.operator("wm.add_rigid_body", text="Add Rigid Body", icon="ADD")
        row.operator("wm.remove_rigid_body", text="Remove", icon="TRASH")

        layout.separator()

        box = layout.box()
        box.label(text="Bake Settings")
        box.prop(props, "frame_start")
        box.prop(props, "frame_end")
        box.operator("wm.bake_simulation", text="Bake Simulation", icon="ANIM")

        layout.separator()

        box = layout.box()
        box.label(text="How to use")
        box.label(text="1. Select an armature")
        box.label(text="2. Enter Pose Mode")
        box.label(text="3. Select bone(s)")
        box.label(text="4. Click Add Rigid Body")
