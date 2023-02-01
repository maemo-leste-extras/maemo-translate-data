#!/usr/bin/env python

import sys
import shutil
import zipfile
import os
import os.path
import json


def read_global_registry(zipfile):
    for name in zf.namelist():
        basename = os.path.basename(name)
        if basename == 'registry.json':
            fp = zf.open(name)
            d = json.load(fp)
            fp.close()

            return d

    return None


def create_install_files(model_names):
    for model_name in model_names:
        filename = 'maemo-translate-data-%s.install' % model_name
        fp = open(os.path.join('debian', filename), 'w+')
        fp.write('/usr/share/kotki/%s/*\n' % model_name)
        fp.close()


def create_control_entries(model_names):
    deps = ', '. join(['maemo-translate-data-%s' % k for k in sorted(model_names)])
    s = '''Source: maemo-translate-data
Priority: optional
Section: localization
Maintainer: Merlijn Wajer <merlijn@wizzup.org>
Build-Depends:
 debhelper-compat (=12),
Standards-Version: 4.3.0
Vcs-Git: https://github.com/maemo-leste/hildon-theme-alpha
Vcs-Browser: https://github.com/maemo-leste/hildon-theme-alpha

Package: maemo-translate-data-all
Architecture: all
Depends: ${misc:Depends}, %s
Description: All available language packs for maemo-translate
''' % deps

    for model_name in sorted(model_names):
        entry = '''
Package: maemo-translate-data-%s
Architecture: all
Depends: ${misc:Depends}
Description: Maemo Translate models for %s language
    ''' % (model_name, model_name)
        s += entry

    return s

def create_debian_dotinstall(model_names):
    deps = ', '. join(['maemo-translate-%s' % k for k in sorted(model_names)])

    s = '''Source: maemo-translate-data
Priority: optional
Section: localization
Maintainer: Merlijn Wajer <merlijn@wizzup.org>
Build-Depends:
 debhelper-compat (=12),
Standards-Version: 4.3.0
Vcs-Git: https://github.com/maemo-leste/hildon-theme-alpha
Vcs-Browser: https://github.com/maemo-leste/hildon-theme-alpha

Package: maemo-translate-data-all
Architecture: all
Depends: ${misc:Depends}, %s
Description: All available language packs for maemo-translate
''' % deps

    for model_name in sorted(model_names):
        entry = '''
Package: maemo-translate-data-%s
Architecture: all
Depends: ${misc:Depends}
Description: Maemo Translate models for %s language
    ''' % (model_name, model_name)
        s += entry

    return s

def extract_zip(zf, model_names, to_install, registry):
    files = []

    for model in model_names:
        os.makedirs(os.path.join('model', model))

    regdata = {}
    for model in model_names:
        for key, val in registry.items():
            if key == model + 'en' or key == 'en' + model:
                if model not in regdata:
                    regdata[model] = {}
                regdata[model][key] = val

    for k, v in regdata.items():
        fp = open(os.path.join('model', k, 'registry.json'), 'w+')
        json.dump(v, fp)
        fp.close()

    for model in model_names:
        for data in to_install[model]:
            for _, file in data.items():
                for name in zf.namelist():
                    if name.endswith(file['name']):
                        path = os.path.join('model', model, file['name'])
                        zipf = zf.open(name, 'r')
                        fp = open(path, 'wb+')
                        fp.write(zipf.read())
                        fp.close()
                        zipf.close()

#def create_makefile_am(model_names, to_install):
#    files = []
#
#    s = '''layoutdir               = ${datadir}/@PACKAGE@/
#
#layout_DATA =\t\\\n'''
#
#    for model in model_names:
#        for data in to_install[model]:
#            s += '\t%s/%s\t\\\n' % (model, 'model.json')
#            for _, file in data.items():
#                s += '\t%s/%s\t\\\n' % (model, file['name'])
#                files.append('%s/%s' % (model, file['name']))
#
#    return s


#MAINTAINERCLEANFILES            = Makefile.in


# TODO:
# Create suggested control entries
# Create Makefile.am model_DATA line

if __name__ == '__main__':
    zf = zipfile.ZipFile(sys.argv[1])

    registry = read_global_registry(zf)

    langs = set()

    for name in zf.namelist():
        name = os.path.basename(name)
        mat = '.s2t.bin'
        if name.endswith(mat):
            name = name.replace(mat, '')
            name = name[name.rfind('.')+1:]
            langs.add(name)


    registry_langs = set(registry.keys())

    #print(langs)
    #print(registry_langs)
    #print(registry_langs - langs)

    model_names = set()

    for lang in langs:
        ll, rl = lang[0:2], lang[2:4]
        dirname = ll
        if dirname == 'en':
            dirname = rl

        model_names.add(dirname)

    #print('models:', model_names)

    to_install = {}

    for regkey, regdata in registry.items():
        stripped = regkey.replace('en', '')
        if stripped not in model_names:
            raise Exception('%s not in %s' % (stripped, model_names))

        if stripped in to_install:
            to_install[stripped].append(regdata)
        else:
            to_install[stripped] = [regdata]

    if os.path.exists('model'):
        shutil.rmtree('model')
    os.makedirs('model')
    extract_zip(zf, model_names, to_install, registry)

    control = create_control_entries(model_names)
    fp = open('debian/control', 'w+')
    fp.write(control)
    fp.close()

    create_install_files(model_names)

    #makefile_am = create_makefile_am(model_names, to_install)
    #makefile_am = makefile_am[:-2] + '\n' # remove \
    #fp = open('model/Makefile.am', 'w+')
    #fp.write(makefile_am)
    #fp.close()


    #print(makefile_am)

    #from pprint import pprint
    #pprint(to_install)

    #for model_name in model_names:
    #    en_name_l = 'en' + model_name
    #    if en_name_l in data:
    #        print(data[en_name_l])

    #    en_name_r = model_name + 'en'
    #    if en_name_r in data:

    #    print(data[en_name_r])
