from django.shortcuts import render, redirect, reverse
import torch
from torchvision import transforms
from PIL import Image
from torch import linalg as LA
from ultralytics import YOLO
from io import BytesIO
from django.core.files import File
import numpy as np

from .capsnet import CapsNet
from .models import Lesion
from .forms import LesionForm
from .utils import get_scaled_mask, overlay

n_channels = 3  # RGB
network_classification = CapsNet(conv_inputs=n_channels,
                                 num_classes=7,
                                 init_weights=False, )
network_classification.load_state_dict(torch.load('model_weights/gpu_78_epochs_capsnet.pth',
                                                  map_location=torch.device('cpu')))

normalize = transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
Resize = transforms.Resize((384, 384))
transforms_img = transforms.Compose([Resize,
                                     transforms.ToTensor(),
                                     normalize])

idx_to_class = {0: "Actinic keratoses and intraepithelial carcinoma / Bowen's disease",
                1: 'basal cell carcinoma',
                2: 'benign keratosis-like lesions solar lentigines / seborrheic keratoses and lichen-planus like keratoses',
                3: 'dermatofibroma', 4: 'melanoma', 5: 'melanocytic nevi',
                6: 'vascular lesions (angiomas, angiokeratomas, pyogenic granulomas and hemorrhage)'}

network_segmentation = YOLO('model_weights/gpu_10_epochs_yolo.pt')


def index(request):
    lesion_objects = Lesion.objects.all()
    if len(lesion_objects) == 0:
        return render(request, 'no_photos.html')
    return render(request, 'index.html', {'lesion_objects': lesion_objects})


def upload(request):
    if request.method == 'POST':
        form = LesionForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect(reverse('main:classification', args=(form['name'].value(),)))  # tuple to save string
    else:
        form = LesionForm()
    return render(request, 'upload.html', {'form': form})


def classification(request, lesion_name):
    lesion_obj = Lesion.objects.get(name=lesion_name)

    img = Image.open(lesion_obj.lesion_Img.path)
    transformed_img = transforms_img(img)

    output = network_classification(torch.unsqueeze(transformed_img, 0))
    v_mag = LA.norm(output, ord='nuc', dim=(2, 3), keepdim=True)
    pred = torch.squeeze(v_mag.data.max(1, keepdim=True)[1].cpu()).item()

    disease = idx_to_class[pred]
    lesion_obj.disease = disease

    # predict by YOLOv8
    masks = get_scaled_mask(network_segmentation, img, conf=0.55)

    # overlay masks on original image
    image_with_masks = np.array(img)
    for mask_i in masks:
        image_with_masks = overlay(image_with_masks, mask_i, color=(0, 255, 0), alpha=0.3)

    segm_im = Image.fromarray(image_with_masks)
    blob = BytesIO()
    segm_im.save(blob, 'JPEG')
    lesion_obj.lesion_Segmentation_Img.save(f'{lesion_name}_segmented.jpg', File(blob))

    return render(request, 'image_prediction.html',
                  {'lesion': lesion_obj})
