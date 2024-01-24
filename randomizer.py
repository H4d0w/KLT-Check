from config import Config
import os
import rep


class Randomizer:
    def __init__(self):
        self.textures = self._load_textures(Config.paths["textures"])
        self.scatter_usds = self._load_scatter_usds(Config.paths["scatter_object_folder"])

    # Private method to load textures
    def _load_textures(self, path):
        return [os.path.join(root, name) for root, folders, files in os.walk(path) for name in files if
                name.endswith((".jpg", ".png", ".jpeg", ".JPG", ".PNG", ".JPEG"))]

    # Private method to load .USD files
    def _load_scatter_usds(self, path):
        return [os.path.join(root, name) for root, folders, files in os.walk(path) for name in files if
                name.endswith((".usd"))]

    def randomize_material(self, obj_ref):
        materials = rep.create.material_omnipbr(
            diffuse_texture=rep.distribution.choice(self.textures),
            roughness=rep.distribution.uniform(0, 1),
            metallic=rep.distribution.choice([0, 1]),
            emissive_texture=rep.distribution.choice(self.textures),
            emissive_intensity=rep.distribution.uniform(0, 100),
            count=len(self.textures)
        )

        with obj_ref:
            rep.randomizer.materials(materials)

    def randomize_lights(self):
        random_rect_lights = rep.create.light(
            position=rep.distribution.uniform((-5, -5, 5), (5, 5, 10)),
            look_at=[0, 0, 0],
            intensity=rep.distribution.uniform(200000, 1500000),
            temperature=rep.distribution.uniform(100, 10000),
            scale=rep.distribution.uniform((1, 1, 1), (5, 5, 5)),
            count=3,
            color=rep.distribution.uniform((0, 0, 0), (1, 1, 1)),
            light_type="rect"
        )

        random_dome_lights = rep.create.light(
            intensity=rep.distribution.uniform(5, 30),
            temperature=(2000),
            color=rep.distribution.uniform((0, 0, 0), (1, 1, 1)),
            light_type="dome"
        )

        random_sphere_lights = rep.create.light(
            position=rep.distribution.uniform((-90, -90, -90), (90, 90, 90)),
            look_at=rep.distribution.uniform((-20, -20, -20), (20, 20, 20)),
            intensity=rep.distribution.uniform(200000, 1500000),
            scale=rep.distribution.uniform((1, 1, 1), (5, 5, 5)),
            count=3,
            color=rep.distribution.uniform((0, 0, 0), (1, 1, 1)),
            light_type="sphere"
        )

    def randomize_pose(self, obj_ref):
        with obj_ref:
            rep.modify.pose(
                position=rep.distribution.uniform((-0.13, -0.1, 0.06), (0.13, 0.1, 0.18)),
                rotation=rep.distribution.uniform((-90, -180, 0), (-90, 180, 0))
            )

    def scatter_objects_inside_box(self, obj_ref):
        for scatter_usd_path in self.scatter_usds:
            with obj_ref:
                rep.randomizer.scatter_3d(
                    min_samp=[-0.13, -0.1, 0.06],
                    max_samp=[0.13, 0.1, 0.18],
                    check_for_collisions=False,
                    input_prims=rep.create.from_usd(scatter_usd_path, semantics=("class", "scatter_object"))
                )