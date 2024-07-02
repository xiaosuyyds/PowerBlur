import threading
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


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
            noise_num: float = 0.03,
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
        :param noise_num: 高斯噪声量(0~1)
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
        self.noise_num = noise_num
        self.mask_alpha = mask_alpha
        self.sigma = sigma
        self.exposure = exposure
        self.saturation = saturation

    # 绘制图片
    def draw(self):
        # 生成高斯噪声和白色蒙版
        def create_white_mask():
            if self.noise_num <= 0:
                white_mask = Image.new("RGB", (self.width_mask, self.height_mask), self.mask_fill)
            else:
                img = np.full((self.height_mask, self.width_mask, 3), self.mask_fill, dtype=np.uint8)
                noise = np.random.normal(0, self.noise_num, img.shape)
                gaussian_out = np.clip(img + noise, 0, 255).astype(np.uint8)
                white_mask = Image.fromarray(gaussian_out)

            white_mask.putalpha(self.mask_alpha)
            return white_mask

        # 生成圆角矩形蒙版
        def create_rounded_mask():
            image1_mask = Image.new(
                "RGBA", (self.width_mask, self.height_mask), (255, 255, 255, 0))
            mask_draw = ImageDraw.Draw(image1_mask, "RGBA")
            mask_draw.rounded_rectangle(
                (0, 0, self.width_mask, self.height_mask), radius=self.radius, fill=(
                    255, 255, 255, 255))
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
        t2 = MyThread(create_white_mask)
        t3 = MyThread(create_rounded_mask)
        # 启动线程
        t1.start()
        if self.mask_alpha > 0:
            t2.start()
        if self.radius > 0:
            t3.start()

        # 等待线程结束
        t1.join()

        image1 = t1.get_result()

        if self.saturation != 1:
            image1 = ImageEnhance.Color(image1).enhance(self.saturation)

        if self.exposure != 1:
            image1 = ImageEnhance.Brightness(image1).enhance(self.exposure)

        if self.mask_alpha > 0:
            t2.join()
            image1 = Image.alpha_composite(image1, t2.get_result())

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
                 noise_num: float = 0,
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
        :param noise_num: 高斯噪声量(0~1)
        :param mask_alpha: 蒙版透明度(0~255)
        :param sigma: 高斯模糊参数
        :param exposure: 曝光度(0~10)
        :param saturation: 饱和度
        """
        super().__init__(image, size, radius, mask_fill, noise_num, mask_alpha, sigma, exposure, saturation)


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
                 noise_num: float = 0.03,
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
        :param noise_num: 高斯噪声量(0~1)
        :param mask_alpha: 蒙版透明度(0~255)
        :param sigma: 高斯模糊参数
        :param exposure: 曝光度(0~10)
        :param saturation: 饱和度
        """
        super().__init__(image, size, radius, mask_fill, noise_num, mask_alpha, sigma, exposure, saturation)


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
                 noise_num: float = 0.03,
                 mask_alpha: int = 100,
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
        :param noise_num: 高斯噪声量(0~1)
        :param mask_alpha: 蒙版透明度(0~255)
        :param sigma: 高斯模糊参数
        :param exposure: 曝光度(0~10)
        :param saturation: 饱和度
        """
        super().__init__(image, size, radius, mask_fill, noise_num, mask_alpha, sigma, exposure, saturation)


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
                 noise_num: float = 0,
                 mask_alpha: int = 150,
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
        :param noise_num: 高斯噪声量(0~1)
        :param mask_alpha: 蒙版透明度(0~255)
        :param sigma: 高斯模糊参数
        :param exposure: 曝光度(0~10)
        :param saturation: 饱和度
        """
        super().__init__(image, size, radius, mask_fill, noise_num, mask_alpha, sigma, exposure, saturation)
