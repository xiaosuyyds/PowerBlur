<h1 align="center">PowerBlur</h1>

| [English](https://github.com/xiaosuyyds/PowerBlur/blob/master/README.md) | 简体中文 |

## 📖介绍

PowerBlur是一个基于Pillow的图像模糊处理工具，自由度极高，能够实现类似win/Mac等系统的毛玻璃效果（？）

## ⬇️安装

#### 请务必使用0.0.3及以上版本，否则可能无法正常使用

```bash
pip install PowerBlur
```

## 🧑‍💻食用方法

### 示例代码
```python
from PIL import Image
import PowerBlur

# 加载图像
image = Image.open("image.jpg")

# 获取图片尺寸
width, height = image.size

# 应用模糊处理
PowerBlur.power_blur(image, (int(width*0.1), int(height*0.1), int(width*0.9), int(height*0.9)))

# 保存模糊处理后的图像
image.save("output.jpg")
```

### 参数说明

| 参数            | 是否必要/默认值              | 类型                             | 说明                            |
|---------------|-----------------------|--------------------------------|-------------------------------|
| image         | ✔️                    | Image                          | 需要处理的图像                       |
| size          | ✔️                    | tuple/list[int, int, int, int] | 需要处理的图像区域，格式为(x1, y1, x2, y2) |
| radius        | ❌（默认值25）              | int                            | 圆角尺寸，0即无圆角                    |
| mask_fill     | ❌（默认值(255, 255, 255)) | tuple/list[int, int, int]      | 蒙版颜色(R, G, B)                 |
| mask_alpha    | ❌（默认值100）             | int                            | 蒙版透明度（0~255），0即完全不透明，100即完全透明 |
| outline_fill  | ❌（默认值(0, 0, 0))       | tuple/list[int, int, int]      | 边框颜色(R, G, B)                 |
| outline_width | ❌（默认值5）               | int                            | 边框宽度                          |
| outline_alpha | ❌（默认值128）             | int                            | 边框透明度（0~255），0即完全透明，128即半透明   |
| noise_mean    | ❌（默认值0.03）            | float                          | 高斯噪声均值(0~255)                 |
| noise_std     | ❌（默认值10）              | float                          | 高斯噪声标准差，为0时无噪声                |
| sigma         | ❌（默认值5）               | float                          | 高斯模糊参数，0即无模糊                  |
| exposure      | ❌（默认值1）               | float                          | 曝光度（0~10），0即无曝光               |
| saturation    | ❌（默认值1）               | float                          | 饱和度，0即无饱和度                    |
| copy          | ❌（默认值False）           | bool                           | 是否复制一份原始图片（不修改原图）             |


### 担心这么多参数设置起来麻烦，我们为你准备了一些预设

| 预设名称       | 中文名称 | 配方                         |
|------------|------|----------------------------|
| power_blur |      | 默认的，没啥好说的吧……反正作者我觉得挺好看的    |
| blur       |      | 基础的模糊效果，没什么特别的             |
| aero       |      | Windows 7 的玻璃效果，具有曝光和饱和度效果 |
| acrylic    | 亚克力  | 模糊, 叠加混合, 饱和度, 颜色蒙版, 噪点纹理  |
| mica       | 云母   | 模糊, 饱和度, 颜色蒙版              |




## ✨效果展示

### 原始图片
![image](https://cdn.jsdelivr.net/gh/xiaosuyyds/PowerBlur@master/example.jpg)
### 处理后图片
![image](https://cdn.jsdelivr.net/gh/xiaosuyyds/PowerBlur@master/example_output.jpg)

## 许可证

版权所有 2025 Xiaosu。

根据 [Apache 2.0 许可证](https://github.com/xiaosuyyds/PowerBlur/blob/master/LICENSE) 的条款分发。
