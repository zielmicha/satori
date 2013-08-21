# vim:ts=4:sts=4:sw=4:et
import argparse
import glob
import logging
import os
import os.path
import shutil
import sys
import time
import yaml

from satori.client.common import want_import
want_import(globals(), '*')
from satori.tools import auth_setup, catch_exceptions, config, options, setup
from satori.tools.params import parser_from_xml

from satori.tools.problems.common import Dirs, upload_blob


def make_oa_map(params_parser, yaml_data, dirs):
    if not params_parser or not params_parser.params:
        return {}
    oa_map = {}
    for param in params_parser.params:
        if param.name in yaml_data:
            if param.type_.name() == 'blob':
                oa_map[param.name] = upload_blob(dirs.parse(yaml_data[param.name]))
            else:
                oa_map[param.name] = AnonymousAttribute(is_blob=False, value=yaml_data[param.name])
        else:
            if param.required and param.default is None:
                raise RuntimeError(
                        'Required param %s not specified' % param.name)
    return oa_map


def open_test(test_yaml_fname):
    with open(test_yaml_fname) as test_yaml_file:
        test_yaml = yaml.safe_load(test_yaml_file)
    if type(test_yaml) != dict:
        raise RuntimeError('Test JSON must be an object')
    if 'name' not in test_yaml:
        raise RuntimeError('Test must have a name')
    return test_yaml


def make_test_data(dirs):
    test_yaml = open_test(dirs.parse('test.yaml'))  # path relative to test dir
    test_name = test_yaml['name']
    test_description = test_yaml.get('description', '')

    if 'judge' not in test_yaml:
        raise RuntimeError('No judge specified')

    judge_path = dirs.parse(test_yaml['judge'])
    with open(judge_path) as judge_file:
        judge_content = judge_file.read()

    judge_params = parser_from_xml(judge_content)
    test_data = make_oa_map(judge_params, test_yaml, dirs)
    test_data['name'] = AnonymousAttribute(is_blob=False, value=test_name)
    test_data['description'] = AnonymousAttribute(is_blob=False,
                                                  value=test_description)
    test_data['judge'] = upload_blob(judge_path)

    return test_data


def discover_tests(problem_dir):
    # TODO: fail if problem_dir does not contain problem.yaml file.
    tests = []
    for fname in glob.glob(os.path.join(problem_dir, '*', 'test.yaml')):
        test_yaml = open_test(fname)
        tests.append((test_yaml['name'], os.path.dirname(fname)))
    return dict(tests)


def get_temporary_submit_result(submit_id):
    submits = TemporarySubmit.filter(TemporarySubmitStruct(id=submit_id))
    if not submits:
        return None
    result = submits[0].result_get_list()
    return result if result else None


def print_temporary_submit_result(result):
    blobs = []
    for attr in result:
        if attr.is_blob:
            blobs.append(attr.name)
        else:
            print attr.name, ':', attr.value
    print 'blobs', ':', ', '.join(blobs) 


def temporary_submit(opts):
    if ':' not in opts.TEST:
        raise RuntimeError('TEST must be of form PROBLEM_DIR:TEST_NAME')
    problem_dir, test_name = opts.TEST.split(':', 1)
    if not test_name:
        raise RuntimeError(
                'Specify a test name. Running all tests is not yet supported')
    if not problem_dir:
        problem_dir = os.getcwd()
    tests = discover_tests(problem_dir)
    if test_name not in tests:
        raise RuntimeError('Unknown test name')
    dirs = Dirs(problem_dir, tests[test_name])
    submit_file_path = opts.SOLUTION

    test_data = make_test_data(dirs)
    submit_data = {'content': upload_blob(submit_file_path)}

    submit = TemporarySubmit.create(test_data, submit_data)
    submit_id = submit.id
    print 'Temporary submit id:', submit_id

    print 'Waiting for results . . .',
    sys.stdout.flush()
    while True:
        time.sleep(2)
        result = get_temporary_submit_result(submit_id)
        if result:
            print
            print_temporary_submit_result(result)
            break
        print '.',
        sys.stdout.flush()
       
