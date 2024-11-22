import cv2, os
from matplotlib import pyplot as plt

from lama_cleaner.model_manager import ModelManager
from lama_cleaner.schema import Config
from lama_cleaner.helper import resize_max_size
import random
from PIL import Image
import numpy as np
import torch
from dotenv import load_dotenv

load_dotenv()

local_storage_path = os.getenv('LOCAL_STORAGE_PATH')


def clean_image_with_lama(image_path, mask_path, task):
    model = ModelManager(
        # lama,ldm,zits,mat,fcf,sd1.5,anything4,realisticVision1.4,cv2,manga,sd2,paint_by_example,instruct_pix2pix
        name=task.model_name,
        sd_controlnet=False,
        sd_controlnet_method='control_v11p_sd15_canny',
        device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
        no_half=False,
        hf_access_token=None,
        disable_nsfw=False,
        sd_cpu_textencoder=False,
        sd_run_local=False,
        sd_local_model_path=False,
        local_files_only=False,
        cpu_offload=False,
        enable_xformers=False,
        # callback=diffuser_callback,
    )

    # print('model',model)

    # RGB
    image = np.array(Image.open(image_path).convert("RGB"))
    mask = np.array(Image.open(mask_path).convert("L"))
    mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]

    # reverse mask
    mask = cv2.bitwise_not(mask)

    if image.shape[:2] != mask.shape[:2]:
        print(f"Mask shape{mask.shape[:2]} not queal to Image shape{image.shape[:2]}")
        return

    original_shape = image.shape
    interpolation = cv2.INTER_CUBIC
    size_limit = max(image.shape)

    form = {
        'ldmSteps': 25,
        'ldmSampler': 'plms',
        'zitsWireframe': True,
        'hdStrategy': 'Crop',
        'hdStrategyCropMargin': 196,
        'hdStrategyCropTrigerSize': 800,
        'hdStrategyResizeLimit': 2048,
        'prompt': '',
        'negativePrompt': '',
        'croperX': 56,
        'croperY': 225,
        'croperHeight': 512,
        'croperWidth': 512,
        'useCroper': False,
        'sdMaskBlur': 5,
        'sdStrength': 0.75,
        'sdSteps': 50,  # todo
        'sdGuidanceScale': 7.5,
        'sdSampler': 'uni_pc',
        'sdSeed': -1,
        'sdMatchHistograms': False,
        'sdScale': 1,
        'cv2Radius': 5,
        'cv2Flag': 'INPAINT_NS',
        'paintByExampleSteps': 50,
        'paintByExampleGuidanceScale': 7.5,
        'paintByExampleSeed': -1,
        'paintByExampleMaskBlur': 5,
        'paintByExampleMatchHistograms': False,
        'p2pSteps': 50,
        'p2pImageGuidanceScale': 1.5,
        'p2pGuidanceScale': 7.5,
        'controlnet_conditioning_scale': 0.4,
        'controlnet_method': 'control_v11p_sd15_canny',
    }

    config = Config(
        ldm_steps=form["ldmSteps"],
        ldm_sampler=form["ldmSampler"],
        hd_strategy=form["hdStrategy"],
        zits_wireframe=form["zitsWireframe"],
        hd_strategy_crop_margin=form["hdStrategyCropMargin"],
        hd_strategy_crop_trigger_size=form["hdStrategyCropTrigerSize"],
        hd_strategy_resize_limit=form["hdStrategyResizeLimit"],
        prompt=form["prompt"],
        negative_prompt=form["negativePrompt"],
        use_croper=form["useCroper"],
        croper_x=form["croperX"],
        croper_y=form["croperY"],
        croper_height=form["croperHeight"],
        croper_width=form["croperWidth"],
        sd_scale=form["sdScale"],
        sd_mask_blur=form["sdMaskBlur"],
        sd_strength=form["sdStrength"],
        sd_steps=form["sdSteps"],
        sd_guidance_scale=form["sdGuidanceScale"],
        sd_sampler=form["sdSampler"],
        sd_seed=form["sdSeed"],
        sd_match_histograms=form["sdMatchHistograms"],
        cv2_flag=form["cv2Flag"],
        cv2_radius=form["cv2Radius"],
        paint_by_example_steps=form["paintByExampleSteps"],
        paint_by_example_guidance_scale=form["paintByExampleGuidanceScale"],
        paint_by_example_mask_blur=form["paintByExampleMaskBlur"],
        paint_by_example_seed=form["paintByExampleSeed"],
        paint_by_example_match_histograms=form["paintByExampleMatchHistograms"],
        paint_by_example_example_image=None,
        p2p_steps=form["p2pSteps"],
        p2p_image_guidance_scale=form["p2pImageGuidanceScale"],
        p2p_guidance_scale=form["p2pGuidanceScale"],
        controlnet_conditioning_scale=form["controlnet_conditioning_scale"],
        controlnet_method=form["controlnet_method"],
    )

    if config.sd_seed == -1:
        config.sd_seed = random.randint(1, 999999999)
    if config.paint_by_example_seed == -1:
        config.paint_by_example_seed = random.randint(1, 999999999)

    image = resize_max_size(image, size_limit=size_limit, interpolation=interpolation)
    mask = resize_max_size(mask, size_limit=size_limit, interpolation=interpolation)

    print('3')
    res_np_img = model(image, mask, config)

    res_np_img = cv2.cvtColor(res_np_img.astype(np.uint8), cv2.COLOR_BGR2RGB)

    # Загрузка результата
    result_image = Image.fromarray(res_np_img)

    # Сохранение обработанного изображения временно
    result_path = f"{local_storage_path}/{task.id}/result.png"
    result_image.save(result_path)
