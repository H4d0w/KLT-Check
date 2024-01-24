import os

import numpy as np
import omni.replicator.core as rep
from omni.replicator.core import Writer, AnnotatorRegistry, BackendDispatch

###############################################################################################################


image_format = (640,640)
trigger_count = 10


Camera_Randomization = True
Materials_Randomization = False
Lighting_Randomization = True
ObjectPose_Randomization = False
ObscurringItems = False
Background_Randomization = True
Configuration_Randomization = False
#Augmentation = True/False
Datasetsize = 10000

path_objects_of_interest = (r"F:\.projects\KLT-Check\Kistenpruefung\CAD_Files\ESK_ASM.usd")
scatter_object_folder = (r"F:\.projects\KLT-Check\Kistenpruefung\CAD_Files\Scatter_objects")
path_textures_rand_mats = r"F:\.projects\KLT-Check\Kistenpruefung\Texturen_Background"
out_dir_writer = r'F:\.projects\KLT-Check\Kistenpruefung\Output'


###############################################################################################################

#set global stage settings
rep.settings.set_stage_meters_per_unit(1.0)
rep.settings.set_stage_up_axis("Z")
rep.settings.set_render_pathtraced(samples_per_pixel = 64)

#writer class definition

class YOLOV8Writer(Writer):
    def __init__(self,output_dir, image_format, id_add):
        #setup
        self._output_dir = output_dir
        self._output_dir_txt= os.path.join(self._output_dir,'txt')
        self._output_dir_bb= os.path.join(self._output_dir,'bb')
        self._output_dir_rgb= os.path.join(self._output_dir,'rgb')
        self._backend = BackendDispatch({"paths": {"out_dir": self._output_dir_rgb}})
        self._frame_id = 0+id_add
        self.image_format = image_format

        #initialize annotators
        self.annotators = []

        self.annotators.append(AnnotatorRegistry.get_annotator("rgb"))
        #self.annotators.append(AnnotatorRegistry.get_annotator("bounding_box_2d_loose", init_params={"semanticTypes": ["class"]}))
        self.annotators.append(AnnotatorRegistry.get_annotator("bounding_box_2d_tight", init_params={"semanticTypes": ["class"]}))
        self.annotators.append(AnnotatorRegistry.get_annotator("semantic_segmentation", init_params={"colorize": False}))
        #self.annotators.append(AnnotatorRegistry.get_annotator("occlusion", init_params={"semanticTypes": ["class"]}))

    #write
    def write(self, data):
        bb_array = []
        if "rgb" in data:
            #bbox_data_loose = data["bounding_box_2d_loose"]["data"]
            bbox_data_tight = data["bounding_box_2d_tight"]["data"]
            
            id_to_labels = data["bounding_box_2d_tight"]["info"]["idToLabels"]
            rgb_color = data["rgb"]
            semantic_segmentation = data["semantic_segmentation"]["data"]
            
            filepath = f"{self._frame_id}.{'png'}"
            self._backend.write_image(filepath, rgb_color)
    
            for id, labels in id_to_labels.items(): #notwendig ? eig soll mit jedem trigger 1 bild gemacht werden
                id = int(id)

                if 'kiste' in labels['class']:
                    
                    i = 0
                    bb_array = []
                    for bb in bbox_data_tight:
                
                        if bb["semanticId"] == id:

                            # normalized_middle_x = (((bbox_data_loose["x_max"][i] + bbox_data_loose["x_min"][i])/2)/self.image_format[0])
                            # normalized_middle_y= (((bbox_data_loose["y_max"][i] + bbox_data_loose["y_min"][i])/2)/self.image_format[1])
                            
                            # normalized_width = (bbox_data_loose["x_max"][i] - bbox_data_loose["x_min"][i])/self.image_format[0]
                            # normalized_height = (bbox_data_loose["y_max"][i] - bbox_data_loose["y_min"][i])/self.image_format[1]
                            
                            box = semantic_segmentation[bbox_data_tight["x_min"][i]:bbox_data_tight["x_max"][i], bbox_data_tight["y_min"][i]:bbox_data_tight["y_max"][i]]
                            count = np.sum(box == 2)
                    
                            box = semantic_segmentation[bbox_data_tight["y_min"][i]:bbox_data_tight["y_max"][i], bbox_data_tight["x_min"][i]:bbox_data_tight["x_max"][i]]
                            count = np.sum(box == 2)
                          
                            bbox_pixels= (bbox_data_tight["x_max"][i] - bbox_data_tight["x_min"][i])*(bbox_data_tight["y_max"][i] - bbox_data_tight["y_min"][i])
                            
                            occ_factor = count/bbox_pixels
                    

                            normalized_middle_x_tight = (((bbox_data_tight["x_max"][i] + bbox_data_tight["x_min"][i])/2)/self.image_format[0])
                            normalized_middle_y_tight = (((bbox_data_tight["y_max"][i] + bbox_data_tight["y_min"][i])/2)/self.image_format[1])

                            normalized_width_tight = (bbox_data_tight["x_max"][i] - bbox_data_tight["x_min"][i])/self.image_format[0]
                            normalized_height_tight = (bbox_data_tight["y_max"][i] - bbox_data_tight["y_min"][i])/self.image_format[1]
                            
                            procentual_bb_area_on_screen = (normalized_height_tight * normalized_width_tight)
                            
                            if procentual_bb_area_on_screen > 0.03 and occ_factor > 0.2:
                                bb_array.append((id,normalized_middle_x_tight,normalized_middle_y_tight,normalized_width_tight,normalized_height_tight))
                                
                        i += 1

                
            bbox_filepath = f"{self._frame_id}.{'txt'}"
            bbox_filepath_absolut = os.path.join(self._output_dir_txt,bbox_filepath)
            with open(bbox_filepath_absolut, 'a') as file:
                for tup in bb_array:
                    line = ' '.join(map(str, tup))
                    file.write(line + '\n')
                    
            bbox_tight_filepath = f"{self._frame_id}.{'txt'}"
            bbox_tight_filepath_absolut = os.path.join(self._output_dir_bb,bbox_tight_filepath)
            with open(bbox_tight_filepath_absolut, 'a') as file:
                for tup in bbox_data_tight:
                    line = ' '.join(map(str, tup))
                    file.write(line + '\n')

        self._frame_id += 1
        

rep.WriterRegistry.register(YOLOV8Writer)



with rep.new_layer():
    
    # BIN PLACE
    kiste = rep.create.from_usd(path_objects_of_interest, semantics=[("class","kiste")])
    
    cube_inside_box = rep.create.cube(
        position = [0,0,0.1],
        scale = [0.35,0.25,0.18],
        visible = False,
    )
        
    # CAMERA PLACE
    camera = rep.create.camera(
        position=(0, 0, 1.5),
        rotation = [0,-90,90],
        focal_length= 0.20, 
        focus_distance= 0.76,
        horizontal_aperture= 0.32,
        #vertical_aperture_offset = -0.13,
        clipping_range= (0.000000000000000001, 1000))
    render_product0 = rep.create.render_product(camera, (image_format))
    
    # camera1 = rep.create.camera(
    #     position=(10, -10, 5),
    #     look_at = (0,0,0),
    #     focal_length= 0.20, 
    #     focus_distance= 0.76,
    #     horizontal_aperture= 0.32,
    #     #vertical_aperture_offset = -0.13,
    #     clipping_range= (0.000000000000000001, 1000))
    # render_product1 = rep.create.render_product(camera1, (image_format))
    
     #Generierung der zufälligen Materialien
    
    textures = [os.path.join(root, name)
                 for root, folders, files in os.walk(path_textures_rand_mats)
                 for name in files
                 if name.endswith((".jpg", ".png",".jepg",".JPG",".PNG", ".JPEG"))]
    
    scatter_usds = [os.path.join(root, name)
                 for root, folders, files in os.walk(scatter_object_folder)
                 for name in files
                 if name.endswith((".usd"))]
    
    print(scatter_usds)    
    
    random_mats = rep.create.material_omnipbr(diffuse_texture=rep.distribution.choice(textures),                                                    
                                                   roughness=rep.distribution.uniform(0, 1),                                               
                                                   metallic=rep.distribution.choice([0, 1]),                                                    
                                                   emissive_texture=rep.distribution.choice(textures),           
                                                   emissive_intensity=rep.distribution.uniform(0, 100),
                                                   count = 1000)###########################################################################################ACHTUNG noch auf 3000 setzen


    wall1 = rep.create.plane(position = (-10,0,0),rotation=(0,90,0),scale = 20)
    wall2 = rep.create.plane(position = (10,0,0),rotation=(0,90,0),scale = 20)
    wall3 = rep.create.plane(position = (0,-10,0),rotation=(90,0,0),scale = 20)
    wall4 = rep.create.plane(position = (0,10,0),rotation=(90,0,0),scale = 20)
    ground = rep.create.plane(position = (0,0,0),rotation=(0,0,0),scale = 20)
    
      #Randomisierung der Wandmaterialien
    def randomize_background_materials():
        room_walls = rep.create.group((wall1,wall2,wall3,wall4,ground))
        with room_walls:
            rep.randomizer.materials(random_mats)
            
    def randomized_lights():
        random_rect_lights = rep.create.light(
            position = rep.distribution.uniform((-5,-5,5),(5,5,10)),
            look_at = [0,0,0],
            intensity = rep.distribution.uniform(200000, 1500000),
            temperature = rep.distribution.uniform(100, 10000),
            scale = rep.distribution.uniform((1,1,1),(5,5,5)),
            count = 3,
            color = rep.distribution.uniform((0,0,0),(1,1,1)),
            light_type="rect")
        random_dome_lights = rep.create.light(
            intensity = rep.distribution.uniform(5,30),
            temperature = (2000),
            color = rep.distribution.uniform((0,0,0),(1,1,1)),
            light_type="dome")
        random_sphere_lights = rep.create.light (
            position = rep.distribution.uniform((-90,-90,-90),(90,90,90)),
            look_at = rep.distribution.uniform((-20,-20,-20),(20,20,20)), 
            intensity = rep.distribution.uniform(200000,1500000),
            scale = rep.distribution.uniform((1,1,1),(5,5,5)),
            count= 3,
            color = rep.distribution.uniform((0,0,0),(1,1,1)),
            light_type="sphere")
        
    def randomize_OoI():
        with kiste:
            rep.modify.pose(position = [0,0,0], rotation = [0,0,0], scale = 1)
            #rep.modify.visibility(rep.distribution.choice([True,True,False]))
            
    
    def env_props(size=50):
        instances = rep.randomizer.instantiate(rep.utils.get_usd_files(scatter_object_folder), size=size, mode='point_instance')
        with instances:
            rep.modify.pose(
                position=rep.distribution.uniform((-0.13,-0.1,0.06), (0.13,0.1,0.18)),
                rotation=rep.distribution.uniform((-90,-180, 0), (-90, 180, 0)),
            )
        return instances.node
    

            
    def scatter_inside_box():
        for scatter_usd_paths in scatter_usds:
            rep.randomizer.scatter_3d(
                min_samp =[-0.13,-0.1,0.06],
                max_samp =[0.13,0.1,0.18],
                check_for_collisions = False,
                input_prims = rep.create.from_usd(scatter_usd_paths, semantics=("class","scatter_object"))
                )
            

    rep.randomizer.register(randomize_background_materials)
    rep.randomizer.register(randomized_lights)
    rep.randomizer.register(randomize_OoI)
    rep.randomizer.register(scatter_inside_box)
    rep.randomizer.register(env_props)
    
    writer = rep.WriterRegistry.get("YOLOV8Writer")
    writer.initialize(output_dir= out_dir_writer, image_format = image_format, id_add = 0)
    writer.attach([render_product0])
        
    with rep.trigger.on_frame(max_execs=trigger_count, rt_subframes=64):
        with camera:
            rep.modify.pose(position=rep.distribution.uniform((-0.05, -0.05, 1), (0.05, 0.05, 1.5)), 
                            rotation = rep.distribution.uniform((-1,-91,85),(1,-89,95))
                            )
            
        with kiste:
            rep.randomizer.color(colors=rep.distribution.uniform((0, 0, 0), (0.002, 0.002, 0.002)))

            rep.physics.collider(approximation_shape = "meshSimplification")
        rep.randomizer.env_props(2)
        rep.randomizer.randomize_background_materials()
        rep.randomizer.randomized_lights()
        rep.randomizer.randomize_OoI()
        rep.randomizer.scatter_inside_box()
            
            
    rep.orchestrator.step()
            
            