from config import Config
from randomizer import Randomizer
from writer import YOLOV8Writer
import rep
import os

class Setup:
    def __init__(self, config, writer, randomizer):
        self.config = config
        self.writer = writer
        self.randomizer = randomizer
        self._output_dir_txt = os.path.join(self.config.paths['out_dir_writer'], 'txt')
        self._output_dir_bb = os.path.join(self.config.paths['out_dir_writer'], 'bb')
        self._output_dir_rgb = os.path.join(self.config.paths['out_dir_writer'], 'rgb')

        self._stage_config()
        self._writer_class_registration()

    def _stage_config(self):
        # Stage setup
        rep.settings.set_stage_meters_per_unit(1.0)
        rep.settings.set_stage_up_axis("Z")
        rep.settings.set_render_pathtraced(samples_per_pixel = 64)

    def _writer_class_registration(self):
        # Writer registration
        writer = self.writer(self.config.paths['out_dir_writer'], self.config.image_format, id_add = 0)
        rep.WriterRegistry.register(writer)

    def setup_environment(self):
        # Create environment
        room_walls = rep.create.group((rep.create.plane(position = (-10,0,0),rotation=(0,90,0),scale = 20),
                                       rep.create.plane(position = (10,0,0),rotation=(0,90,0),scale = 20),
                                       rep.create.plane(position = (0,-10,0),rotation=(90,0,0),scale = 20),
                                       rep.create.plane(position = (0,10,0),rotation=(90,0,0),scale = 20),
                                       rep.create.plane(position = (0,0,0),rotation=(0,0,0),scale = 20)))
        return room_walls