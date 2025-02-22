# PowerBlur

| English | [简体中文](https://github.com/xiaosuyyds/PowerBlur/blob/master/README_ZH.md) |

## 📖 Introduction

PowerBlur is an image blurring tool based on Pillow, offering a high degree of freedom. It can achieve effects similar to the frosted glass effect found in systems like Windows/Mac (?). 

## ⬇️ Installation

#### Make sure to use version 0.0.3 or higher; otherwise, it might not function properly.

```bash
pip install PowerBlur
```

## 🧑‍💻 Usage

### Example Code
```python
from PIL import Image
import PowerBlur

# Load the image
image = Image.open("image.jpg")

# Get image size
width, height = image.size

# Create a blur processing object
blur = PowerBlur.PowerBlur(image, (int(width*0.1), int(height*0.1), int(width*0.9), int(height*0.9)))

# Apply the blur effect
blurred_image = blur.draw()

# Save the blurred image
blurred_image.save("output.jpg")
```

### Parameter Explanation

| Parameter  | Required/Default Value          | Type       | Description                                                           |
|------------|---------------------------------|------------|-----------------------------------------------------------------------|
| image      | ✔️                              | Image      | The image to be processed                                             |
| size       | ✔️                              | tuple/list | The area of the image to be processed, in the format (x1, y1, x2, y2) |
| radius     | ❌ (default is 25)               | int        | Corner radius; 0 means no corner radius                               |
| mask_fill  | ❌ (default is (255, 255, 255))  | tuple/list | Mask color (R, G, B)                                                  |
| mask_alpha | ❌ (default is 100)              | int        | Mask opacity (0~255); 0 is fully opaque, 100 is fully transparent     |
| noise_mean | ❌ (default is 0.03)             | float      | Gaussian noise mean (0~255)                                           |
| noise_std  | ❌ (default is 10)               | float      | Gaussian noise standard deviation; 0 means no noise                   |
| sigma      | ❌ (default is 5)                | float      | Gaussian blur parameter; 0 means no blur                              |
| exposure   | ❌ (default is 1)                | float      | Exposure (0~10); 0 means no exposure                                  |
| saturation | ❌ (default is 1)                | float      | Saturation; 0 means no saturation                                     |

### Concerned about configuring all these parameters? We’ve prepared some presets for you.

| Preset Name | Chinese Name | Formula                                                                  |
|-------------|--------------|--------------------------------------------------------------------------|
| PowerBlur   |              | The default one; nothing much to say, but the author finds it quite nice |
| Blur        |              | Basic blur effect, nothing special                                       |
| Aero        |              | Windows 7 glass effect, with exposure and saturation effects             |
| Acrylic     | 亚克力          | Blur, overlay blend, saturation, color mask, noise texture               |
| Mica        | 云母           | Blur, saturation, color mask                                             |

## ✨ Effect Showcase

### Original Image
![image](https://cdn.jsdelivr.net/gh/xiaosuyyds/PowerBlur@master/test.jpg)

### Processed Image
![image](https://cdn.jsdelivr.net/gh/xiaosuyyds/PowerBlur@master/test_output.jpg)
