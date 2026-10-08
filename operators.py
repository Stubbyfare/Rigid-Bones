import bpy
from mathutils import Vector
import math


class RIGIDG_OT_add_rigid_body(bpy.types.Operator):
    bl_idname = "wm.add_rigid_body"
    bl_label = "Add Rigid Body"
    bl_description = "Add rigid body collider to selected bone(s)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.type != "ARMATURE":
            self.report({"ERROR"}, "Select an armature first.")
            return {"FINISHED"}

        if context.mode != "POSE":
            try:
                bpy.ops.object.mode_set(mode="POSE")
            except RuntimeError:
                self.report({"ERROR"}, "Switch to Pose Mode before adding rigid bodies.")
                return {"FINISHED"}

        bones = context.selected_pose_bones
        if not bones:
            self.report({"WARNING"}, "No bones selected.")
            return {"FINISHED"}

        props = context.scene.rigid_bones_props
        for bone in bones:
            self._create_rigid_body_for_bone(context, obj, bone, props)

        self.report({"INFO"}, f"Added rigid bodies to {len(bones)} bone(s).")
        return {"FINISHED"}

    def _create_rigid_body_for_bone(self, context, armature, bone, props):
        head = armature.matrix_world @ bone.head
        tail = armature.matrix_world @ bone.tail
        direction = tail - head
        if direction.length == 0:
            direction = Vector((0.0, 0.0, 1.0))

        length = max(direction.length, 0.05)
        radius = max((bone.length if getattr(bone, "length", 0) > 0 else 0.1) * 0.5, 0.05)

        if props.collision_shape == "BOX":
            mesh = self._create_box_mesh(length, radius)
            shape_name = "BOX"
        elif props.collision_shape == "SPHERE":
            mesh = self._create_sphere_mesh(radius)
            shape_name = "SPHERE"
        elif props.collision_shape == "CAPSULE":
            mesh = self._create_capsule_mesh(length, radius)
            shape_name = "CAPSULE"
        else:
            mesh = self._create_cylinder_mesh(length, radius)
            shape_name = "CYLINDER"

        object_name = f"RB_{armature.name}_{bone.name}_{shape_name}"
        collision_obj = bpy.data.objects.new(object_name, mesh)
        context.collection.objects.link(collision_obj)

        collision_obj.location = head + (direction * 0.5)
        quat = direction.to_track_quat("-Z", "Y")
        collision_obj.rotation_euler = quat.to_euler()

        collision_obj.parent = armature
        collision_obj.parent_type = "BONE"
        collision_obj.parent_bone = bone.name

        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = collision_obj
        collision_obj.select_set(True)
        bpy.ops.rigidbody.objects_add(type="ACTIVE")

        rigid_body = collision_obj.rigid_body
        rigid_body.mass = props.mass
        rigid_body.friction = props.friction
        rigid_body.restitution = props.restitution
        rigid_body.enabled = props.enabled

        delete_constraint = collision_obj.constraints.new(type="COPY_LOCATION")
        delete_constraint.target = armature
        delete_constraint.subtarget = bone.name

    @staticmethod
    def _create_box_mesh(length, radius):
        mesh = bpy.data.meshes.new("rb_box_mesh")
        size = max(radius, 0.05)
        verts = [
            (-size, -size, 0.0),
            (size, -size, 0.0),
            (size, size, 0.0),
            (-size, size, 0.0),
            (-size, -size, length),
            (size, -size, length),
            (size, size, length),
            (-size, size, length),
        ]
        faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
        ]
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        return mesh

    @staticmethod
    def _create_sphere_mesh(radius):
        mesh = bpy.data.meshes.new("rb_sphere_mesh")
        verts = []
        faces = []
        segments_u = 12
        segments_v = 12

        for v in range(segments_v + 1):
            for u in range(segments_u + 1):
                theta = (u / segments_u) * 2.0 * math.pi
                phi = (v / segments_v) * math.pi
                x = radius * math.sin(phi) * math.cos(theta)
                y = radius * math.sin(phi) * math.sin(theta)
                z = radius * math.cos(phi)
                verts.append((x, y, z))

        for v in range(segments_v):
            for u in range(segments_u):
                a = v * (segments_u + 1) + u
                b = a + 1
                c = a + segments_u + 1
                d = c + 1
                faces.append((a, b, d, c))

        mesh.from_pydata(verts, [], faces)
        mesh.update()
        return mesh

    @staticmethod
    def _create_capsule_mesh(length, radius):
        mesh = bpy.data.meshes.new("rb_capsule_mesh")
        segments = 12
        verts = []
        faces = []

        # Cylinder body
        for i in range(segments):
            angle = (i / segments) * 2.0 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            verts.append((x, y, 0.0))
            verts.append((x, y, length))
        for i in range(segments):
            a = i * 2
            b = ((i + 1) % segments) * 2
            c = b + 1
            d = a + 1
            faces.append((a, b, c, d))

        mesh.from_pydata(verts, [], faces)
        mesh.update()
        return mesh

    @staticmethod
    def _create_cylinder_mesh(length, radius):
        mesh = bpy.data.meshes.new("rb_cylinder_mesh")
        segments = 12
        verts = []
        faces = []

        for i in range(segments):
            angle = (i / segments) * 2.0 * math.pi
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            verts.append((x, y, 0.0))
            verts.append((x, y, length))

        for i in range(segments):
            a = i * 2
            b = ((i + 1) % segments) * 2
            c = b + 1
            d = a + 1
            faces.append((a, b, c, d))

        bottom = [i * 2 for i in range(segments)]
        top = [i * 2 + 1 for i in range(segments)]
        faces.append(tuple(bottom))
        faces.append(tuple(reversed(top)))

        mesh.from_pydata(verts, [], faces)
        mesh.update()
        return mesh


class RIGIDG_OT_remove_rigid_body(bpy.types.Operator):
    bl_idname = "wm.remove_rigid_body"
    bl_label = "Remove Rigid Body"
    bl_description = "Remove rigid body colliders from selected bone(s)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        armature = context.active_object
        if armature is None or armature.type != "ARMATURE":
            self.report({"ERROR"}, "Select an armature first.")
            return {"FINISHED"}

        selected_bones = context.selected_pose_bones
        if not selected_bones:
            self.report({"WARNING"}, "No bones selected.")
            return {"FINISHED"}

        removed = 0
        for obj in list(bpy.data.objects):
            if obj.type == "MESH" and obj.name.startswith(f"RB_{armature.name}_"):
                for bone in selected_bones:
                    if bone.name in obj.name:
                        bpy.data.objects.remove(obj, do_unlink=True)
                        removed += 1
                        break

        self.report({"INFO"}, f"Removed {removed} rigid body/bodies.")
        return {"FINISHED"}


class RIGIDG_OT_bake_simulation(bpy.types.Operator):
    bl_idname = "wm.bake_simulation"
    bl_label = "Bake Simulation"
    bl_description = "Bake rigid body simulation to animation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.rigid_bones_props
        scene = context.scene
        scene.frame_start = props.frame_start
        scene.frame_end = props.frame_end

        active_objects = [obj for obj in scene.objects if obj.type == "MESH" and obj.rigid_body is not None]
        if not active_objects:
            self.report({"WARNING"}, "No rigid bodies found in the scene.")
            return {"FINISHED"}

        try:
            bpy.ops.rigidbody.bake_to_keyframes(
                frame_start=props.frame_start,
                frame_end=props.frame_end,
            )
            self.report({"INFO"}, "Rigid body simulation baked successfully.")
        except RuntimeError as exc:
            self.report({"ERROR"}, f"Bake failed: {exc}")

        return {"FINISHED"}
