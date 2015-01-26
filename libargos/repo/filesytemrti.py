# -*- coding: utf-8 -*-

# This file is part of Argos.
# 
# Argos is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Argos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Argos. If not, see <http://www.gnu.org/licenses/>.

""" Repository items (RTIs) for browsing the file system
"""

import logging, os
from .treeitems import (ICONS_DIRECTORY, BaseRti)
from libargos.info import DEBUGGING
from libargos.qt import QtGui
from libargos.repo.registry import getRtiRegistry

logger = logging.getLogger(__name__)


class UnknownFileRti(BaseRti):
    """ A repository tree item that represents a file of unknown type.  
        The file is not opened.
    """
    _label = "Unknown File"
    _iconClosed = QtGui.QIcon(os.path.join(ICONS_DIRECTORY, 'fs.file-closed.svg'))    
    _iconOpen = QtGui.QIcon(os.path.join(ICONS_DIRECTORY, 'fs.file-open.svg'))
    
    def __init__(self, nodeName='', fileName=''):
        """ Constructor 
        """
        super(UnknownFileRti, self).__init__(nodeName=nodeName, fileName=fileName)
        self._checkFileExists()


    def hasChildren(self):
        """ Returns False. Leaf nodes never have children. """
        return False
    


class DirectoryRti(BaseRti):
    """ A repository tree item that has a reference to a file. 
    """
    _label = "Directory"
    _iconClosed = QtGui.QIcon(os.path.join(ICONS_DIRECTORY, 'fs.directory-closed.svg'))
    _iconOpen = QtGui.QIcon(os.path.join(ICONS_DIRECTORY, 'fs.directory-open.svg'))
    
    def __init__(self, nodeName='', fileName=''):
        """ Constructor
        """
        super(DirectoryRti, self).__init__(nodeName=nodeName, fileName=fileName)
        self._checkFileExists() # TODO: check for directory?

        
    def _fetchAllChildren(self):
        """ Gets all sub directories and files within the current directory.
            Does not fetch hidden files.
        """
        childItems = []
        fileNames = os.listdir(self._fileName)
        absFileNames = [os.path.join(self._fileName, fn) for fn in fileNames]

        # Add subdirectories
        for fileName, absFileName in zip(fileNames, absFileNames):
            if os.path.isdir(absFileName) and not fileName.startswith('.'):
                childItems.append(DirectoryRti(fileName=absFileName, nodeName=fileName))
            
        # Add regular files
        for fileName, absFileName in zip(fileNames, absFileNames):
            if os.path.isfile(absFileName) and not fileName.startswith('.'):
                childItem = createRtiFromFileName(absFileName)
                childItems.append(childItem)
                        
        return childItems
    
    
def detectRtiFromFileName(fileName):
    """ Determines the type of RepoTreeItem to use given a file name.
        Uses a DirectoryRti for directories and an UnknownFileRti if the file
        extension doesn't match one of the registered RTI extensions.
    """
    _, extension = os.path.splitext(fileName)
    if os.path.isdir(fileName):
        cls = DirectoryRti
    else:
        try:
            cls = getRtiRegistry().getRtiByExtension(extension)
        except KeyError:
            cls = UnknownFileRti
            
    return cls


def createRtiFromFileName(fileName):
    """ Determines the type of RepoTreeItem to use given a file name and creates it.
        Uses a DirectoryRti for directories and an UnknownFileRti if the file
        extension doesn't match one of the registered RTI extensions.
    """
    cls = detectRtiFromFileName(fileName)
    return cls.createFromFileName(fileName)

