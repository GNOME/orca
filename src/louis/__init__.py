# Liblouis Python bindings
#
# Copyright 2007-2008 Eitan Isaacson
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Liblouis Python bindings"""

__copyright__ = "Copyright (c) 2007-2008 Eitan Isaacson"
__license__   = "LGPL"

from constants import *
import os

def listTables():
   tables = {}
   try:
      for fname in os.listdir(TABLES_DIR):
         if fname[-4:] in ('.utb', '.ctb'):
            alias = fname[:-4]
            tables[TABLE_NAMES.get(alias, alias)] = \
                                          os.path.join(TABLES_DIR, fname)
   except OSError:
      pass

   return tables

def getDefaultTable():
   try:
      for fname in os.listdir(TABLES_DIR):
         if fname[-4:] in ('.utb', '.ctb'):
            if fname.startswith('en-us'):
               return os.path.join(TABLES_DIR, fname)
   except OSError:
      pass

   return ''

#####################################################################
#
# The following code is here to compensate on a few current liblouis
# bugs.
#
#####################################################################

import _louis
version = _louis.version
translateString = _louis.translateString

def translate(tran_tables, inbuf, typeform=[], cursorPos=0, mode=0):
   if mode == MODE.compbrlAtCursor:
      contracted, inPos, outPos, cursorPos,  = \
                  _expandAtCursor(tran_tables, inbuf,
                                  typeform, cursorPos, mode)
   else:
      contracted, inPos, outPos, cursorPos,  = \
                  _louis.translate(tran_tables, inbuf,
                                    typeform, cursorPos, mode)
      
   return contracted, inPos, outPos, cursorPos

def _expandAtCursor(tran_tables, inbuf, typeform=[], cursorPos=0, mode=0):
   """Contracts a inbuf, leaving the word under the cursor expanded.
   This is a temporary method that should disappear once liblouis
   get it right.
   
   Arguments:
   - inbuf: Inbuf to contract.
   - cursorPos: Offset of cursor.
   """
   prefix, uncontractedWord, suffix  = \
           _divideLine(inbuf, cursorPos)

   cursorInWord = cursorPos - len(prefix)

   # Contract prefix
   # 
   prefixContracted, prefixInPos, prefixOutPos, cursorPos = \
                     _louis.translate(tran_tables,
                                     prefix.decode())

   # Contract suffix
   # 
   suffixContracted, suffixInPos, suffixOutPos, cursorPos = \
                     _louis.translate(tran_tables,
                                     suffix.decode())

   cursorPos = len(prefixContracted) + cursorInWord
   
   contracted = prefixContracted + \
                uncontractedWord + \
                suffixContracted

   inPos = _mushPosArrays(prefixInPos,
                          len(uncontractedWord),
                          suffixInPos)

   outPos = _mushPosArrays(prefixOutPos,
                           len(uncontractedWord),
                           suffixOutPos)

   return contracted, inPos, outPos, cursorPos

def _mushPosArrays(prefixPos, uncontractedLen, suffixPos):
   try:
      uncontractedPos = range(prefixPos[-1] + 1,
                              uncontractedLen+prefixPos[-1] + 1)
   except IndexError:
      uncontractedPos = range(uncontractedLen)

   pos = prefixPos + \
         uncontractedPos

   try:
      suffixOffset = pos[-1] + 1
   except IndexError:
      suffixOffset = 0

   pos += [offs + suffixOffset for offs in suffixPos]

   return pos

def _partition(myStr, mySep):
   """Provides an implementation of partition for compatibility with
   Python 2.4.

   Arguments:
   - myStr: the string
   - mySep: the separator to look for, starting at the beginning of the string

   Returns:
   (stringBeforeSep, mySep, stringAfterSep)
   """

   try:
     return myStr.partition(mySep)
   except AttributeError:
     index = myStr.find(mySep)
     if index < 0:
        return (myStr, u'', u'')
     else:
        return (myStr[0:index], 
                myStr[index:index+len(mySep)], 
                myStr[index+len(mySep):])

def _rpartition(myStr, mySep):
   """Provides an implementation of rpartition for compatibility with
   Python 2.4.

   Arguments:
   - myStr: the string
   - mySep: the separator to look for, starting at the end of the string

   Returns:
   (stringBeforeSep, mySep, stringAfterSep)
   """

   try:
     return myStr.rpartition(mySep)
   except AttributeError:
     index = myStr.rfind(mySep)
     if index < 0:
        return (u'', u'', myStr)
     else:
        return (myStr[0:index], 
                myStr[index:index+len(mySep)], 
                myStr[index+len(mySep):])

def _divideLine(line, offset):
   """Isolates a word the cursor is on and returns the prefix,
   the cursored word, and the suffix. This is a temporary method
   that avoids a liblouis bug.
   
   Arguments:
   - line: The line to process.
   - offset: The offset of the cursor.
   """
   if len(line) <= offset:
      return line, '', ''
   
   firstHalf = _rpartition(line[:offset], ' ')
   secondHalf = _partition(line[offset:], ' ')
   return firstHalf[0] + firstHalf[1], \
          firstHalf[2] + secondHalf[0], \
          secondHalf[1] + secondHalf[2]
