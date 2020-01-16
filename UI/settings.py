import sys

import inspect
from distutils.util import strtobool

from PyQt5 import QtCore
from PyQt5.QtWidgets import QComboBox,QLineEdit,QCheckBox,QRadioButton

#===================================================================
# restore "ui" controls with values stored in registry "settings"
# currently only handles comboboxes, editlines &checkboxes
# ui = QMainWindow object
# settings = QSettings object
#===================================================================


def save_settings(ui, settings):
    settings.setValue('size', ui.size())
    settings.setValue('pos', ui.pos())

    for name, obj in inspect.getmembers(ui):
      if isinstance(obj, QComboBox):
          name = obj.objectName()  # get combobox name
          index = obj.currentIndex()  # get current index from combobox
          text = obj.itemText(index)  # get the text for current index
          settings.setValue(name, text)  # save combobox selection to registry

      if isinstance(obj, QLineEdit):
          name = obj.objectName()
          value = obj.text()
          settings.setValue(name, value)  # save ui values, so they can be restored next time

      if isinstance(obj, QCheckBox):
          name = obj.objectName()
          state = obj.isChecked()
          settings.setValue(name, state)

      if isinstance(obj, QRadioButton):
          name = obj.objectName()
          value = obj.isChecked()  # get stored value from registry
          settings.setValue(name, value)


def load_settings(ui, settings):
  # Restore geometry
  ui.resize(settings.value('size', QtCore.QSize(500, 500)))
  ui.move(settings.value('pos', QtCore.QPoint(60, 60)))

  for name, obj in inspect.getmembers(ui):
      if isinstance(obj, QComboBox):
          index = obj.currentIndex()  # get current region from combobox
          # text   = obj.itemText(index)   # get the text for new selected index
          name = obj.objectName()

          value = (settings.value(name))

          if value == "":
              continue

          index = obj.findText(value)  # get the corresponding index for specified string in combobox

          if index == -1:  # add to list if not found
                obj.insertItems(0, [value])
                index = obj.findText(value)
                obj.setCurrentIndex(index)
          else:
                obj.setCurrentIndex(index)  # preselect a combobox value by index

      if isinstance(obj, QLineEdit):
          name = obj.objectName()
          value = (settings.value(name).decode('utf-8'))  # get stored value from registry
          obj.setText(value)  # restore lineEditFile

      if isinstance(obj, QCheckBox):
          name = obj.objectName()
          value = settings.value(name)  # get stored value from registry
          if value != None:
              obj.setChecked(strtobool(value))  # restore checkbox

      if isinstance(obj, QRadioButton):
         name = obj.objectName()
         value = settings.value(name)  # get stored value from registry
         if value != None:
             obj.setChecked(strtobool(value))