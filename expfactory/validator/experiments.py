'''

validators/experiments.py: python functions to validate experiments and library
experiment objects

The MIT License (MIT)

Copyright (c) 2017 Vanessa Sochat, Stanford University

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import os
import re
import sys
from expfactory.logman import bot
from glob import glob
import json


class ExperimentValidator:

    def __init__(self,quiet=False):
        if quiet is True:
            bot.level = 0


class LibraryValidator:

    def __init__(self,quiet=False):
        if quiet is True:
            bot.level = 0

    def validate_all(self,jsonfile):
        if not self.validate_extension(jsonfile):
            return False
        if not self.validate_loading(jsonfile):
            return False
        if not self.validate_content(jsonfile):
            return False
        return True


    def validate_extension(self,jsonfile):
        bot.test("EXTENSION: Experiment %s" %(os.path.basename(jsonfile)))
        return jsonfile.endswith('.json')
 

    def validate_loading(self,jsonfile):
        bot.test("LOADING: Experiment %s" %(os.path.basename(jsonfile)))
        with open(jsonfile,'r') as filey:
            content = json.load(filey)
        return isinstance(content,dict)


    def validate_content(self,jsonfile):
        name = os.path.basename(jsonfile)
        bot.test("CONTENT: Experiment %s" %(name))
        with open(jsonfile,'r') as filey:
            content = json.load(filey)

        # Validate name
        bot.test("        Name")
        if "name" not in content:
            return notvalid('"name" not found in %s' %(name)) 

        if not re.match("^[a-z0-9_]*$", content['name']): 
            return notvalid('''invalid characters in %s, only 
                               lowercase and "_" allowed.''' %(content['name'])) 
         
        # Validate Github
        bot.test("        Github")
        if "github" not in content:
            return notvalid('"github" not found in %s' %(name)) 
        if not re.search("(\w+://)(.+@)*([\w\d\.]+)(:[\d]+){0,1}/*(.*)",content['github']):
            return notvalid('%s is not a valid URL.' %(content['github'])) 
        if not isinstance(content["github"],str):
            return notvalid("%s must be a string" %(content['github']))

        # Maintainers
        bot.test("        Maintainers")
        if "maintainers" not in content:
            return notvalid('"maintainers" missing in %s' %(name)) 
        if not isinstance(content["maintainers"],list):
            return notvalid('"maintainers" must be list in %s' %(name))  
        for maintainer in content['maintainers']:
            if not isinstance(maintainer,dict):
                return notvalid("%s must be a dict in %s" %(maintainer,name))
            if "email" not in maintainer:
                return notvalid("email missing in %s for %s" %(maintainer,name))
            if "github" not in maintainer:
                return notvalid("github missing in %s for %s" %(maintainer,name))
            if "name" not in maintainer:
                return notvalid("name missing in %s for %s" %(maintainer,name))
            if not maintainer['github'].startswith('@'):
                return notvalid("%s must start with @ for %s" (maintainer['github'],name))
            if not re.search("^.+@.+[.]{1}.+$",maintainer['email']):
                return notvalid('%s is not a valid email.' %(maintainer['email'])) 
        return True

def notvalid(reason):
    print(reason)
    return False
