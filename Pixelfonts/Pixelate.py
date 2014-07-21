#MenuTitle: Pixelate
# -*- coding: utf-8 -*-
__doc__="""
Turns outline glyphs into pixel glyphs by inserting pixel components, resetting widths and moving outlines to the background.
"""

import vanilla
import GlyphsApp

class Pixelate( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 250
		windowHeight = 150
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Pixelate", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.Pixelate.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15-1, 12+2, 140, 14), "Pixel grid step", sizeStyle='small' )
		self.w.text_2 = vanilla.TextBox( (15-1, 12+26, 140, 14), "Pixel component name", sizeStyle='small' )
		self.w.pixelRasterWidth = vanilla.EditText( (140+10, 12, -15, 15+4), "50", sizeStyle = 'small')
		self.w.pixelComponentName = vanilla.EditText( (140+10, 12+24, -15, 15+4), "pixel", sizeStyle = 'small', callback=self.EnableButton )
		self.w.resetWidths = vanilla.CheckBox( (15, 12+52, -15, 20), "Snap widths to pixel grid", value=False, callback=self.SavePreferences, sizeStyle='small' )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-120-15, -20-15, -15, -15), "Insert Pixels", sizeStyle='regular', callback=self.PixelateMain )
		self.w.setDefaultButton( self.w.runButton )
		self.EnableButton(None)
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Pixelate' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.Pixelate.pixelComponentName"] = self.w.pixelComponentName.get()
			Glyphs.defaults["com.mekkablue.Pixelate.pixelRasterWidth"] = self.w.pixelRasterWidth.get()
			Glyphs.defaults["com.mekkablue.Pixelate.resetWidths"] = self.w.resetWidths.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.pixelComponentName.set( Glyphs.defaults["com.mekkablue.Pixelate.pixelComponentName"] )
			self.w.pixelRasterWidth.set( Glyphs.defaults["com.mekkablue.Pixelate.pixelRasterWidth"] )
			self.w.resetWidths.set( Glyphs.defaults["com.mekkablue.Pixelate.resetWidths"] )
		except:
			return False
			
		return True
	
	def EnableButton( self, sender ):
		"""
		Checks if the pixel component entered by the user actually exists,
		and enables/disables the Run button accordingly.
		"""
		onOff = False
		pixelNameEntered = str(self.w.pixelComponentName.get())
		currentGlyphNames = [g.name for g in Glyphs.font.glyphs] # glyph names of frontmost font
		if pixelNameEntered in currentGlyphNames:
			onOff = True
		self.w.runButton.enable(onOff)

	def PixelateMain( self, sender ):
		try:
			thisFont = Glyphs.font # frontmost font
			listOfSelectedLayers = thisFont.selectedLayers # active layers of currently selected glyphs
			pixelRasterWidth = float(self.w.pixelRasterWidth.get())
			pixelNameEntered = str(self.w.pixelComponentName.get())
			pixel = thisFont.glyphs[pixelNameEntered]
			widthsShouldBeReset = self.w.resetWidths.get()
			
			for thisLayer in listOfSelectedLayers: # loop through layers
				thisGlyph = thisLayer.parent
				
				if len(thisLayer.paths) > 0:
					
					# get all possible pixel positions within layer bounds:
					thisLayerBezierPath = thisLayer.bezierPath() # necessary for containsPoint_() function
					layerBounds = thisLayer.bounds
					xStart = int(round( layerBounds.origin.x / pixelRasterWidth ))
					yStart = int(round( layerBounds.origin.y / pixelRasterWidth ))
					xIterations = int(round( layerBounds.size.width / pixelRasterWidth ))
					yIterations = int(round( layerBounds.size.height / pixelRasterWidth ))
					pixelCount = 0

					# move current layer to background and clean foreground:
					thisLayer.clearBackground()
					try: # circumvent typo in API:
						thisLayer.swapForgroundWithBackground()
					except:
						thisLayer.swapForegroundWithBackground()
					
					# snap width to pixel grid:
					widthReport = ""
					if widthsShouldBeReset:
						originalWidth = thisLayer.width
						pixelatedWidth = round( originalWidth / pixelRasterWidth ) * pixelRasterWidth
						thisLayer.setWidth_( pixelatedWidth )
						if originalWidth != thisLayer.width: # only if it really changed
							widthReport = ", snapped width to %.1f" % pixelatedWidth
					
					for x in range(xStart, xStart + xIterations):
						for y in range( yStart, yStart + yIterations):
							# if the pixel center is black, insert a pixel component here:
							pixelCenter = NSPoint( (x+0.5) * pixelRasterWidth, (y+0.5) * pixelRasterWidth )
							print x, y
							if thisLayerBezierPath.containsPoint_( pixelCenter ):
								pixelCount += 1
								pixelComponent = GSComponent( pixel, NSPoint( x * pixelRasterWidth, y * pixelRasterWidth ) )
								thisLayer.addComponent_( pixelComponent )
					
					print "%s: added %i pixels to layer '%s'%s." % ( thisGlyph.name, pixelCount, thisLayer.name, widthReport )
				else:
					print "No paths in '%s' (layer '%s'), skipping." % ( thisGlyph.name, thisLayer.name )
			
			if not self.SavePreferences( self ):
				print "Note: 'Pixelate' could not write preferences."
			
			self.w.close() # delete if you want window to stay open
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Pixelate Error: %s" % e

Pixelate()