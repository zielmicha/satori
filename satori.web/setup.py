# vim:ts=4:sts=4:sw=4:expandtab
from setuptools import setup, find_packages
from distutils.util import convert_path
import os

def find_files(where='.', prefix=''):
    out = []
    stack=[(convert_path(where), prefix)]
    while stack:
        where,prefix = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where,name)
            if name != '..' and name != '.' and os.path.isdir(fn):
                stack.append((fn,prefix+name+'/'))
            elif os.path.isfile(fn):
                out.append(prefix+name); 
    return out

setup(name='satori.web',
    packages=find_packages(),
    namespace_packages=[
        'satori',
    ],
    install_requires=[
        'flup',
        'setuptools',
        'Thrift',
        'satori.client.common',
        'satori.tools',
        'Sphinx',
    ],
    entry_points='''
        [console_scripts]
	    satori.web.manage = satori.web:manage
    ''',
    package_data={
        'satori.web': find_files('satori/web/templates', 'templates/') + find_files('satori/web/files', 'files/'),
    },
)
