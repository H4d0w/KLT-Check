from omni.replicator.core import Writer, AnnotatorRegistry, BackendDispatch
import numpy as np
import os


class YOLOV8Writer(Writer):

    def __init__(self, output_dir, image_format, id_add):
        super().__init__()
        self._output_dir = output_dir
        self._output_dir_txt = os.path.join(self._output_dir, 'txt')
        self._output_dir_bb = os.path.join(self._output_dir, 'bb')
        self._output_dir_rgb = os.path.join(self._output_dir, 'rgb')
        self._backend = BackendDispatch({"paths": {"out_dir": self._output_dir_rgb}})
        self._frame_id = id_add
        self.image_format = image_format
        self.annotators = [AnnotatorRegistry.get_annotator(anno_name) for anno_name in
                           ['rgb', 'bounding_box_2d_tight', 'semantic_segmentation']]

    def write(self, data):
        bb_array = []
        if "rgb" in data:
            bbox_data_tight = data["bounding_box_2d_tight"]["data"]
            id_to_labels = data["bounding_box_2d_tight"]["info"]["idToLabels"]
            rgb_color = data["rgb"]
            semantic_segmentation = data["semantic_segmentation"]["data"]

            # write RGB image file
            filepath = f"{self._frame_id}.{'png'}"
            self._backend.write_image(filepath, rgb_color)

            # filter necessary bounding box data and write to text file
            for id, labels in id_to_labels.items():
                if 'kiste' in labels['class']:
                    filtered_data = self.filter_bbox_data(id, bbox_data_tight, semantic_segmentation)
                    bb_array.extend(filtered_data)

            self.write_bbox_files(bb_array, bbox_data_tight)

        # increment frame_id for next write
        self._frame_id += 1

    def filter_bbox_data(self, id, bbox_data, semantic_segmentation):
        # Filter out and return necessary bounding box data
        bbox_data_filtered = []
        for bb in bbox_data:
            if bb["semanticId"] == id:
                # Calculate normalized values
                normalized_x = (bb["x_min"] + bb["x_max"]) / 2 / self.image_format[0]
                normalized_y = (bb["y_min"] + bb["y_max"]) / 2 / self.image_format[1]
                normalized_width = (bb["x_max"] - bb["x_min"]) / self.image_format[0]
                normalized_height = (bb["y_max"] - bb["y_min"]) / self.image_format[1]

                # Check for occlusion or other criteria if necessary
                # ...

                bbox_data_filtered.append((id, normalized_x, normalized_y, normalized_width, normalized_height))

        return bbox_data_filtered

    def write_bbox_files(self, bb_array, bbox_data_tight):
        # Write filtered bbox data to files
        bbox_filepath = os.path.join(self._output_dir_txt, f"{self._frame_id}.txt")
        with open(bbox_filepath, 'w') as file:
            for bbox in bb_array:
                line = ' '.join(map(str, bbox))
                file.write(line + '\n')


# registration of the Writer class
rep.WriterRegistry.register(YOLOV8Writer)