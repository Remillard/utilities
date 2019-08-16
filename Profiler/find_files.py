#! python3
"""Initial work on a hierarchy scanning module"""

import re
import os
from collections import defaultdict
from timeit import default_timer as timer

# Global pattern for valid HDL names.
IDENT_P = r"[a-zA-Z](?:[a-zA-Z0-9]|_(?!_))*[a-zA-Z0-9]*"


class VHDLEntity:
    """
    Class representing the information related to where an entity in VHDL.
    In general, entities are pretty easy because they are a single block item,
    and there's nothing in particular to extract from them.  The negative
    lookbehind in the pattern is to prevent matching when the name appears
    in direct entity instantiations.
    """

    ENTITY_P = r"(?<!:)(?:\n\s*|^\s*)(entity)\s+({})".format(IDENT_P)

    # Instantiation
    def __init__(self, name, root, filename, start):
        self.name = name
        self.root = root
        self.filename = filename
        self.start = start

    def __str__(self):
        return "{} @ {} in '{}'".format(self.name, self.start, os.path.join(self.root, self.filename))

    # Generator functions ueed to populate the tree of entities
    @classmethod
    def entity_scan(cls, root, file, buf):
        """
        Iterates over the buffer and yields Entity objects.  No longer
        any need to check for filetype as this will be handled at a higher
        level.
        """
        for match in re.finditer(cls.ENTITY_P, buf, re.I):
            yield cls(match.group(2), root, file, match.start(1))


class SVModule:
    """
    Class representing the information related to where a module block in
    Verilog/SystemVerilog begins and ends.  This has been factored out of
    the VHDL Entity class because in Verilog/SystemVerilog the module acts
    as both block descriptor and architecture.  Thus to correctly identify
    the hierarchy, both the start and end positions must be identified.
    """

    MODULE_P = r"(?:\n\s*|^\s*)(module)\s+({})".format(IDENT_P)
    ENDMODULE_P = r"\b(endmodule)\b"

    # Instantiation
    def __init__(self, name, root, filename, start, end):
        self.name = name
        self.root = root
        self.filename = filename
        self.start = start
        self.end = end

    def __str__(self):
        return "{} @ {}->{} {}".format(self.name, self.start, self.end, os.path.join(self.root, self.filename))


    # Generator functions ueed to populate the tree of entities
    @classmethod
    def module_scan(cls, root, file, buf):
        """
        Iterates over the buffer and yields Module objects.  Each
        identification of a module requires finding the matching endmodule
        statement to correction apportion any instantiations within to the
        right module.
        """
        for match in re.finditer(cls.MODULE_P, buf, re.I):
            endmatch = re.search(cls.ENDMODULE_P, buf[match.start() :], re.I)
            yield cls(
                match.group(2),
                root,
                file,
                match.start(1),
                match.start(1) + endmatch.end(),
            )


class VHDLComponent:
    """
    Class representing the information related to where a component is
    declared in a file.  Don't need the type because this is VHDL only.
    Again the negative lookbehind is for avoiding named component
    instantiations.  Components may be defined in architectures or packages,
    so for the moment will just scan entire files for these.
    """

    COMPONENT_P = r"(?<!:)(?:\n\s*|^\s*)(component)\s+({})".format(IDENT_P)

    # Instantiation
    def __init__(self, name, root, filename, start):
        self.name = name
        self.root = root
        self.filename = filename
        self.start = start

    def __str__(self):
        return "{} @ {} in '{}'".format(self.name, self.start, os.path.join(self.root, self.filename))

    # Generator functions used to populate the tree.
    @classmethod
    def component_scan(cls, root, file, buf):
        """Iterates over the buffer and yields Component objects"""
        if file.lower().endswith(".vhd"):
            for match in re.finditer(cls.COMPONENT_P, buf, re.I):
                yield cls(match.group(2), root, file, match.start(1))


class VHDLArchitecture:
    """
    Class representing the information related to an architecture defined
    for a particular entity body.  Must also look for the end sequence in
    order to define a start and stop for scanning for instances similiarly to
    Verilog modules.
    """

    ARCHITECTURE_P = r"(?:\n\s*|^\s*)(architecture)\s+({})\s+of\s+({})\s+is".format(
        IDENT_P, IDENT_P
    )

    def __init__(self, name, entity, root, filename, start, end):
        self.name = name
        self.entity = entity
        self.root = root
        self.filename = filename
        self.start = start
        self.end = end

    def __str__(self):
        return "{} @ {}->{} in '{}'".format(self.name, self.start, self.end, os.path.join(self.root, self.filename))

    @classmethod
    def arch_scan(cls, root, file, buf):
        """
        Iterates over a buffer and yields Architecture objects.  Each
        identification of an architecture must find the closing end
        architecture structure to correctly apportion any instantiations
        within to the right module.
        """
        for match in re.finditer(cls.ARCHITECTURE_P, buf, re.I):
            # Moving the end pattern here because it needs to be dynamically
            # updated with the name of the architecture, because otherwise
            # we'll match to other words.
            end_architecture_p = r"\bend(?:\s+architecture)?(?:\s+{})?\s*;".format(match.group(2))
            endmatch = re.search(end_architecture_p, buf[match.start():], re.I)
            yield cls(
                match.group(2),
                match.group(3),
                root,
                file,
                match.start(1),
                match.start(1) + endmatch.end(),
            )


class VHDLInstance:
    """
    Class representing the information related to instantiations of block units
    in VHDL.  Factored out the Verilog variation.  Also added class attributes
    for what entity/arch pair it's located in as well as what entity it's
    instantiating.
    """

    # Component and Direct Entity Instantiations.  Accounts for multiple
    # layers of library invocations as well.
    VHDL_INSTANCE = r"\n\s*({})\s*:\s*(?:entity\s+|component\s+)?(?:{}\.)*({})(?=\s+(?:port|generic))".format(
        IDENT_P, IDENT_P, IDENT_P
    )

    def __init__(self, instance_name, instance_entity, calling_entity, calling_arch, root, filename, position):
        self.instance_name = instance_name
        self.instance_entity = instance_entity
        self.calling_entity = calling_entity
        self.calling_arch = calling_arch
        self.root = root
        self.filename = filename
        self.position = position

    def __str__(self):
        return "{} @ {} in '{}'".format(self.instance_name, self.position, os.path.join(self.root, self.filename))

    @classmethod
    def instance_scan(cls, root, file, buf, offset, call_entity, call_arch):
        """
        Iterates over a buffer and yields Instance objects.  Note that the
        position returned is relative to the start of the buffer hence
        passing in the offset for the buffer start.
         """
        for match in re.finditer(cls.VHDL_INSTANCE, buf, re.I):
            yield cls(
                match.group(1),
                match.group(2),
                call_entity,
                call_arch,
                root,
                file,
                match.start(1) + offset
            )


class SVInstance:
    """
    Class representing the information related to instantiations of block units
    in Verilog/SystemVerilog.
    """
    # Verilog Constructs.  There seems to be no simple way to detect a Verilog
    # instantiation purely by regular expression.  Here is an algorithmic
    # solution.
    # 1. The module finder will chunk out a block defined by module/endmodule
    #    and pass that to the instantiation scanner.
    # 2. The scanner method will break the block on semicolons which
    #    ensures no more than one instantiation per subsection.
    # 3. Words in each subsection will be scanned one at a time and checked
    #    against the reserved word list.
    # 4. If a non-match is found, the pattern will be applied to check
    #    for an instantiation.
    # 5. If the instantiation matches, we may extract the information and
    #    continue to the next substring.
    SVLOG_RESERVED_LIST = ['alias', 'always', 'always_comb', 'always_ff',
    'always_latch', 'and', 'assert', 'assign', 'assume', 'automatic',
    'before', 'begin', 'bind', 'bins', 'binsof', 'bit', 'break', 'buf',
    'bufif0', 'bufif1', 'byte', 'case', 'casex', 'casez', 'cell', 'chandle',
    'class', 'clocking', 'cmos', 'config', 'const', 'constraint', 'context',
    'continue', 'cover', 'covergroup', 'coverpoint', 'cross', 'deassign',
    'default', 'defparam', 'design', 'disable', 'dist', 'do', 'edge', 'else',
    'end', 'endcase', 'endclass', 'endclocking', 'endconfig', 'endfunciton',
    'endgenerate', 'endgroup', 'endinterface', 'endmodule', 'endpackage',
    'endprimitive', 'endprogram', 'endproperty', 'endspecify', 'endsequence',
    'endtable', 'endtask', 'enum', 'event', 'expect', 'export', 'extends',
    'extern', 'final', 'first_match', 'for', 'force', 'foreach', 'forever',
    'fork', 'forkjoin', 'function', 'generate', 'genvar', 'highz0', 'highz1',
    'if', 'iff', 'ifnone', 'ignore_bins', 'illegal_bins',  'import', 'incdir',
    'include', 'initial', 'inout', 'input', 'inside', 'instance', 'int',
    'integer', 'interface', 'intersect', 'join', 'join_any', 'join_none',
    'large', 'liblist', 'library', 'local', 'localparam', 'logic', 'longint',
    'macromodule', 'matches', 'medium', 'modport', 'module', 'nand', 'negedge',
    'new', 'nmos', 'nor', 'noshowcancelled', 'not', 'notif0', 'notif1', 'null',
    'or', 'output', 'package', 'packed', 'parameter', 'pmos', 'posedge',
    'primitive', 'priority', 'program', 'property', 'protected', 'pull0',
    'pull1', 'pulldown', 'pullup', 'pulsestyle_onevent', 'pulsestyle_ondetect',
    'pure', 'rand', 'randc', 'randcase', 'randsequence', 'rcmos', 'real',
    'realtime', 'ref', 'reg', 'release', 'repeat', 'return', 'rnmos' 'rpmos',
    'rtran', 'rtranif0', 'rtranif1', 'scalared', 'sequence', 'shortint',
    'shortreal', 'showcancelled', 'signed', 'small', 'solve', 'specify',
    'specparam', 'static', 'string', 'strong0', 'strong1', 'struct',
    'super', 'supply0', 'supply1', 'table', 'tagged', 'task', 'this',
    'throughout', 'time', 'timeprecision', 'timeunit', 'tran', 'tranif0',
    'tranif1', 'tri', 'tri0', 'tri1', 'triand', 'trior', 'trireg', 'type',
    'typedef', 'union', 'unique', 'unsigned', 'use', 'uwire', 'var',
    'vectored', 'virtual', 'void', 'wait', 'wait_order', 'wand', 'weak0',
    'weak1', 'while', 'wildcard', 'wire', 'with', 'within', 'wor', 'xnor',
    'xor']
    WORD_P = r"\b(\w+)\b"
    SVCOMMENT_P = r"//.*\n"
    VLOG_INSTANCE_P = r"\b(\w+)\b(?:\s*?#\((?:\([\w\W]*?\)|[\s\w\W])*?\))?\s*?\b(\w+)\b\s*?(?:\s*?\((?:\([\w\W]*?\)|[\s\w\W])*?\));"

    def __init__(self, instance_name, instance_module, calling_module, root, filename, position):
        self.instance_name = instance_name
        self.instance_module = instance_module
        self.calling_module = calling_module
        self.root = root
        self.filename = filename
        self.position = position

    def __str__(self):
        return "{} @ {} '{}'".format(self.instance_name, self.position, os.path.join(self.root, self.filename))

    @classmethod
    def instance_scan(cls, root, file, buf, offset, call_module):
        """Iterates over a buffer and yields Instance objects"""
        # See notes above on methodology.
        substrings = buf.split(';')
        sub_offset = 0
        for string in substrings:
            # Tacking a semicolon back on to help the match
            string += ';'
            print("Scanning string chunk: '{}'".format(string))
            # Stripping comments and replacing with spaces in order to preserve
            # locational information
            for comment in re.finditer(cls.SVCOMMENT_P, string):
                pad = ' '*len(comment.group())
                string = string[:comment.start()]+pad+string[comment.end():]
            print("Comment-free version: '{}'".format(string))
            for word in re.finditer(cls.WORD_P, string):
                print("Evaluating '{}'".format(word.group()))
                if word.group(1) not in cls.SVLOG_RESERVED_LIST:
                    s = re.search(cls.VLOG_INSTANCE_P, string[word.start(1):])
                    if s:
                        yield cls(
                            s.group(2),
                            s.group(1),
                            call_module,
                            root,
                            file,
                            offset + sub_offset + s.start(1)
                        )
                        break
            # Length of the substring, plus the semicolon that was removed
            # by split.
            sub_offset = len(string)


class EntityTreeItem:
    """Class that holds the item for an entity name."""

    def __init__(self):
        self.entities = []
        self.architectures = []
        self.components = []
        self.instances = []
        self.instance_used = []

start = timer()
entity_tree = {}

for root, dirs, files in os.walk("."):
    for file in files:
        # Filter out files.  We don't want instantiation template files (_inst)
        # or blackbox files (_bb).
        # TODO: Make this list more robust.
        if "_bb." not in file and "_inst." not in file:
            # Separate VHDL and Verilog paths here once more since the two
            # are handled differently.
            if file.lower().endswith(".vhd"):
                print("[{:13.6f}] VHDL Processing {}".format(timer()-start, os.path.join(root, file)))
                try:
                    with open(os.path.join(root, file)) as f_in:
                        buf = f_in.read()
                        for entity in VHDLEntity.entity_scan(root, file, buf):
                            print("Found {}".format(entity.name))
                            if entity.name not in entity_tree:
                                entity_tree[entity.name] = EntityTreeItem()
                            entity_tree[entity.name].entities.append(entity)
                        # Architecture and Instance Scans are linked in order
                        # to ensure that instances are linked to the correct
                        # architecture.
                        for arch in VHDLArchitecture.arch_scan(root, file, buf):
                            print("Found {} of {}".format(arch.name, arch.entity))
                            if arch.entity not in entity_tree:
                                entity_tree[arch.entity] = EntityTreeItem()
                            entity_tree[arch.entity].architectures.append(arch)
                            sub_buf = buf[arch.start:arch.end]
                            print("Processing {} region".format(arch.name))
                            for instance in VHDLInstance.instance_scan(root, file, sub_buf, arch.start, arch.entity, arch.name):
                                print("Found instance of {} named {}".format(instance.instance_entity, instance.instance_name))
                                if instance.instance_entity not in entity_tree:
                                    entity_tree[instance.instance_entity] = EntityTreeItem()
                                entity_tree[instance.instance_entity].instances.append(instance)
                                entity_tree[arch.entity].instance_used.append(instance)
                        # Components could be linked to architectures, but
                        # they may also be declared in packages so for now will
                        # split this out.
                        for component in VHDLComponent.component_scan(root, file, buf):
                            if component.name not in entity_tree:
                                entity_tree[component.name] = EntityTreeItem()
                            entity_tree[component.name].components.append(component)
                        print("")
                except UnicodeDecodeError:
                    # File is likely obfuscated binary
                    pass
            elif file.lower().endswith(".v") or file.lower().endswith(".sv"):
                print("[{:13.6f}] Verilog Processing {}".format(timer()-start, os.path.join(root, file)))
                try:
                    with open(os.path.join(root, file)) as f_in:
                        buf = f_in.read()
                        # Modules and instance scanning are linked as well
                        # since a buffer subset is used to scan for instances.
                        for module in SVModule.module_scan(root, file, buf):
                            print("\nFound module {}".format(module.name))
                            if module.name not in entity_tree:
                                entity_tree[module.name] = EntityTreeItem()
                            entity_tree[module.name].entities.append(module)
                            sub_buf = buf[module.start:module.end]
                            print("Processing {} region".format(module.name))
                            for instance in SVInstance.instance_scan(root, file, sub_buf, module.start, module.name):
                                print("Found instance of {} named {}".format(instance.instance_module, instance.instance_name))
                                if instance.instance_module not in entity_tree:
                                    entity_tree[instance.instance_module] = EntityTreeItem()
                                entity_tree[instance.instance_module].instances.append(instance)
                                entity_tree[module.name].instance_used.append(instance)
                        print("")
                except UnicodeDecodeError:
                    # File is likely obfuscated binary
                    pass

for name in sorted(entity_tree):
    print("Entity {}:".format(name))
    print("=========================")
    print("Declarations:")
    for entity in entity_tree[name].entities:
        print(entity)
    print("Architectures:")
    for arch in entity_tree[name].architectures:
        print(arch)
    print("Component Declarations:")
    for component in entity_tree[name].components:
        print(component)
    print("Where Used As Instance:")
    for instance in entity_tree[name].instances:
        print(instance)
    print("Instances Contained:")
    for instance in entity_tree[name].instance_used:
        print(instance)
    print("")
