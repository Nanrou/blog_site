# python日常碎碎念--PIL

昨天在处理网站相关图片的时候，发现图片都大小不一样，虽然一下就能想起PIL这个库，但是用法却不记得了。

简单记录一下用法。

可以直接用 Image.open 来打开图片，PIL库为这个文件对象提供了各种属性和方法。

```python
from PIL import Image

img = Image.open('picture')

w, h = img.size

img = img.resize((w, h))

img.save('picture')

img.close()
```

以上就是把图片重新设定了尺寸。

然后廖大的教程里提到了一个生成简单验证码的方法，原文在这里：[点我](http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/00140767171357714f87a053a824ffd811d98a83b58ec13000)

```python
from PIL import Image, ImageFont, ImageFilter, ImageDraw
import random

def rnd_char():
    return chr(random.randint(65, 90))
    
def rndColor():
    return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255)) 

def rndColor2():
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127)) 

width = 60 * 4
height = 60
image = Image.new('RGB', (width, height), (255, 255, 255))

font = ImageFont.truetype('Arial.ttf', 36)
draw = ImageDraw.Draw(image)

for x in range(width):
    for y in range(height):
        draw.point((x, y), fill=rndColor())
        
for t in range(4):
    draw.text((60 * t + 10, 10), rnd_char(), font = font, fill=rndColor2())
    

image = image.filter(ImageFilter.BLUR)
image.save('code.jpg', 'jpeg')
```

