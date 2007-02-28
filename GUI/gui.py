#!/usr/bin/env python
from __future__ import division 
import sys,os, os.path, PyMC2
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk, gobject
    import gtk.glade
except:
    sys.exit(1)
import re
handler_re = re.compile(r'(on|after)_(.*)_(.*)')
from threading import Thread

def progress_timeout(self):
    # Calculate the value of the progress bar 
    if self.model.sampling:
        i = min(max(self.model._current_iter,0), self.model._iter)
        self.pbar.set_fraction(i/(self.model._iter))    
    else:
        if self.model._current_iter < 0 : # Sampling is over 
            self.pbar.set_fraction(0.)
            self.button2.set_label('Start')
            self.button2.set_image(gtk.image_new_from_stock('gtk-yes', gtk.ICON_SIZE_BUTTON))
            return False
        
        else:    # Sampling is interrupted.
            return False
    # As this is a timeout function, return TRUE so that it
    # continues to get called
    return True

class GladeWidget:
    def __init__(self, glade_file, widget_name):
        """Connects signal handling methods to Glade widgets.

        Methods named like on_widget__signal or after_widget__signal
        are connected to the appropriate widgets and signals.
        """
        get_widget = gtk.glade.XML(glade_file, widget_name).get_widget
        W = {}
        for attr in dir(self):
            match = handler_re.match(attr)
            if match:
                when, widget, signal = match.groups()
                method = getattr(self, attr)
                assert callable(method)
                if when == 'on':
                    get_widget(widget).connect(signal, method)
                elif when == 'after':
                    get_widget(widget).connect_after(signal, method)
                W[widget]=get_widget(widget)
            elif attr.startswith('on_') or attr.startswith('after_'):
                # Warn about some possible typos like separating
                # widget and signal name with _ instead of __.
                print ('Warning: attribute %r not connected'
                       ' as a signal handler' % (attr,))
        self.__dict__.update(W)
        self.get_widget = get_widget

    def on_window1_destroy(self, widget):
        gtk.main_quit()

    def on_button1_clicked(self, widget):
        dialog = gtk.FileChooserDialog("Open python module",
            None,
            gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name("Python files")
        filter.add_pattern("*.py")
        dialog.add_filter(filter)
        dialog.set_filename(os.path.sep.join([os.environ['HOME'], 'science_svn', 'pymc', 'trial', 'PyMC2', 'examples', 'DisasterModel.py']))
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.filename= dialog.get_filename()
            self.modulename = os.path.splitext(os.path.basename(self.filename))[0]
            sys.path.append(os.path.dirname(self.filename))
            mod = __import__(self.modulename)
            self.model = PyMC2.Model(mod)

        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()
        self.button1.set_label(self.modulename)

    def on_spinbuttonit_changed(self, widget):
        pass

    def on_spinbuttonburn_changed(self, widget):
        pass

    def on_spinbuttonthin_changed(self, widget):
        pass

    def on_button2_clicked(self, widget):
        self.pbar = self.get_widget('progressbar1')
        # Not started, not sampling
        if not self.model.sampling:
            self.iter = int(self.spinbuttonit.get_value())
            self.burn = int(self.spinbuttonburn.get_value())
            self.thin = int(self.spinbuttonthin.get_value())
            self.pbar.set_fraction(0.0)
        
            self.T = Thread(target=self.model.sample, args=(self.iter, self.burn, self.thin))
            self.T.start()      

            self.timer = Thread(target=gobject.timeout_add, args= (100, progress_timeout, self))
            self.timer.start()
            self.model.sampling = True

            # Change label to stop
            widget.set_label('Stop')
            widget.set_image(gtk.image_new_from_stock('gtk-stop', gtk.ICON_SIZE_BUTTON))

        else:
            self.model.sampling = False
            widget.set_label('Continue')
            widget.set_image(gtk.image_new_from_stock('gtk-yes', gtk.ICON_SIZE_BUTTON))

    
if __name__ == "__main__":
    hwg = GladeWidget('gui.glade', 'window1')
    gtk.gdk.threads_init() 
    gtk.main()
