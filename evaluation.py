import numpy as np
import matplotlib.pyplot as plt
import torch
from torch.utils.data import Dataset
from torchvision import transforms as T
from PIL import Image
import cv2
import albumentations as A
import os
from tqdm import tqdm
from model import ViT_UNet
from dataset import (IMAGE_PATH, MASK_PATH, X_test)
from utils import *
import sys
sys.path.append('UTNet/model')
from utnet import UTNet
from swin_unet import SwinUnet, SwinUnet_config

# Set GPU number
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

## import pretrained model
#model = ViT_UNet(img_size=(512, 768))
#saved_path = "saved_model/ViT_UNet.pt"

#config = SwinUnet_config()
#model = SwinUnet(config, img_size=(512,768), num_classes=23, zero_head=False, vis=False)
#saved_path = "saved_model/SwinUnet-0.346.pt"
model = UTNet(in_chan = 3, base_chan = 16, num_classes=23, block_list='234',num_blocks =[1,2,4], num_heads=[2,4,8], attn_drop=0.1, proj_drop=0.1)
saved_path = "saved_model/UTnet.pt"


# test dataset
class DroneTestDataset(Dataset):

    def __init__(self, img_path, mask_path, X, transform=None):
        self.img_path = img_path
        self.mask_path = mask_path
        self.X = X
        self.transform = transform

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        img = cv2.imread(self.img_path + self.X[idx] + '.jpg')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mask = cv2.imread(self.mask_path + self.X[idx] + '.png', cv2.IMREAD_GRAYSCALE)

        if self.transform is not None:
            aug = self.transform(image=img, mask=mask)
            img = Image.fromarray(aug['image'])
            mask = aug['mask']

        if self.transform is None:
            img = Image.fromarray(img)

        mask = torch.from_numpy(mask).long()

        return img, mask


t_test = A.Resize(512, 768, interpolation=cv2.INTER_NEAREST)
test_set = DroneTestDataset(IMAGE_PATH, MASK_PATH, X_test, transform=t_test)


def predict_image_mask_miou(model, image, mask, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], device="cuda"):
    model.load_state_dict(torch.load(saved_path))
    model.eval()
    t = T.Compose([T.ToTensor(), T.Normalize(mean, std)])
    image = t(image)
    model.to(device);
    image = image.to(device)
    mask = mask.to(device)
    with torch.no_grad():
        image = image.unsqueeze(0)
        mask = mask.unsqueeze(0)

        output = model(image)
        score = mIoU(output, mask)
        masked = torch.argmax(output, dim=1)
        masked = masked.cpu().squeeze(0)
    return masked, score


def predict_image_mask_pixel(model, image, mask, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], device="cuda"):
    model.load_state_dict(torch.load(saved_path))
    model.eval()
    t = T.Compose([T.ToTensor(), T.Normalize(mean, std)])
    image = t(image)
    model.to(device);
    image = image.to(device)
    mask = mask.to(device)
    with torch.no_grad():
        image = image.unsqueeze(0)
        mask = mask.unsqueeze(0)

        output = model(image)
        acc = pixel_accuracy(output, mask)
        masked = torch.argmax(output, dim=1)
        masked = masked.cpu().squeeze(0)
    return masked, acc


image, mask = test_set[3]
pred_mask, score = predict_image_mask_miou(model, image, mask)


def miou_score(model, test_set):
    model.load_state_dict(torch.load(saved_path))
    model.eval()
    score_iou = []
    for i in tqdm(range(len(test_set))):
        img, mask = test_set[i]
        pred_mask, score = predict_image_mask_miou(model, img, mask)
        score_iou.append(score)
    return score_iou


mob_miou = miou_score(model, test_set)


def pixel_acc(model, test_set):
    model.load_state_dict(torch.load(saved_path))
    model.eval()
    accuracy = []
    for i in tqdm(range(len(test_set))):
        img, mask = test_set[i]
        pred_mask, acc = predict_image_mask_pixel(model, img, mask)
        accuracy.append(acc)
    return accuracy


mob_acc = pixel_acc(model, test_set)


fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(20,10))
ax1.imshow(image)
ax1.set_title('Picture');

ax2.imshow(mask)
ax2.set_title('Ground truth')
ax2.set_axis_off()

ax3.imshow(pred_mask)
ax3.set_title('SwinUNet | mIoU {:.3f}'.format(score))
ax3.set_axis_off()

plt.show()



print('Test Set mIoU', np.mean(mob_miou))
print('Test Set Pixel Accuracy', np.mean(mob_acc))