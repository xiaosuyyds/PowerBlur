from PIL import Image, ImageDraw, ImageFont
import PowerBlur

# 加载图像
image = Image.open("example.jpg")
font = ImageFont.truetype("PINGFANG BOLD.TTF", 30)

# 计算每一种预设展示位置以及坐标
w, h = image.size
size = int(w/3), int(h/2)  # 2行，3列

size1 = (int(size[0]*1+size[0]*0.1), int(size[1]*0+size[1]*0.1), int(size[0]*1+size[0]*0.9), int(size[1]*0+size[1]*0.9))
size2 = (int(size[0]*2+size[0]*0.1), int(size[1]*0+size[1]*0.1), int(size[0]*2+size[0]*0.9), int(size[1]*0+size[1]*0.9))
size3 = (int(size[0]*0+size[0]*0.1), int(size[1]*1+size[1]*0.1), int(size[0]*0+size[0]*0.9), int(size[1]*1+size[1]*0.9))
size4 = (int(size[0]*1+size[0]*0.1), int(size[1]*1+size[1]*0.1), int(size[0]*1+size[0]*0.9), int(size[1]*1+size[1]*0.9))
size5 = (int(size[0]*2+size[0]*0.1), int(size[1]*1+size[1]*0.1), int(size[0]*2+size[0]*0.9), int(size[1]*1+size[1]*0.9))
print(w, h)
print(size)
print(size1)
print(size2)
print(size3)
print(size4)
print(size5)

# 绘制
image = PowerBlur.PowerBlur(image, size1, sigma=25, radius=35).draw()
image = PowerBlur.Blur(image, size2, sigma=25, radius=35).draw()
image = PowerBlur.Aero(image, size3, sigma=25, radius=35).draw()
image = PowerBlur.Acrylic(image, size4, sigma=50, mask_fill=(0, 0, 0), radius=35).draw()
image = PowerBlur.Mica(image, size5, sigma=100, mask_fill=(32, 32, 32), radius=35).draw()

# 添加文字
draw = ImageDraw.Draw(image)
draw.text((int(size1[0]) + 12, int(size1[1])), "PowerBlur", font=font, fill=(0, 0, 0))
draw.text((int(size2[0]) + 12, int(size2[1])), "Blur", font=font, fill=(0, 0, 0))
draw.text((int(size3[0]) + 12, int(size3[1])), "Aero", font=font, fill=(0, 0, 0))
draw.text((int(size4[0]) + 12, int(size4[1])), "Acrylic", font=font, fill=(0, 0, 0))
draw.text((int(size5[0]) + 12, int(size5[1])), "Mica", font=font, fill=(0, 0, 0))

# 保存图像
image.save("example_output.jpg")
