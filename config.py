class Config:
    image_format = (640, 640)
    trigger_count = 10
    randomizations = {
        "camera": True,
        "materials": False,
        "lighting": True,
        "objectPose": False,
        "objectObscuring": False,
        "background": True,
        "configuration": False,
    }
    datasetsize = 10000
    paths = {
        "objects_of_interest": r"F:\.projects\KLT-Check\Kistenpruefung\CAD_Files\ESK_ASM.usd",
        "scatter_object_folder": r"F:\.projects\KLT-Check\Kistenpruefung\CAD_Files\Scatter_objects",
        "textures": r"F:\.projects\KLT-Check\Kistenpruefung\Texturen_Background",
        "out_dir_writer": r'F:\.projects\KLT-Check\Kistenpruefung\Output'
    }
