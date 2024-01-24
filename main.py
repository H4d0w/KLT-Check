import os
import rep
from config import Config
from randomizer import Randomizer
from setup import Setup
from writer import YOLOV8Writer


def main():
    # Initialize configuration and randomizer
    config = Config()
    randomizer = Randomizer()

    # Initialize and configure the setup
    setup = Setup(config, YOLOV8Writer, randomizer)
    setup._stage_config()
    setup._writer_class_registration()

    # Register YOLOV8Writer
    writer = YOLOV8Writer(config.paths['out_dir_writer'], config.image_format, 0)
    rep.WriterRegistry.register(writer)

    # Main loop for creating scenes and rendering
    for _ in range(config.trigger_count):
        with rep.new_layer():
            # Object Initialization
            kiste = rep.create.from_usd(config.paths['objects_of_interest'], semantics=[("class", "kiste")])

            # Camera and Render Product Setup
            camera = rep.create.camera(position=(0, 0, 1.5), rotation=[0, -90, 90], focal_length=0.20,
                                       focus_distance=0.76, horizontal_aperture=0.32,
                                       clipping_range=(0.000000000000000001, 1000))
            render_product0 = rep.create.render_product(camera, config.image_format)

            # Randomization Calls
            randomizer.randomize_material(kiste)
            randomizer.randomize_lights()
            randomizer.randomize_pose(kiste)
            randomizer.scatter_objects_inside_box(kiste)

            # Attach writer to render product
            writer.attach([render_product0])

            # Trigger processing
            with rep.trigger.on_frame(max_execs=config.trigger_count, rt_subframes=64):
                # Additional randomizations or modifications per frame
                # ...

                # Step the orchestrator to process the frame
                rep.orchestrator.step()


if __name__ == "__main__":
    main()
