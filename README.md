# PowerBlur

## 📖介绍

PowerBlur是一个基于Pillow的图像模糊处理工具，能够实现类似win/Mac等系统的毛玻璃效果。

## ⬇️安装


## 🧑‍💻食用方法

```python
import PowerBlur
from PIL import Image

# 加载图像
image = Image.open("image.jpg")

# 获取图片尺寸
width, height = image.size

# 创建模糊处理对象
blur = PowerBlur.PowerBlur(image, (int(width*0.1), int(height*0.1), int(width*0.9), int(height*0.9)))

# 模糊处理
blurred_image = blur.draw()

# 保存模糊处理后的图像
blurred_image.save("output.jpg")
```


## ✨效果展示