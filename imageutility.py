from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import wx


def WxBitmapToPilImage( myBitmap ) :
    return WxImageToPilImage( WxBitmapToWxImage( myBitmap ) )


def WxBitmapToWxImage( myBitmap ) :
    return wx.Bitmap.ConvertToImage ( myBitmap )


def WxImageToPilImage( myWxImage ):
    myPilImage = Image.new( 'RGB', (myWxImage.GetWidth(), myWxImage.GetHeight()) )
    myPilImage.frombytes( bytes(myWxImage.GetData()) )
    return myPilImage


def PIL2wx (image):
    width, height = image.size
    return wx.Bitmap.FromBuffer(width, height, image.convert("RGB").tobytes())


def wx2PIL(bitmap):
    return WxBitmapToPilImage(bitmap)

