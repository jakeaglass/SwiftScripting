#!/usr/bin/env python2.7

import sys

from clang.cindex import TranslationUnit
from clang.cindex import CursorKind
from clang.cindex import Config


Config.set_library_path("/Applications/Xcode.app//Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib")

keywords = ['class', 'deinit', 'enum', 'extension', 'func', 'import', 'init', 'internal', 'let', 'operator', 'private',
            'protocol', 'public', 'static', 'struct', 'subscript', 'typealias', 'var', 'break', 'case', 'continue',
            'default', 'do', 'else', 'fallthrough', 'for', 'if', 'in', 'return', 'switch', 'where', 'while', 'as',
            'dynamicType', 'false', 'is', 'nil', 'self', 'Self', 'super', 'true', 'associativity', 'convenience',
            'dynamic', 'didSet', 'final', 'get', 'infix', 'inout', 'lazy', 'left', 'mutating', 'none', 'nonmutating',
            'optional', 'override', 'postfix', 'precedence', 'prefix', 'Protocol', 'required', 'right', 'set', 'Type',
            'unowned', 'weak', 'willSet']

type_dict = {'BOOL': 'Bool',
             'double': 'Double',
             'NSInteger': 'Int',
             'NSString': 'String',
             'id': 'AnyObject',
             'NSArray': '[AnyObject]',
             'NSDictionary': '[NSObject : AnyObject]'}


def safe_name(name):
    return '`{}`'.format(name) if name in keywords else name


def type_for_type(objc_type):
    obj_type_string = objc_type.spelling.split(" ")[0]
    return type_dict.get(obj_type_string, obj_type_string)


def name_from_path(path):
    last_part = path.split("/")[-1]
    return last_part.split('.')[0]


class SBHeaderProcessor(object):
    swift_file = None

    def __init__(self, file_path):
        self.file_path = file_path
        fid = open(file_path)
        self.lines = fid.readlines()
        fid.close()
        self.app_name = name_from_path(file_path)

    def line_comment(self, cursor):
        line = self.lines[cursor.location.line - 1]
        parts = line.strip().split('//')
        return ' //{}'.format(parts[1]) if len(parts) == 2 else ''

    def emit_enums(self):
        enum_file = open('{}Enums.h'.format(self.app_name), 'w')
        typedefs = [line for line in self.lines if line.startswith('typedef')]
        class_lines = [line for line in self.lines if line.startswith('@class')]
        start_line_index = self.lines.index(class_lines[-1]) + 1
        last_typedef_line_index = self.lines.index(typedefs[-1]) + 1
        for index in xrange(start_line_index, last_typedef_line_index):
            enum_file.write(self.lines[index])
        enum_file.close()

    def emit_line(self, line):
        self.swift_file.write(line + '\n')

    def emit_property(self, cursor):
        tokens = cursor.translation_unit.get_tokens(extent=cursor.extent)
        get_set = 'get set'
        for word in (x.spelling for x in tokens):
            if word == 'readonly':
                get_set = 'get'
        swift_type = type_for_type(cursor.type)
        self.emit_line('    optional var {}: {} {{ {} }}{}'.format(cursor.spelling, swift_type, get_set,
                                                                   self.line_comment(cursor)))

    def emit_function(self, cursor, accessors):
        if cursor.spelling not in accessors:
            func_name = cursor.spelling.split(':')[0]
            parameters = ['{}: {}'.format(safe_name(child.spelling), type_for_type(child.type))
                          for child in cursor.get_children() if child.kind == CursorKind.PARM_DECL]
            return_type = [child.type for child in cursor.get_children() if child.kind != CursorKind.PARM_DECL]
            if return_type:
                return_string = ' -> {}'.format(type_for_type(return_type[0]))
            else:
                return_string = ''
            self.emit_line('    optional func {}({}){}{}'.format(
                func_name, ", ".join(parameters), return_string, self.line_comment(cursor)))

    def emit_protocol(self, cursor):
        self.emit_line('@objc public protocol {} {{'.format(cursor.spelling))
        superclass = 'SBObject'
        property_accessors = [child.spelling for child in cursor.get_children()
                              if child.kind == CursorKind.OBJC_PROPERTY_DECL]
        property_setters = ['set{}{}:'.format(getter[0].capitalize(), getter[1:]) for getter in property_accessors]
        property_accessors += property_setters
        for child in cursor.get_children():
            if child.kind == CursorKind.OBJC_PROPERTY_DECL:
                self.emit_property(child)
            elif child.kind == CursorKind.OBJC_INSTANCE_METHOD_DECL:
                self.emit_function(child, property_accessors)
            elif child.kind == CursorKind.OBJC_SUPER_CLASS_REF and child.spelling.startswith('SB'):
                superclass = child.spelling
        self.emit_line('}')
        self.emit_line('extension {} : {} {{}}\n'.format(superclass, cursor.spelling))

    def walk(self, cursor):
        local_children = [child for child in cursor.get_children()
                          if child.location.file and child.location.file.name == self.file_path]
        for child in local_children:
            if child.kind in (CursorKind.OBJC_INTERFACE_DECL, CursorKind.OBJC_CATEGORY_DECL):
                self.emit_protocol(child)

    def emit_swift(self):
        translation_unit = TranslationUnit.from_source(self.file_path, args=["-ObjC"])
        self.swift_file = open('{}.swift'.format(self.app_name), 'w')
        for inclusion in translation_unit.get_includes():
            if inclusion.depth == 1:
                include = inclusion.include.name
                self.emit_line('import {}'.format(name_from_path(include)))
        self.emit_line("")
        cursor = translation_unit.cursor
        self.walk(cursor)
        self.swift_file.close()


def main(file_path):
    header_processor = SBHeaderProcessor(file_path)
    header_processor.emit_swift()
    header_processor.emit_enums()


if __name__ == '__main__':
    main(sys.argv[1])
