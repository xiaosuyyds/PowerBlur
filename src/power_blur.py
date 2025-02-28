import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


def rounded_rectangle(
        image: Image,
        size: list[int, int, int, int] | tuple[int, int, int, int],
        radius: int = 100,
        color: list[int, int, int] | tuple[int, int, int] = (255, 255, 255),
        magnification: int = 4,
        copy: bool = False
):
    if copy:
        image = image.copy()

    # 创建一个圆形的单色图片
    circle = Image.new('L', (radius * 2 * magnification, radius * 2 * magnification), 0)

    # 绘制一个圆
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2 * magnification, radius * 2 * magnification), fill=255)

    # 缩放回正常大小
    circle = circle.resize(
        (radius * 2, radius * 2),
        Image.Resampling.LANCZOS)

    # 创建一个矩形蒙版
    mask = Image.new("RGBA", ((size[2] - size[0]), (size[3] - size[1])),
                     (color[0], color[1], color[2], 255))
    w, h = mask.size

    # 创建一个蒙版的alpha层，并将四个角替换为圆形
    mask_alpha = Image.new('L', mask.size, 255)
    mask_alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))  # 左上角
    mask_alpha.paste(circle.crop((radius, 0, radius * 2, radius)),
                     (w - radius, 0))  # 右上角
    mask_alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)),
                     (w - radius, h - radius))  # 右下角
    mask_alpha.paste(circle.crop((0, radius, radius, radius * 2)),
                     (0, h - radius))  # 左下角

    # 将圆角矩形蒙版粘贴到矩形蒙版上
    mask.putalpha(mask_alpha)

    image.paste(mask, (size[0], size[1]), mask)

    # 以前效率很低的实现（速度相差约5倍）
    # mask = Image.new("RGBA", ((size[2] - size[0]) * magnification,
    #                           (size[3] - size[1]) * magnification), (255, 255, 255, 0))
    #
    # draw = ImageDraw.Draw(mask)
    # draw.rounded_rectangle(
    #     (0, 0, mask.size[0], mask.size[1]),
    #     radius=radius * magnification,
    #     fill=color
    # )
    # mask = mask.resize(
    #     (mask.size[0] // magnification, mask.size[1] // magnification),
    #
    #     Image.Resampling.LANCZOS)
    # image.paste(mask, (size[0], size[1]), mask)
    return image


def power_blur(
        image: Image,
        size: list[int, int, int, int] | tuple[int, int, int, int],
        radius: int = 25,
        mask_fill: list[int, int, int] | tuple[int, int, int] = (255, 255, 255),
        mask_alpha: int = 100,
        outline_fill: list[int, int, int] | tuple[int, int, int] = (0, 0, 0),
        outline_width: int = 5,
        outline_alpha: int = 128,
        noise_mean: float = 0.03,
        noise_std: float = 10,
        sigma: float = 5,
        exposure: float = 1,
        saturation: float = 1,
        copy: bool = False
):
    """
    为图片添加有毛玻璃效果的圆角矩形
    tips: 边框功能还在开发中，目前的边框可能会有些瑕疵
    :param image: 图片
    :param radius: 圆角半径
    :param size: 矩形的坐标(x1,y1,x2,y2)
    :param mask_fill: 蒙版颜色(R,G,B)
    :param mask_alpha: 蒙版透明度(0~255)
    :param outline_fill: 边框颜色(R,G,B)
    :param outline_width: 边框宽度
    :param outline_alpha: 边框透明度(0~255)
    :param noise_mean: 高斯噪声均值(0~255)
    :param noise_std: 高斯噪声标准差
    :param sigma: 高斯模糊参数
    :param exposure: 曝光度(0~10)
    :param saturation: 饱和度
    :param copy: 是否复制一份原始图片（不修改原图）
    """

    if copy:
        image = image.copy()
    base_image = image

    # 计算遮罩的宽度和高度
    width_mask, height_mask = size[2] - size[0], size[3] - size[1]

    # 裁剪图像到指定区域，并转换为 RGBA 格式
    crop_image = image.crop(
        (size[0], size[1],
         size[2], size[3])
    ).convert('RGBA')

    # 应用高斯模糊
    crop_image = crop_image.filter(ImageFilter.GaussianBlur(radius=sigma))

    # 调整饱和度
    if saturation != 1:
        crop_image = ImageEnhance.Color(crop_image).enhance(saturation)

    # 调整亮度
    if exposure != 1:
        crop_image = ImageEnhance.Brightness(crop_image).enhance(exposure)

    # 添加高斯噪声
    if noise_std > 0:
        # 生成高斯噪声
        noise = np.random.normal(loc=noise_mean, scale=noise_std,
                                 size=(height_mask, width_mask))

        # 归一化噪声到 [0, 255]，并限制到合法范围
        noise = np.clip(noise, 0, 255).astype(np.uint8)

        zero = np.zeros((height_mask, width_mask), dtype=np.uint8)

        # 合成 RGBA 图像（R=G=B=噪声, A=透明度）
        rgba_image = np.stack([zero, zero, zero, noise], axis=-1)

        # 转换为 PIL Image
        noise_img = Image.fromarray(rgba_image, mode="RGBA")

        # 将噪声图像与裁剪图像合并
        crop_image = Image.alpha_composite(crop_image, noise_img)

    # 添加白色遮罩
    if mask_alpha > 0:
        # 创建白色遮罩图像
        white_mask = Image.new("RGBA", (width_mask, height_mask),
                               (mask_fill[0], mask_fill[1], mask_fill[2], mask_alpha))
        # 将裁剪图像与白色遮罩合并
        crop_image = Image.alpha_composite(crop_image, white_mask)

    # 创建圆角矩形遮罩
    if radius > 0:
        crop_image_mask = Image.new(
            "RGBA", (width_mask, height_mask), (255, 255, 255, 0))
        rounded_rectangle(crop_image_mask, (0, 0, width_mask, height_mask), radius)

        # 将圆角矩形遮罩粘贴到裁剪图像上
        new_crop = Image.new(
            "RGBA", (width_mask, height_mask), (255, 255, 255, 0)
        )
        new_crop.paste(crop_image, (0, 0), crop_image_mask)
        crop_image = new_crop

    # 计算描边
    if outline_alpha > 0 and outline_width > 0:
        outline_image = Image.new(
            "RGBA", (width_mask + outline_width * 2, height_mask + outline_width * 2),
            (outline_fill[0], outline_fill[1], outline_fill[2], outline_alpha)
        )
        outline_image.alpha_composite(crop_image, (outline_width, outline_width))
        # 对描边进行圆角
        outline_image_mask = Image.new(
            "RGBA", (width_mask + outline_width * 2, height_mask + outline_width * 2),
            (255, 255, 255, 0)
        )
        # 创建圆角遮罩（并计算 radius 的修正值，就是这里有点问题，因为浮点数和 int 的转换会有误差，不过也可能是我计算方法的问题，反正看着就有点难受，之后肯定是要换一种描边计算方法的）
        rounded_rectangle(outline_image_mask, (0, 0, width_mask + outline_width * 2, height_mask + outline_width * 2),
                          round(radius * ((width_mask + height_mask + outline_width * 4) / (width_mask + height_mask))))
        new_outline = Image.new(
            "RGBA", (width_mask + outline_width * 2, height_mask + outline_width * 2),
            (255, 255, 255, 0)
        )
        new_outline.paste(outline_image, (0, 0), outline_image_mask)
        base_image.paste(new_outline, (size[0] - outline_width, size[1] - outline_width), new_outline)
    else:
        base_image.paste(crop_image, (size[0], size[1]), crop_image)

    # 返回处理后的图像
    return base_image


def blur(
        image: Image,
        size: list[int, int, int, int] | tuple[int, int, int, int],
        radius: int = 25,
        mask_fill: list[int, int, int] | tuple[int, int, int] = (
                255,
                255,
                255
        ),
        noise_mean: float = 0,
        noise_std: float = 0,
        mask_alpha: int = 0,
        outline_fill: list[int, int, int] | tuple[int, int, int] = (0, 0, 0),
        outline_width: int = 0,
        outline_alpha: int = 255,
        sigma: float = 5,
        exposure: float = 1.1,
        saturation: float = 1.1,
        copy: bool = False
):
    """
    Blur 毛玻璃效果
    为图片添加有毛玻璃效果的圆角矩形
    tips: 边框功能还在开发中，目前的边框可能会有些瑕疵
    :param image: 图片
    :param radius: 圆角半径
    :param size: 矩形的坐标(x1,y1,x2,y2)
    :param mask_fill: 蒙版颜色(R,G,B)
    :param mask_alpha: 蒙版透明度(0~255)
    :param outline_fill: 边框颜色(R,G,B)
    :param outline_width: 边框宽度
    :param outline_alpha: 边框透明度(0~255)
    :param noise_mean: 高斯噪声均值(0~255)
    :param noise_std: 高斯噪声标准差
    :param sigma: 高斯模糊参数
    :param exposure: 曝光度(0~10)
    :param saturation: 饱和度
    :param copy: 是否复制一份原始图片（不修改原图）
    """
    return power_blur(image, size, radius, mask_fill, mask_alpha, outline_fill, outline_width, outline_alpha,
                      noise_mean, noise_std, sigma, exposure, saturation, copy)


def aero(
        image: Image,
        size: list[int, int, int, int] | tuple[int, int, int, int],
        radius: int = 25,
        mask_fill: list[int, int, int] | tuple[int, int, int] = (
                255,
                255,
                255
        ),
        noise_mean: float = 0,
        noise_std: float = 0,
        mask_alpha: int = 0,
        outline_fill: list[int, int, int] | tuple[int, int, int] = (0, 0, 0),
        outline_width: int = 0,
        outline_alpha: int = 255,
        sigma: float = 5,
        exposure: float = 1.1,
        saturation: float = 1.1,
        copy: bool = False
):
    """
    Aero 毛玻璃效果
    为图片添加有毛玻璃效果的圆角矩形
    tips: 边框功能还在开发中，目前的边框可能会有些瑕疵
    :param image: 图片
    :param radius: 圆角半径
    :param size: 矩形的坐标(x1,y1,x2,y2)
    :param mask_fill: 蒙版颜色(R,G,B)
    :param mask_alpha: 蒙版透明度(0~255)
    :param outline_fill: 边框颜色(R,G,B)
    :param outline_width: 边框宽度
    :param outline_alpha: 边框透明度(0~255)
    :param noise_mean: 高斯噪声均值(0~255)
    :param noise_std: 高斯噪声标准差
    :param sigma: 高斯模糊参数
    :param exposure: 曝光度(0~10)
    :param saturation: 饱和度
    :param copy: 是否复制一份原始图片（不修改原图）
    """
    return power_blur(image, size, radius, mask_fill, mask_alpha, outline_fill, outline_width, outline_alpha,
                      noise_mean, noise_std, sigma, exposure, saturation, copy)


def acrylic(
        image: Image,
        size: list[int, int, int, int] | tuple[int, int, int, int],
        radius: int = 25,
        mask_fill: list[int, int, int] | tuple[int, int, int] = (
                255,
                255,
                255
        ),
        noise_mean: float = 0.03,
        noise_std: float = 10,
        mask_alpha: int = 45,
        outline_fill: list[int, int, int] | tuple[int, int, int] = (0, 0, 0),
        outline_width: int = 5,
        outline_alpha: int = 200,
        sigma: float = 5,
        exposure: float = 1,
        saturation: float = 1.1,
        copy: bool = False
):
    """
    亚克力Acrylic 毛玻璃效果
    为图片添加有毛玻璃效果的圆角矩形
    tips: 边框功能还在开发中，目前的边框可能会有些瑕疵
    :param image: 图片
    :param radius: 圆角半径
    :param size: 矩形的坐标(x1,y1,x2,y2)
    :param mask_fill: 蒙版颜色(R,G,B)
    :param mask_alpha: 蒙版透明度(0~255)
    :param outline_fill: 边框颜色(R,G,B)
    :param outline_width: 边框宽度
    :param outline_alpha: 边框透明度(0~255)
    :param noise_mean: 高斯噪声均值(0~255)
    :param noise_std: 高斯噪声标准差
    :param sigma: 高斯模糊参数
    :param exposure: 曝光度(0~10)
    :param saturation: 饱和度
    :param copy: 是否复制一份原始图片（不修改原图）
    """
    return power_blur(image, size, radius, mask_fill, mask_alpha, outline_fill, outline_width, outline_alpha,
                      noise_mean, noise_std, sigma, exposure, saturation, copy)


def mica(
        image: Image,
        size: list[int, int, int, int] | tuple[int, int, int, int],
        radius: int = 25,
        mask_fill: list[int, int, int] | tuple[int, int, int] = (
                255,
                255,
                255
        ),
        noise_mean: float = 0,
        noise_std: float = 0,
        mask_alpha: int = 200,
        outline_fill: list[int, int, int] | tuple[int, int, int] = (0, 0, 0),
        outline_width: int = 5,
        outline_alpha: int = 255,
        sigma: float = 5,
        exposure: float = 1,
        saturation: float = 1.1,
        copy: bool = False
):
    """
    云母Mica 毛玻璃效果
    为图片添加有毛玻璃效果的圆角矩形
    tips: 边框功能还在开发中，目前的边框可能会有些瑕疵
    :param image: 图片
    :param radius: 圆角半径
    :param size: 矩形的坐标(x1,y1,x2,y2)
    :param mask_fill: 蒙版颜色(R,G,B)
    :param mask_alpha: 蒙版透明度(0~255)
    :param outline_fill: 边框颜色(R,G,B)
    :param outline_width: 边框宽度
    :param outline_alpha: 边框透明度(0~255)
    :param noise_mean: 高斯噪声均值(0~255)
    :param noise_std: 高斯噪声标准差
    :param sigma: 高斯模糊参数
    :param exposure: 曝光度(0~10)
    :param saturation: 饱和度
    :param copy: 是否复制一份原始图片（不修改原图）
    """
    return power_blur(image, size, radius, mask_fill, mask_alpha, outline_fill, outline_width, outline_alpha,
                      noise_mean, noise_std, sigma, exposure, saturation, copy)
