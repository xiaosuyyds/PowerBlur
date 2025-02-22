import threading
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


class RoundedRectangle:
    """
    圆角矩形，但是抗锯齿
    """

    def __init__(self,
                 image: Image,
                 size: list[int, int, int, int] | tuple[int, int, int, int],
                 radius: int = 100,
                 color: list[int, int, int] | tuple[int, int, int] = (255, 255, 255),
                 magnification: int = 4,
                 ):
        self.color = color
        self.image = image
        self.size = size
        self.radius = radius
        self.magnification = magnification
        self.mask = Image.new("RGBA", ((size[2] - size[0])*self.magnification,
                                       (size[3] - size[1])*self.magnification), (255, 255, 255, 0))

    def draw(self):
        draw = ImageDraw.Draw(self.mask)
        draw.rounded_rectangle(
            (0, 0, self.mask.size[0], self.mask.size[1]),
            radius=self.radius*self.magnification,
            fill=self.color
        )
        self.mask = self.mask.resize(
            (self.mask.size[0] // self.magnification, self.mask.size[1] // self.magnification),
            Image.Resampling.LANCZOS)
        self.image.paste(self.mask, (self.size[0], self.size[1]), self.mask)
        return self.image


class PowerBlur:
    def __init__(
            self,
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
            mask_alpha: int = 100,
            sigma: float = 5,
            exposure: float = 1,
            saturation: float = 1
    ):
        """
        为图片添加有毛玻璃效果的圆角矩形
        :param image: 图片
        :param radius: 圆角半径
        :param size: 矩形的坐标(x1,y1,x2,y2)
        :param mask_fill: 蒙版颜色(R,G,B)
        :param noise_mean: 高斯噪声均值(0~255)
        :param noise_std: 高斯噪声标准差
        :param mask_alpha: 蒙版透明度(0~255)
        :param sigma: 高斯模糊参数
        :param exposure: 曝光度(0~10)
        :param saturation: 饱和度
        """

        self.image = image
        self.width_mask, self.height_mask = size[2] - size[0], size[3] - size[1]
        self.radius = radius
        self.size = size
        self.mask_fill = mask_fill
        self.noise_mean = noise_mean
        self.noise_std = noise_std
        self.mask_alpha = mask_alpha
        self.sigma = sigma

        self.exposure = exposure
        self.saturation = saturation

    # 绘制图片
    def draw(self):
        # 生成高斯噪声和颜色蒙版
        def create_noise_mask():
            if self.noise_std > 0:
                # 生成高斯噪声
                noise = np.random.normal(loc=self.noise_mean, scale=self.noise_std,
                                         size=(self.height_mask, self.width_mask))

                # 归一化噪声到 [0, 255]，并限制到合法范围
                noise = np.clip(noise, 0, 255).astype(np.uint8)

                zero = np.zeros((self.height_mask, self.width_mask), dtype=np.uint8)

                # 合成 RGBA 图像（R=G=B=噪声, A=透明度）
                rgba_image = np.stack([zero, zero, zero, noise], axis=-1)

                # 转换为 PIL Image
                img = Image.fromarray(rgba_image, mode="RGBA")
            else:
                img = Image.new("RGBA", (self.width_mask, self.height_mask), (255, 255, 255, 0))

            return img

        # 生成圆角矩形蒙版
        def create_rounded_mask():
            image1_mask = Image.new(
                "RGBA", (self.width_mask, self.height_mask), (255, 255, 255, 0))
            # mask_draw = ImageDraw.Draw(image1_mask, "RGBA")
            # mask_draw.rounded_rectangle(
            #     (0, 0, self.width_mask, self.height_mask), radius=self.radius, fill=(
            #         255, 255, 255, 255))
            RoundedRectangle(image1_mask, (0, 0, self.width_mask, self.height_mask), self.radius).draw()
            return image1_mask

        # 对图片进行高斯模糊
        def composite():
            image1 = self.image.crop(
                (self.size[0], self.size[1],
                 self.size[2], self.size[3])
            ).convert('RGBA')
            image1 = image1.filter(ImageFilter.GaussianBlur(radius=self.sigma))
            return image1

        class MyThread(threading.Thread):
            def __init__(self, func, args=()):
                """
                :param func: 可调用的对象
                :param args: 可调用对象的参数
                """
                threading.Thread.__init__(self)
                self.func = func
                self.args = args
                self.result = None

            def run(self):
                self.result = self.func(*self.args)

            def get_result(self):
                return self.result

        # 执行三个函数
        t1 = MyThread(composite)
        t2 = MyThread(create_noise_mask)
        t3 = MyThread(create_rounded_mask)
        # 启动线程
        t1.start()
        if self.noise_std > 0:
            t2.start()
        if self.radius > 0:
            t3.start()

        if self.mask_alpha > 0:
            white_mask = Image.new("RGBA", (self.width_mask, self.height_mask),
                                   (self.mask_fill[0], self.mask_fill[1], self.mask_fill[2], self.mask_alpha))

        # 等待线程结束
        t1.join()

        image1 = t1.get_result()

        if self.saturation != 1:
            image1 = ImageEnhance.Color(image1).enhance(self.saturation)

        if self.exposure != 1:
            image1 = ImageEnhance.Brightness(image1).enhance(self.exposure)

        if self.noise_std > 0:
            t2.join()
            res = t2.get_result()
            image1 = Image.alpha_composite(image1, res)

        if self.mask_alpha > 0:
            image1 = Image.alpha_composite(image1, white_mask)

        if self.radius > 0:
            t3.join()
            image1_mask = t3.get_result()
            self.image.paste(image1, (self.size[0], self.size[1]), image1_mask)
        else:
            self.image.paste(image1, (self.size[0], self.size[1]))

        return self.image


class Blur(PowerBlur):
    def __init__(self,
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
                 sigma: float = 5,
                 exposure: float = 1.1,
                 saturation: float = 1.1
                 ):
        """
        Blur 毛玻璃效果
        为图片添加有毛玻璃效果的圆角矩形
        :param image: 图片
        :param radius: 圆角半径
        :param size: 矩形的坐标(x1,y1,x2,y2)
        :param mask_fill: 蒙版颜色(R,G,B)
        :param noise_mean: 高斯噪声均值(0~255)
        :param noise_std: 高斯噪声标准差
        :param mask_alpha: 蒙版透明度(0~255)
        :param sigma: 高斯模糊参数
        :param exposure: 曝光度(0~10)
        :param saturation: 饱和度
        """
        super().__init__(image, size, radius, mask_fill, noise_mean, noise_std, mask_alpha, sigma, exposure, saturation)


class Aero(PowerBlur):
    def __init__(self,
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
                 sigma: float = 5,
                 exposure: float = 1.1,
                 saturation: float = 1.1
                 ):
        """
        Aero 毛玻璃效果
        为图片添加有毛玻璃效果的圆角矩形
        :param image: 图片
        :param radius: 圆角半径
        :param size: 矩形的坐标(x1,y1,x2,y2)
        :param mask_fill: 蒙版颜色(R,G,B)
        :param noise_mean: 高斯噪声均值(0~255)
        :param noise_std: 高斯噪声标准差
        :param mask_alpha: 蒙版透明度(0~255)
        :param sigma: 高斯模糊参数
        :param exposure: 曝光度(0~10)
        :param saturation: 饱和度
        """
        super().__init__(image, size, radius, mask_fill, noise_mean, noise_std, mask_alpha, sigma, exposure, saturation)


class Acrylic(PowerBlur):
    def __init__(self,
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
                 sigma: float = 5,
                 exposure: float = 1,
                 saturation: float = 1.1
                 ):
        """
        亚克力Acrylic 毛玻璃效果
        为图片添加有毛玻璃效果的圆角矩形
        :param image: 图片
        :param radius: 圆角半径
        :param size: 矩形的坐标(x1,y1,x2,y2)
        :param mask_fill: 蒙版颜色(R,G,B)
        :param noise_mean: 高斯噪声均值(0~255)
        :param noise_std: 高斯噪声标准差
        :param mask_alpha: 蒙版透明度(0~255)
        :param sigma: 高斯模糊参数
        :param exposure: 曝光度(0~10)
        :param saturation: 饱和度
        """
        super().__init__(image, size, radius, mask_fill, noise_mean, noise_std, mask_alpha, sigma, exposure, saturation)


class Mica(PowerBlur):
    def __init__(self,
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
                 mask_alpha: int = 230,
                 sigma: float = 5,
                 exposure: float = 1,
                 saturation: float = 1.1
                 ):
        """
        云母Mica 毛玻璃效果
        为图片添加有毛玻璃效果的圆角矩形
        :param image: 图片
        :param radius: 圆角半径
        :param size: 矩形的坐标(x1,y1,x2,y2)
        :param mask_fill: 蒙版颜色(R,G,B)
        :param noise_mean: 高斯噪声均值(0~255)
        :param noise_std: 高斯噪声标准差
        :param mask_alpha: 蒙版透明度(0~255)
        :param sigma: 高斯模糊参数
        :param exposure: 曝光度(0~10)
        :param saturation: 饱和度
        """
        super().__init__(image, size, radius, mask_fill, noise_mean, noise_std, mask_alpha, sigma, exposure, saturation)
