# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DeactivateActiveLabels
                                 A QGIS plugin
 Deactivate or Active Labels from all layes
                              -------------------
        begin                : 2017-07-06
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Carlos Eduardo Cagna\ IBGE
        email                : carlos.cagna@ibge.gov.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from deactivate_active_labels_dialog import DeactivateActiveLabelsDialog
import os.path



class DeactivateActiveLabels:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DeactivateActiveLabels_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'DeactivateActiveLabels')
        self.toolbar.setObjectName(u'DeactivateActiveLabels')

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DeactivateActiveLabels', message)

        
    def createAction(self, icon_path, text, callback):
        action = QAction(
            QIcon(icon_path),
            text,
            self.iface.mainWindow())
        # connect the action to the run method
        action.setCheckable(True)
        action.toggled.connect(callback)
        return action            
        
    def createToolButton(self, parent, text):
        button = QToolButton(parent)
        button.setObjectName(text)
        button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        parent.addWidget(button)
        return button       

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference


        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        self.actions.append(action)

        return action
        
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        
        self.actionCriar = self.createAction(':/plugins/DeactivateActiveLabels/label.png',
                                            u"Deactivate/Active Labels (Select Layer)",
                                            self.run)
        self.tool = self.run 
        #QToolButtons
        self.activeButton = self.createToolButton(self.toolbar, u"Active Label(Select Layer)")
        self.activeButton.addAction(self.actionCriar)     
        self.activeButton.setDefaultAction(self.actionCriar)  
        layer = self.iface.activeLayer()
        if layer <> None:
            if layer.customProperty("labeling/enabled")== 'True':
                self.activeButton.setChecked(True)
        self.iface.currentLayerChanged['QgsMapLayer*'].connect(self.toggle)
        
        
        self.actionCriar = self.createAction(':/plugins/DeactivateActiveLabels/labels.png',
                                            u"Invert Actives Labels",
                                            self.run2)
        self.tool = self.run 
        #QToolButtons
        self.allButton = self.createToolButton(self.toolbar, u"Invert Actives Labels")    
        self.allButton.setDefaultAction(self.actionCriar)          
          
         
        
      
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Deactivate/Active Labels'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        if self.iface.activeLayer() <> None:
            layer = self.iface.activeLayer()       
            if layer.customProperty("labeling/enabled")== 'True' or layer.customProperty("labeling/enabled")== 'true':
                layer.setCustomProperty("labeling/enabled", False)
                self.activeButton.setChecked(False)            
                
            else :
                layer.setCustomProperty("labeling/enabled", 'True')
                self.activeButton.setChecked(True)  
            self.iface.mapCanvas().refresh()          
        else:
            self.activeButton.setChecked(False)
            
    def run2(self):
        """Run method that performs all the real work"""
        layers = self.iface.legendInterface()
        for layer in layers.layers():
            if layer.customProperty("labeling/enabled")== 'True' or layer.customProperty("labeling/enabled")== 'true':
                    layer.setCustomProperty("labeling/enabled", 'False')
                                    
            else :
                layer.setCustomProperty("labeling/enabled", 'True')
        
        self.toggle()
        self.allButton.setChecked(False)        
        self.iface.mapCanvas().refresh()              
    
    def toggle(self):
        mc = self.iface.mapCanvas()
        layer = mc.currentLayer()
        if layer is None:
            return
        if layer.customProperty("labeling/enabled")== 'True' or layer.customProperty("labeling/enabled")== 'true':
            self.activeButton.setChecked(True)
        else:
            self.activeButton.setChecked(False)
         
   
        