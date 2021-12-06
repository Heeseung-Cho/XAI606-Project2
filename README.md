# XAI606-Project2

## Training Result

### Accuracy
<img class="Acc" src="Result/Loss_total.png">

### Loss
<img class="Acc" src="Result/Acc_total.png">

### mIoU
<img class="Acc" src="Result/mIoU_total.png">

## Performance
||TransUNet|Swin UNet|UTNet|  
|:-----:|----|-------|-------|
|# of Parameters| 90.08M | 41.35M | **14.42M** | 
|FLOPs(GMac)| 68.48 | **49.49** | 123.12 |
|mIoU| 0.3971 | 0.3406 | **0.4947** |
|Pixel Acc| 0.8537 | 0.8043 | **0.8805** |

## Reference
UTNet, Swin Unet model: https://github.com/yhygao/UTNet
