import sys
import tempfile
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageOps
import StringIO
import math


def hex_to_rgb(hex):
    assert len(hex) == 6
    return tuple(int(hex[pos:pos+2], 16)
            for pos in range(0,6,2))


FONT = PIL.ImageFont.truetype('potama.ttf', 50)


def paste(destination, source, box=(0, 0), mask=None, force=False):
    """"Pastes the source image into the destination image while using an
    alpha channel if available.

    :param destination: destination image
    :type destination:  PIL image object
    :param source: source image
    :type source: PIL image object
    :param box:

        The box argument is either a 2-tuple giving the upper left corner,
        a 4-tuple defining the left, upper, right, and lower pixel coordinate,
        or None (same as (0, 0)). If a 4-tuple is given, the size of the
        pasted image must match the size of the region.

    :type box: tuple
    :param mask: mask or None

    :type mask: bool or PIL image object
    :param force:

        With mask: Force the invert alpha paste or not.

        Without mask:

        - If ``True`` it will overwrite the alpha channel of the destination
          with the alpha channel of the source image. So in that case the
          pixels of the destination layer will be abandonned and replaced
          by exactly the same pictures of the destination image. This is mostly
          what you need if you paste on a transparant canvas.
        - If ``False`` this will use a mask when the image has an alpha
          channel. In this case pixels of the destination image will appear
          through where the source image is transparent.

    :type force: bool
    """
    # Paste on top
    if source == mask:
        if has_alpha(source):
            # invert_alpha = the transparant pixels of the destination
            if has_alpha(destination) and (destination.size == source.size
                    or force):
                invert_alpha = PIL.ImageOps.invert(get_alpha(destination))
                if invert_alpha.size != source.size:
                    # if sizes are not the same be careful!
                    # check the results visually
                    if len(box) == 2:
                        w, h = source.size
                        box = (box[0], box[1], box[0] + w, box[1] + h)
                    invert_alpha = invert_alpha.crop(box)
            else:
                invert_alpha = None
            # we don't want composite of the two alpha channels
            source_without_alpha = remove_alpha(source)
            # paste on top of the opaque destination pixels
            destination.paste(source_without_alpha, box, source)
            if invert_alpha != None:
                # the alpha channel is ok now, so save it
                destination_alpha = get_alpha(destination)
                # paste on top of the transparant destination pixels
                # the transparant pixels of the destination should
                # be filled with the color information from the source
                destination.paste(source_without_alpha, box, invert_alpha)
                # restore the correct alpha channel
                destination.putalpha(destination_alpha)
        else:
            destination.paste(source, box)
    elif mask:
        destination.paste(source, box, mask)
    else:
        destination.paste(source, box)
        if force and has_alpha(source):
            destination_alpha = get_alpha(destination)
            source_alpha = get_alpha(source)
            destination_alpha.paste(source_alpha, box)
            destination.putalpha(destination_alpha)


def create_rounded_rectangle(img, radius=20, opacity=0):
    #rounded_rectangle
    size = img.size
    im_x, im_y = size
    #cross
    cross = PIL.Image.new('L', size, 0)
    draw = PIL.ImageDraw.Draw(cross)
    draw.rectangle((radius, 0, im_x - radius, im_y), fill=opacity)
    draw.rectangle((0, radius, im_x, im_y - radius), fill=opacity)
    #corner
    factor = 2
    corner = PIL.Image.new('1', (factor * radius, factor * radius), 255)
    draw = PIL.ImageDraw.Draw(corner)
    draw.pieslice((0, 0, 2 * factor * radius, 2 * factor * radius),
        180, 270, fill=0)
    corner = corner.resize((radius, radius), PIL.Image.ANTIALIAS)
    #rounded rectangle
    rectangle = PIL.Image.new('1', (radius, radius), 0)
    rounded_rectangle = cross.copy()
    for index, angle in enumerate(range(4)):
        element = corner
        if index % 2:
            x = im_x - radius
            element = element.transpose(PIL.Image.FLIP_LEFT_RIGHT)
        else:
            x = 0
        if index < 2:
            y = 0
        else:
            y = im_y - radius
            element = element.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        paste(rounded_rectangle, element, (x, y))

    #rounded_rect = PIL.Image.eval(rounded_rectangle, lambda x: x)o
    rounded_rect = PIL.ImageOps.invert(rounded_rectangle)
    return PIL.Image.composite(img,
        rounded_rect.convert('RGB'), rounded_rect)


def create_image(name, with_hole=True):
    if with_hole:
        #heightmap2stl: 8 0
        fill = 'black'
        bg = 200
    else:
        #heightmap2stl: 8 0
        fill = 'white'
        bg = 127

    image = PIL.Image.new('RGBA', (300, 300), (0,0,0,0))
    draw = PIL.ImageDraw.Draw(image)
    text_size_x, text_size_y = draw.textsize(name, font=FONT)
    x,y = out_size = (text_size_x + 60, text_size_y + 30)
    imtext = PIL.Image.new("L", out_size, bg)
    drtext = PIL.ImageDraw.Draw(imtext)
    drtext.text((45, 15), name, font=FONT, fill=fill)
    h_r = 5
    hole_x = 25
    hole_y = int(y/2.0)
    drtext.ellipse((hole_x-h_r,hole_y-h_r, hole_x+h_r, hole_y+h_r), fill="black")
    imtext = create_rounded_rectangle(imtext, 20)
    #imtext.show()
    outfile = open('/tmp/out.png', 'w+')
    imtext.save(outfile, 'PNG')

if __name__ == "__main__":
    name = u' '.join([unicode(x.decode('utf8')) for x in sys.argv[1:]])
    create_image(name)

