#!/usr/bin/env python3
# pylint: disable=R0902,R0903,R0911,R0912,R0913,R0914,R0915,R0917,C0302
# Copyright(c) 2025: Mauro Carvalho Chehab <mchehab@kernel.org>.
# SPDX-License-Identifier: GPL-2.0

"""
Parse ABI documentation and produce results from it.
"""

import argparse
import logging
import os
import re
import sys

from concurrent import futures
from pprint import pformat
from random import randrange, seed, shuffle
from datetime import datetime

ABI_DIR = "Documentation/ABI/"

# Debug levels
DEBUG_WHAT_PARSING = 1
DEBUG_WHAT_OPEN = 2
DEBUG_DUMP_ABI_STRUCTS = 4
DEBUG_UNDEFINED = 8
DEBUG_REGEX = 16
DEBUG_SUBGROUP_MAP = 32
DEBUG_SUBGROUP_DICT = 64
DEBUG_SUBGROUP_SIZE = 128
DEBUG_GRAPH = 256

DEBUG_HELP = """
Print debug information according with the level(s),
which is given by the following bitmask:

1  - enable debug parsing logic
2  - enable debug messages on file open
4  - enable debug for ABI parse data
8  - enable extra debug information to identify troubles
     with ABI symbols found at the local machine that
     weren't found on ABI documentation (used only for
     undefined subcommand)
16 - enable debug for what to regex conversion
32 - enable debug for symbol regex subgroups
64 - enable debug for sysfs graph tree variable
"""


class AbiParser:
    """Main class to parse ABI files"""

    TAGS = r"(what|where|date|kernelversion|contact|description|users)"
    XREF = r"(?:^|\s|\()(\/(?:sys|config|proc|dev|kvd)\/[^,.:;\)\s]+)(?:[,.:;\)\s]|\Z)"

    def __init__(self, directory, logger=None,
                 enable_lineno=False, show_warnings=True, debug=0):
        """Stores arguments for the class and initialize class vars"""

        self.directory = directory
        self.enable_lineno = enable_lineno
        self.show_warnings = show_warnings
        self.debug = debug

        if not logger:
            self.log = logging.getLogger("get_abi")
        else:
            self.log = logger

        self.data = {}
        self.what_symbols = {}
        self.file_refs = {}
        self.what_refs = {}

        # Ignore files that contain such suffixes
        self.ignore_suffixes = (".rej", ".org", ".orig", ".bak", "~")

        # Regular expressions used on parser
        self.re_abi_dir = re.compile(r"(.*)" + ABI_DIR)
        self.re_tag = re.compile(r"(\S+)(:\s*)(.*)", re.I)
        self.re_valid = re.compile(self.TAGS)
        self.re_start_spc = re.compile(r"(\s*)(\S.*)")
        self.re_whitespace = re.compile(r"^\s+")

        # Regular used on print
        self.re_what = re.compile(r"(\/?(?:[\w\-]+\/?){1,2})")
        self.re_escape = re.compile(r"([\.\x01-\x08\x0e-\x1f\x21-\x2f\x3a-\x40\x7b-\xff])")
        self.re_unprintable = re.compile(r"([\x00-\x2f\x3a-\x40\x5b-\x60\x7b-\xff]+)")
        self.re_title_mark = re.compile(r"\n[\-\*\=\^\~]+\n")
        self.re_doc = re.compile(r"Documentation/(?!devicetree)(\S+)\.rst")
        self.re_abi = re.compile(r"(Documentation/ABI/)([\w\/\-]+)")
        self.re_xref_node = re.compile(self.XREF)

    def warn(self, fdata, msg, extra=None):
        """Displays a parse error if warning is enabled"""

        if not self.show_warnings:
            return

        msg = f"{fdata.fname}:{fdata.ln}: {msg}"
        if extra:
            msg += "\n\t\t" + extra

        self.log.warning(msg)

    def add_symbol(self, what, fname, ln=None, xref=None):
        """Create a reference table describing where each 'what' is located"""

        if what not in self.what_symbols:
            self.what_symbols[what] = {"file": {}}

        if fname not in self.what_symbols[what]["file"]:
            self.what_symbols[what]["file"][fname] = []

        if ln and ln not in self.what_symbols[what]["file"][fname]:
            self.what_symbols[what]["file"][fname].append(ln)

        if xref:
            self.what_symbols[what]["xref"] = xref

    def _parse_line(self, fdata, line):
        """Parse a single line of an ABI file"""

        new_what = False
        new_tag = False
        content = None

        match = self.re_tag.match(line)
        if match:
            new = match.group(1).lower()
            sep = match.group(2)
            content = match.group(3)

            match = self.re_valid.search(new)
            if match:
                new_tag = match.group(1)
            else:
                if fdata.tag == "description":
                    # New "tag" is actually part of description.
                    # Don't consider it a tag
                    new_tag = False
                elif fdata.tag != "":
                    self.warn(fdata, f"tag '{fdata.tag}' is invalid", line)

        if new_tag:
            # "where" is Invalid, but was a common mistake. Warn if found
            if new_tag == "where":
                self.warn(fdata, "tag 'Where' is invalid. Should be 'What:' instead")
                new_tag = "what"

            if new_tag == "what":
                fdata.space = None

                if content not in self.what_symbols:
                    self.add_symbol(what=content, fname=fdata.fname, ln=fdata.ln)

                if fdata.tag == "what":
                    fdata.what.append(content.strip("\n"))
                else:
                    if fdata.key:
                        if "description" not in self.data.get(fdata.key, {}):
                            self.warn(fdata, f"{fdata.key} doesn't have a description")

                        for w in fdata.what:
                            self.add_symbol(what=w, fname=fdata.fname,
                                            ln=fdata.what_ln, xref=fdata.key)

                    fdata.label = content
                    new_what = True

                    key = "abi_" + content.lower()
                    fdata.key = self.re_unprintable.sub("_", key).strip("_")

                    # Avoid duplicated keys but using a defined seed, to make
                    # the namespace identical if there aren't changes at the
                    # ABI symbols
                    seed(42)

                    while fdata.key in self.data:
                        char = randrange(0, 51) + ord("A")
                        if char > ord("Z"):
                            char += ord("a") - ord("Z") - 1

                        fdata.key += chr(char)

                    if fdata.key and fdata.key not in self.data:
                        self.data[fdata.key] = {
                            "what": [content],
                            "file": [fdata.file_ref],
                            "path": fdata.ftype,
                            "line_no": fdata.ln,
                        }

                    fdata.what = self.data[fdata.key]["what"]

                self.what_refs[content] = fdata.key
                fdata.tag = new_tag
                fdata.what_ln = fdata.ln

                if fdata.nametag["what"]:
                    t = (content, fdata.key)
                    if t not in fdata.nametag["symbols"]:
                        fdata.nametag["symbols"].append(t)

                return

            if fdata.tag and new_tag:
                fdata.tag = new_tag

                if new_what:
                    fdata.label = ""

                    if "description" in self.data[fdata.key]:
                        self.data[fdata.key]["description"] += "\n\n"

                    if fdata.file_ref not in self.data[fdata.key]["file"]:
                        self.data[fdata.key]["file"].append(fdata.file_ref)

                    if self.debug == DEBUG_WHAT_PARSING:
                        self.log.debug("what: %s", fdata.what)

                if not fdata.what:
                    self.warn(fdata, "'What:' should come first:", line)
                    return

                if new_tag == "description":
                    fdata.space = None

                    if content:
                        sep = sep.replace(":", " ")

                        c = " " * len(new_tag) + sep + content
                        c = c.expandtabs()

                        match = self.re_start_spc.match(c)
                        if match:
                            # Preserve initial spaces for the first line
                            fdata.space = match.group(1)
                            content = match.group(2) + "\n"

                self.data[fdata.key][fdata.tag] = content

            return

        # Store any contents before tags at the database
        if not fdata.tag and "what" in fdata.nametag:
            fdata.nametag["description"] += line
            return

        if fdata.tag == "description":
            content = line.expandtabs()

            if self.re_whitespace.sub("", content) == "":
                self.data[fdata.key][fdata.tag] += "\n"
                return

            if fdata.space is None:
                match = self.re_start_spc.match(content)
                if match:
                    # Preserve initial spaces for the first line
                    fdata.space = match.group(1)

                    content = match.group(2) + "\n"
            else:
                if content.startswith(fdata.space):
                    content = content[len(fdata.space):]

                else:
                    fdata.space = ""

            if fdata.tag == "what":
                w = content.strip("\n")
                if w:
                    self.data[fdata.key][fdata.tag].append(w)
            else:
                self.data[fdata.key][fdata.tag] += content
            return

        content = line.strip()
        if fdata.tag:
            if fdata.tag == "what":
                w = content.strip("\n")
                if w:
                    self.data[fdata.key][fdata.tag].append(w)
            else:
                self.data[fdata.key][fdata.tag] += "\n" + content.rstrip("\n")
            return

        # Everything else is error
        if content:
            self.warn(fdata, "Unexpected content", line)

    def parse_readme(self, nametag, fname):
        """Parse ABI README file"""

        nametag["what"] = ["ABI file contents"]
        nametag["path"] = "README"
        with open(fname, "r", encoding="utf8", errors="backslashreplace") as fp:
            for line in fp:
                match = self.re_tag.match(line)
                if match:
                    new = match.group(1).lower()

                    match = self.re_valid.search(new)
                    if match:
                        nametag["description"] += "\n:" + line
                        continue

                nametag["description"] += line

    def parse_file(self, fname, path, basename):
        """Parse a single file"""

        ref = f"abi_file_{path}_{basename}"
        ref = self.re_unprintable.sub("_", ref).strip("_")

        # Store per-file state into a namespace variable. This will be used
        # by the per-line parser state machine and by the warning function.
        fdata = argparse.Namespace

        fdata.fname = fname
        fdata.name = basename

        pos = fname.find(ABI_DIR)
        if pos > 0:
            f = fname[pos:]
        else:
            f = fname

        fdata.file_ref = (f, ref)
        self.file_refs[f] = ref

        fdata.ln = 0
        fdata.what_ln = 0
        fdata.tag = ""
        fdata.label = ""
        fdata.what = []
        fdata.key = None
        fdata.xrefs = None
        fdata.space = None
        fdata.ftype = path.split("/")[0]

        fdata.nametag = {}
        fdata.nametag["what"] = [f"ABI file {path}/{basename}"]
        fdata.nametag["type"] = "File"
        fdata.nametag["path"] = fdata.ftype
        fdata.nametag["file"] = [fdata.file_ref]
        fdata.nametag["line_no"] = 1
        fdata.nametag["description"] = ""
        fdata.nametag["symbols"] = []

        self.data[ref] = fdata.nametag

        if self.debug & DEBUG_WHAT_OPEN:
            self.log.debug("Opening file %s", fname)

        if basename == "README":
            self.parse_readme(fdata.nametag, fname)
            return

        with open(fname, "r", encoding="utf8", errors="backslashreplace") as fp:
            for line in fp:
                fdata.ln += 1

                self._parse_line(fdata, line)

            if "description" in fdata.nametag:
                fdata.nametag["description"] = fdata.nametag["description"].lstrip("\n")

            if fdata.key:
                if "description" not in self.data.get(fdata.key, {}):
                    self.warn(fdata, f"{fdata.key} doesn't have a description")

                for w in fdata.what:
                    self.add_symbol(what=w, fname=fname, xref=fdata.key)

    def _parse_abi(self, root=None):
        """Internal function to parse documentation ABI recursively"""

        if not root:
            root = self.directory

        with os.scandir(root) as obj:
            for entry in obj:
                name = os.path.join(root, entry.name)

                if entry.is_dir():
                    self._parse_abi(name)
                    continue

                if not entry.is_file():
                    continue

                basename = os.path.basename(name)

                if basename.startswith("."):
                    continue

                if basename.endswith(self.ignore_suffixes):
                    continue

                path = self.re_abi_dir.sub("", os.path.dirname(name))

                self.parse_file(name, path, basename)

    def parse_abi(self, root=None):
        """Parse documentation ABI"""

        self._parse_abi(root)

        if self.debug & DEBUG_DUMP_ABI_STRUCTS:
            self.log.debug(pformat(self.data))

    def desc_txt(self, desc):
        """Print description as found inside ABI files"""

        desc = desc.strip(" \t\n")

        return desc + "\n\n"

    def xref(self, fname):
        """
        Converts a Documentation/ABI + basename into a ReST cross-reference
        """

        xref = self.file_refs.get(fname)
        if not xref:
            return None
        else:
            return xref

    def desc_rst(self, desc):
        """Enrich ReST output by creating cross-references"""

        # Remove title markups from the description
        # Having titles inside ABI files will only work if extra
        # care would be taken in order to strictly follow the same
        # level order for each markup.
        desc = self.re_title_mark.sub("\n\n", "\n" + desc)
        desc = desc.rstrip(" \t\n").lstrip("\n")


        # FIXME: Python's regex performance for non-compiled expressions
        # is a lot worse than Perl, as Perl automatically caches them at their
        # first usage. Here, we'll need to do the same, as otherwise the
        # performance penalty is be high

        new_desc = ""
        for d in desc.split("\n"):
            if d == "":
                new_desc += "\n"
                continue

            # Use cross-references for doc files where needed
            d = self.re_doc.sub(r":doc:`/\1`", d)

            # Use cross-references for ABI generated docs where needed
            matches = self.re_abi.findall(d)
            for m in matches:
                abi = m[0] + m[1]

                xref = self.file_refs.get(abi)
                if not xref:
                    # This may happen if ABI is on a separate directory,
                    # like parsing ABI testing and symbol is at stable.
                    # The proper solution is to move this part of the code
                    # for it to be inside sphinx/kernel_abi.py
                    self.log.info("Didn't find ABI reference for '%s'", abi)
                else:
                    new = self.re_escape.sub(r"\\\1", m[1])
                    d = re.sub(fr"\b{abi}\b", f":ref:`{new} <{xref}>`", d)

            # Seek for cross reference symbols like /sys/...
            # Need to be careful to avoid doing it on a code block
            if d[0] not in [" ", "\t"]:
                matches = self.re_xref_node.findall(d)
                for m in matches:
                    # Finding ABI here is more complex due to wildcards
                    xref = self.what_refs.get(m)
                    if xref:
                        new = self.re_escape.sub(r"\\\1", m)
                        d = re.sub(fr"\b{m}\b", f":ref:`{new} <{xref}>`", d)

            new_desc += d + "\n"

        return new_desc + "\n\n"

    def doc(self, output_in_txt=False, show_symbols=True, show_file=True,
            filter_path=None):
        """Print ABI at stdout"""

        part = None
        for key, v in sorted(self.data.items(),
                             key=lambda x: (x[1].get("type", ""),
                                            x[1].get("what"))):

            wtype = v.get("type", "Symbol")
            file_ref = v.get("file")
            names = v.get("what", [""])

            if wtype == "File":
                if not show_file:
                    continue
            else:
                if not show_symbols:
                    continue

            if filter_path:
                if v.get("path") != filter_path:
                    continue

            msg = ""

            if wtype != "File":
                cur_part = names[0]
                if cur_part.find("/") >= 0:
                    match = self.re_what.match(cur_part)
                    if match:
                        symbol = match.group(1).rstrip("/")
                        cur_part = "Symbols under " + symbol

                if cur_part and cur_part != part:
                    part = cur_part
                    msg += f"{part}\n{"-" * len(part)}\n\n"

                msg += f".. _{key}:\n\n"

                max_len = 0
                for i in range(0, len(names)):           # pylint: disable=C0200
                    names[i] = "**" + self.re_escape.sub(r"\\\1", names[i]) + "**"

                    max_len = max(max_len, len(names[i]))

                msg += "+-" + "-" * max_len + "-+\n"
                for name in names:
                    msg += f"| {name}" + " " * (max_len - len(name)) + " |\n"
                    msg += "+-" + "-" * max_len + "-+\n"
                msg += "\n"

            for ref in file_ref:
                if wtype == "File":
                    msg += f".. _{ref[1]}:\n\n"
                else:
                    base = os.path.basename(ref[0])
                    msg += f"Defined on file :ref:`{base} <{ref[1]}>`\n\n"

            if wtype == "File":
                msg += f"{names[0]}\n{"-" * len(names[0])}\n\n"

            desc = v.get("description")
            if not desc and wtype != "File":
                msg += f"DESCRIPTION MISSING for {names[0]}\n\n"

            if desc:
                if output_in_txt:
                    msg += self.desc_txt(desc)
                else:
                    msg += self.desc_rst(desc)

            symbols = v.get("symbols")
            if symbols:
                msg += "Has the following ABI:\n\n"

                for w, label in symbols:
                    # Escape special chars from content
                    content = self.re_escape.sub(r"\\\1", w)

                    msg += f"- :ref:`{content} <{label}>`\n\n"

            users = v.get("users")
            if users and users.strip(" \t\n"):
                msg += f"Users:\n\t{users.strip("\n").replace('\n', '\n\t')}\n\n"

            ln = v.get("line_no", 1)

            yield (msg, file_ref[0][0], ln)

    def check_issues(self):
        """Warn about duplicated ABI entries"""

        for what, v in self.what_symbols.items():
            files = v.get("file")
            if not files:
                # Should never happen if the parser works properly
                self.log.warning("%s doesn't have a file associated", what)
                continue

            if len(files) == 1:
                continue

            f = []
            for fname, lines in sorted(files.items()):
                if not lines:
                    f.append(f"{fname}")
                elif len(lines) == 1:
                    f.append(f"{fname}:{lines[0]}")
                else:
                    f.append(f"{fname} lines {", ".join(str(x) for x in lines)}")

            self.log.warning("%s is defined %d times: %s", what, len(f), "; ".join(f))

    def search_symbols(self, expr):
        """ Searches for ABI symbols """

        regex = re.compile(expr, re.I)

        found_keys = 0
        for t in sorted(self.data.items(), key=lambda x: [0]):
            v = t[1]

            wtype = v.get("type", "")
            if wtype == "File":
                continue

            for what in v.get("what", [""]):
                if regex.search(what):
                    found_keys += 1

                    kernelversion = v.get("kernelversion", "").strip(" \t\n")
                    date = v.get("date", "").strip(" \t\n")
                    contact = v.get("contact", "").strip(" \t\n")
                    users = v.get("users", "").strip(" \t\n")
                    desc = v.get("description", "").strip(" \t\n")

                    files = []
                    for f in v.get("file", ()):
                        files.append(f[0])

                    what = str(found_keys) + ". " + what
                    title_tag = "-" * len(what)

                    print(f"\n{what}\n{title_tag}\n")

                    if kernelversion:
                        print(f"Kernel version:\t\t{kernelversion}")

                    if date:
                        print(f"Date:\t\t\t{date}")

                    if contact:
                        print(f"Contact:\t\t{contact}")

                    if users:
                        print(f"Users:\t\t\t{users}")

                    print(f"Defined on file{'s'[:len(files) ^ 1]}:\t{", ".join(files)}")

                    if desc:
                        print(f"\n{desc.strip("\n")}\n")

        if not found_keys:
            print(f"Regular expression /{expr}/ not found.")


class AbiRegex(AbiParser):
    """Extends AbiParser to search ABI nodes with regular expressions"""

    # Escape only ASCII visible characters
    escape_symbols = r"([\x21-\x29\x2b-\x2d\x3a-\x40\x5c\x60\x7b-\x7e])"
    leave_others = "others"

    # Tuples with regular expressions to be compiled and replacement data
    re_whats = [
        # Drop escape characters that might exist
        (re.compile("\\\\"), ""),

        # Temporarily escape dot characters
        (re.compile(r"\."),  "\xf6"),

        # Temporarily change [0-9]+ type of patterns
        (re.compile(r"\[0\-9\]\+"),  "\xff"),

        # Temporarily change [\d+-\d+] type of patterns
        (re.compile(r"\[0\-\d+\]"),  "\xff"),
        (re.compile(r"\[0:\d+\]"),  "\xff"),
        (re.compile(r"\[(\d+)\]"),  "\xf4\\\\d+\xf5"),

        # Temporarily change [0-9] type of patterns
        (re.compile(r"\[(\d)\-(\d)\]"),  "\xf4\1-\2\xf5"),

        # Handle multiple option patterns
        (re.compile(r"[\{\<\[]([\w_]+)(?:[,|]+([\w_]+)){1,}[\}\>\]]"), r"(\1|\2)"),

        # Handle wildcards
        (re.compile(r"([^\/])\*"), "\\1\\\\w\xf7"),
        (re.compile(r"/\*/"), "/.*/"),
        (re.compile(r"/\xf6\xf6\xf6"), "/.*"),
        (re.compile(r"\<[^\>]+\>"), "\\\\w\xf7"),
        (re.compile(r"\{[^\}]+\}"), "\\\\w\xf7"),
        (re.compile(r"\[[^\]]+\]"), "\\\\w\xf7"),

        (re.compile(r"XX+"), "\\\\w\xf7"),
        (re.compile(r"([^A-Z])[XYZ]([^A-Z])"), "\\1\\\\w\xf7\\2"),
        (re.compile(r"([^A-Z])[XYZ]$"), "\\1\\\\w\xf7"),
        (re.compile(r"_[AB]_"), "_\\\\w\xf7_"),

        # Recover [0-9] type of patterns
        (re.compile(r"\xf4"), "["),
        (re.compile(r"\xf5"),  "]"),

        # Remove duplicated spaces
        (re.compile(r"\s+"), r" "),

        # Special case: drop comparison as in:
        # What: foo = <something>
        # (this happens on a few IIO definitions)
        (re.compile(r"\s*\=.*$"), ""),

        # Escape all other symbols
        (re.compile(escape_symbols), r"\\\1"),
        (re.compile(r"\\\\"), r"\\"),
        (re.compile(r"\\([\[\]\(\)\|])"), r"\1"),
        (re.compile(r"(\d+)\\(-\d+)"), r"\1\2"),

        (re.compile(r"\xff"), r"\\d+"),

        # Special case: IIO ABI which a parenthesis.
        (re.compile(r"sqrt(.*)"), r"sqrt(.*)"),

        # Simplify regexes with multiple .*
        (re.compile(r"(?:\.\*){2,}"),  ""),

        # Recover dot characters
        (re.compile(r"\xf6"), "\\."),
        # Recover plus characters
        (re.compile(r"\xf7"), "+"),
    ]
    re_has_num = re.compile(r"\\d")

    # Symbol name after escape_chars that are considered a devnode basename
    re_symbol_name =  re.compile(r"(\w|\\[\.\-\:])+$")

    # List of popular group names to be skipped to minimize regex group size
    # Use DEBUG_SUBGROUP_SIZE to detect those
    skip_names = set(["devices", "hwmon"])

    def regex_append(self, what, new):
        """
        Get a search group for a subset of regular expressions.

        As ABI may have thousands of symbols, using a for to search all
        regular expressions is at least O(n^2). When there are wildcards,
        the complexity increases substantially, eventually becoming exponential.

        To avoid spending too much time on them, use a logic to split
        them into groups. The smaller the group, the better, as it would
        mean that searches will be confined to a small number of regular
        expressions.

        The conversion to a regex subset is tricky, as we need something
        that can be easily obtained from the sysfs symbol and from the
        regular expression. So, we need to discard nodes that have
        wildcards.

        If it can't obtain a subgroup, place the regular expression inside
        a special group (self.leave_others).
        """

        for search_group in reversed(new.split("/")):
            if not search_group or search_group in self.skip_names:
                continue
            if self.re_symbol_name.match(search_group):
                break

        if not search_group:
            search_group = self.leave_others

        if self.debug & DEBUG_SUBGROUP_MAP:
            self.log.debug("%s: mapped as %s", what, search_group)

        try:
            if search_group not in self.regex_group:
                self.regex_group[search_group] = []

            self.regex_group[search_group].append(re.compile(new))
            if self.search_string:
                if what.find(self.search_string) >= 0:
                    print(f"What: {what}")
        except re.PatternError:
            self.log.warning("Ignoring '%s' as it produced an invalid regex:\n"
                             "           '%s'", what, new)

    def get_regexes(self, what):
        """
        Given an ABI devnode, return a list of all regular expressions that
        may match it, based on the sub-groups created by regex_append()
        """

        re_list = []

        patches = what.split("/")
        patches.reverse()
        patches.append(self.leave_others)

        for search_group in patches:
            if search_group in self.regex_group:
                re_list += self.regex_group[search_group]

        return re_list

    def __init__(self, *args, **kwargs):
        """
        Override init method to get verbose argument
        """

        self.regex_group = None
        self.search_string = None
        self.re_string = None

        if "search_string" in kwargs:
            self.search_string = kwargs.get("search_string")
            del kwargs["search_string"]

            if self.search_string:

                try:
                    self.re_string = re.compile(self.search_string)
                except re.PatternError as e:
                    msg = f"{self.search_string} is not a valid regular expression"
                    raise ValueError(msg) from e

        super().__init__(*args, **kwargs)

    def parse_abi(self, *args, **kwargs):

        super().parse_abi(*args, **kwargs)

        self.regex_group = {}

        print("Converting ABI What fields into regexes...", file=sys.stderr)

        for t in sorted(self.data.items(), key=lambda x: x[0]):
            v = t[1]
            if v.get("type") == "File":
                continue

            v["regex"] = []

            for what in v.get("what", []):
                if not what.startswith("/sys"):
                    continue

                new = what
                for r, s in self.re_whats:
                    try:
                        new = r.sub(s, new)
                    except re.PatternError as e:
                        # Help debugging troubles with new regexes
                        raise re.PatternError(f"{e}\nwhile re.sub('{r.pattern}', {s}, str)") from e

                v["regex"].append(new)

                if self.debug & DEBUG_REGEX:
                    self.log.debug("%-90s <== %s", new, what)

                # Store regex into a subgroup to speedup searches
                self.regex_append(what, new)

        if self.debug & DEBUG_SUBGROUP_DICT:
            self.log.debug("%s", pformat(self.regex_group))

        if self.debug & DEBUG_SUBGROUP_SIZE:
            biggestd_keys = sorted(self.regex_group.keys(),
                                   key= lambda k: len(self.regex_group[k]),
                                   reverse=True)

            print("Top regex subgroups:", file=sys.stderr)
            for k in biggestd_keys[:10]:
                print(f"{k} has {len(self.regex_group[k])} elements", file=sys.stderr)

class SystemSymbols:
    """Stores arguments for the class and initialize class vars"""

    def graph_add_file(self, path, link=None):
        """
        add a file path to the sysfs graph stored at self.root
        """

        if path in self.files:
            return

        name = ""
        ref = self.root
        for edge in path.split("/"):
            name += edge + "/"
            if edge not in ref:
                ref[edge] = {"__name": [name.rstrip("/")]}

            ref = ref[edge]

        if link and link not in ref["__name"]:
            ref["__name"].append(link.rstrip("/"))

        self.files.add(path)

    def print_graph(self, root_prefix="", root=None, level=0):
        """Prints a reference tree graph using UTF-8 characters"""

        if not root:
            root = self.root
            level = 0

        # Prevent endless traverse
        if level > 5:
            return

        if level > 0:
            prefix = "├──"
            last_prefix = "└──"
        else:
            prefix = ""
            last_prefix = ""

        items = list(root.items())

        names = root.get("__name", [])
        for k, edge in items:
            if k == "__name":
                continue

            if not k:
                k = "/"

            if len(names) > 1:
                k += " links: " + ",".join(names[1:])

            if edge == items[-1][1]:
                print(root_prefix + last_prefix + k)
                p = root_prefix
                if level > 0:
                    p += "   "
                self.print_graph(p, edge, level + 1)
            else:
                print(root_prefix + prefix + k)
                p = root_prefix + "│   "
                self.print_graph(p, edge, level + 1)

    def _walk(self, root):
        """
        Walk through sysfs to get all devnodes that aren't ignored.

        By default, uses /sys as sysfs mounting point. If another
        directory is used, it replaces them to /sys at the patches.
        """

        with os.scandir(root) as obj:
            for entry in obj:
                path = os.path.join(root, entry.name)
                if self.sysfs:
                    p = path.replace(self.sysfs, "/sys", count=1)
                else:
                    p = path

                if self.re_ignore.search(p):
                    return

                # Handle link first to avoid directory recursion
                if entry.is_symlink():
                    real = os.path.realpath(path)
                    if not self.sysfs:
                        self.aliases[path] = real
                    else:
                        real = real.replace(self.sysfs, "/sys", count=1)

                    # Add absfile location to graph if it doesn't exist
                    if not self.re_ignore.search(real):
                        # Add link to the graph
                        self.graph_add_file(real, p)

                elif entry.is_file():
                    self.graph_add_file(p)

                elif entry.is_dir():
                    self._walk(path)

    def __init__(self, abi, sysfs="/sys", hints=False):
        """
        Initialize internal variables and get a list of all files inside
        sysfs that can currently be parsed.

        Please notice that there are several entries on sysfs that aren't
        documented as ABI. Ignore those.

        The real paths will be stored under self.files. Aliases will be
        stored in separate, as self.aliases.
        """

        self.abi = abi
        self.log = abi.log

        if sysfs != "/sys":
            self.sysfs = sysfs.rstrip("/")
        else:
            self.sysfs = None

        self.hints = hints

        self.root = {}
        self.aliases = {}
        self.files = set()

        dont_walk = [
            # Those require root access and aren't documented at ABI
            f"^{sysfs}/kernel/debug",
            f"^{sysfs}/kernel/tracing",
            f"^{sysfs}/fs/pstore",
            f"^{sysfs}/fs/bpf",
            f"^{sysfs}/fs/fuse",

            # This is not documented at ABI
            f"^{sysfs}/module",

            f"^{sysfs}/fs/cgroup",  # this is big and has zero docs under ABI
            f"^{sysfs}/firmware",   # documented elsewhere: ACPI, DT bindings
            "sections|notes",       # aren't actually part of ABI

            # kernel-parameters.txt - not easy to parse
            "parameters",
        ]

        self.re_ignore = re.compile("|".join(dont_walk))

        print(f"Reading {sysfs} directory contents...", file=sys.stderr)
        self._walk(sysfs)

    def check_file(self, refs, found):
        """Check missing ABI symbols for a given sysfs file"""

        res_list = []

        try:
            for names in refs:
                fname = names[0]

                res = {
                    "found": False,
                    "fname": fname,
                    "msg": "",
                }
                res_list.append(res)

                re_what = self.abi.get_regexes(fname)
                if not re_what:
                    self.abi.log.warning(f"missing rules for {fname}")
                    continue

                for name in names:
                    for r in re_what:
                        if self.abi.debug & DEBUG_UNDEFINED:
                            self.log.debug("check if %s matches '%s'", name, r.pattern)
                        if r.match(name):
                            res["found"] = True
                            if found:
                                res["msg"] += f"  {fname}: regex:\n\t"
                            continue

                if self.hints and not res["found"]:
                    res["msg"] += f"  {fname} not found. Tested regexes:\n"
                    for r in re_what:
                        res["msg"] += "    " + r.pattern + "\n"

        except KeyboardInterrupt:
            pass

        return res_list

    def _ref_interactor(self, root):
        """Recursive function to interact over the sysfs tree"""

        for k, v in root.items():
            if isinstance(v, dict):
                yield from self._ref_interactor(v)

            if root == self.root or k == "__name":
                continue

            if self.abi.re_string:
                fname = v["__name"][0]
                if self.abi.re_string.search(fname):
                    yield v
            else:
                yield v


    def get_fileref(self, all_refs, chunk_size):
        """Interactor to group refs into chunks"""

        n = 0
        refs = []

        for ref in all_refs:
            refs.append(ref)

            n += 1
            if n >= chunk_size:
                yield refs
                n = 0
                refs = []

        yield refs

    def check_undefined_symbols(self, max_workers=None, chunk_size=50,
                                found=None, dry_run=None):
        """Seach ABI for sysfs symbols missing documentation"""

        self.abi.parse_abi()

        if self.abi.debug & DEBUG_GRAPH:
            self.print_graph()

        all_refs = []
        for ref in self._ref_interactor(self.root):
            all_refs.append(ref["__name"])

        if dry_run:
            print(f"Would check", file=sys.stderr)
            for ref in all_refs:
                print(", ".join(ref))

            return

        print("Starting to search symbols (it may take several minutes):",
              file=sys.stderr)
        start = datetime.now()
        old_elapsed = None

        # Python doesn't support multithreading due to limitations on its
        # global lock (GIL). While Python 3.13 finally made GIL optional,
        # there are still issues related to it. Also, we want to have
        # backward compatibility with older versions of Python.
        #
        # So, use instead multiprocess. However, Python is very slow passing
        # data from/to multiple processes. Also, it may consume lots of memory
        # if the data to be shared is not small.  So, we need to group workload
        # in chunks that are big enough to generate performance gains while
        # not being so big that would cause out-of-memory.

        num_refs = len(all_refs)
        print(f"Number of references to parse: {num_refs}", file=sys.stderr)

        if not max_workers:
            max_workers = os.cpu_count()
        elif max_workers > os.cpu_count():
            max_workers = os.cpu_count()

        max_workers = max(max_workers, 1)

        max_chunk_size = int((num_refs + max_workers - 1) / max_workers)
        chunk_size = min(chunk_size, max_chunk_size)
        chunk_size = max(1, chunk_size)

        if max_workers > 1:
            executor = futures.ProcessPoolExecutor

            # Place references in a random order. This may help improving
            # performance, by mixing complex/simple expressions when creating
            # chunks
            shuffle(all_refs)
        else:
            # Python has a high overhead with processes. When there's just
            # one worker, it is faster to not create a new process.
            # Yet, User still deserves to have a progress print. So, use
            # python's "thread", which is actually a single process, using
            # an internal schedule to switch between tasks. No performance
            # gains for non-IO tasks, but still it can be quickly interrupted
            # from time to time to display progress.
            executor = futures.ThreadPoolExecutor

        not_found = []
        f_list = []
        with executor(max_workers=max_workers) as exe:
            for refs in self.get_fileref(all_refs, chunk_size):
                if refs:
                    try:
                        f_list.append(exe.submit(self.check_file, refs, found))

                    except KeyboardInterrupt:
                        return

            total = len(f_list)

            if not total:
                if self.abi.re_string:
                    print(f"No ABI symbol matches {self.abi.search_string}")
                else:
                    self.abi.log.warning("No ABI symbols found")
                return

            print(f"{len(f_list):6d} jobs queued on {max_workers} workers",
                  file=sys.stderr)

            while f_list:
                try:
                    t = futures.wait(f_list, timeout=1,
                                     return_when=futures.FIRST_COMPLETED)

                    done = t[0]

                    for fut in done:
                        res_list = fut.result()

                        for res in res_list:
                            if not res["found"]:
                                not_found.append(res["fname"])
                            if res["msg"]:
                                print(res["msg"])

                        f_list.remove(fut)
                except KeyboardInterrupt:
                    return

                except RuntimeError as e:
                    self.abi.log.warning(f"Future: {e}")
                    break

                if sys.stderr.isatty():
                    elapsed = str(datetime.now() - start).split(".", maxsplit=1)[0]
                    if len(f_list) < total:
                        elapsed += f" ({total - len(f_list)}/{total} jobs completed).  "
                    if elapsed != old_elapsed:
                        print(elapsed + "\r", end="", flush=True,
                              file=sys.stderr)
                        old_elapsed = elapsed

        elapsed = str(datetime.now() - start).split(".", maxsplit=1)[0]
        print(elapsed, file=sys.stderr)

        for f in sorted(not_found):
            print(f"{f} not found.")


REST_DESC = """
Produce output in ReST format.

The output is done on two sections:

- Symbols: show all parsed symbols in alphabetic order;
- Files: cross reference the content of each file with the symbols on it.
"""


class AbiRest:
    """Initialize an argparse subparser for rest output"""

    def __init__(self, subparsers):
        """Initialize argparse subparsers"""

        parser = subparsers.add_parser("rest",
                                       formatter_class=argparse.RawTextHelpFormatter,
                                       description=REST_DESC)

        parser.add_argument("--enable-lineno",  action="store_true",
                            help="enable lineno")
        parser.add_argument("--raw", action="store_true",
                            help="output text as contained in the ABI files. "
                                 "It not used, output will contain dynamically"
                                 " generated cross references when possible.")
        parser.add_argument("--no-file", action="store_true",
                            help="Don't show files section")
        parser.add_argument("--no-symbols", action="store_true",
                            help="Don't show symbols section")
        parser.add_argument("--filter",
                            help="Filter a section of ABI (e..g stable, testing, obsolete, removed)")
        parser.add_argument("--show-hints", help="Show-hints")

        parser.set_defaults(func=self.run)

    def run(self, args):
        """Run subparser"""

        parser = AbiParser(args.dir, debug=args.debug)
        parser.parse_abi()
        parser.check_issues()

        for t in parser.doc(args.raw, show_file=not args.no_file,
                            show_symbols=not args.no_symbols,
                            filter_path=args.filter):

            # As line number is returned at the tuple, artifically place
            # them as a comment tag if one wants to debug troubles there
            if args.enable_lineno:
                print (f".. LINENO {t[1]}#{t[2]}\n\n")

            print(t[0])


class AbiValidate:
    """Initialize an argparse subparser for ABI validation"""

    def __init__(self, subparsers):
        """Initialize argparse subparsers"""

        parser = subparsers.add_parser("validate",
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                       description="list events")

        parser.set_defaults(func=self.run)

    def run(self, args):
        """Run subparser"""

        parser = AbiParser(args.dir, debug=args.debug)
        parser.parse_abi()
        parser.check_issues()


class AbiSearch:
    """Initialize an argparse subparser for ABI search"""

    def __init__(self, subparsers):
        """Initialize argparse subparsers"""

        parser = subparsers.add_parser("search",
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                       description="Search ABI using a regular expression")

        parser.add_argument("expression",
                            help="Case-insensitive search pattern for the ABI symbol")

        parser.set_defaults(func=self.run)

    def run(self, args):
        """Run subparser"""

        parser = AbiParser(args.dir, debug=args.debug)
        parser.parse_abi()
        parser.search_symbols(args.expression)

UNDEFINED_DESC="""
Check undefined ABIs on local machine.

Read sysfs devnodes and check if the devnodes there are defined inside
ABI documentation.

The search logic tries to minimize the number of regular expressions to
search per each symbol.

By default, it runs on a single CPU, as Python support for CPU threads
is still experimental, and multi-process runs on Python is very slow.

On experimental tests, if the number of ABI symbols to search per devnode
is contained on a limit of ~150 regular expressions, using a single CPU
is a lot faster than using multiple processes. However, if the number of
regular expressions to check is at the order of ~30000, using multiple
CPUs speeds up the check.
"""

class AbiUndefined:
    """
    Initialize an argparse subparser for logic to check undefined ABI at
    the current machine's sysfs
    """

    def __init__(self, subparsers):
        """Initialize argparse subparsers"""

        parser = subparsers.add_parser("undefined",
                                       formatter_class=argparse.RawTextHelpFormatter,
                                       description=UNDEFINED_DESC)

        parser.add_argument("-S", "--sysfs-dir", default="/sys",
                            help="directory where sysfs is mounted")
        parser.add_argument("-s", "--search-string",
                            help="search string regular expression to limit symbol search")
        parser.add_argument("-H", "--show-hints", action="store_true",
                            help="Hints about definitions for missing ABI symbols.")
        parser.add_argument("-j", "--jobs", "--max-workers", type=int, default=1,
                            help="If bigger than one, enables multiprocessing.")
        parser.add_argument("-c", "--max-chunk-size", type=int, default=50,
                            help="Maximum number of chunk size")
        parser.add_argument("-f", "--found", action="store_true",
                            help="Also show found items. "
                                 "Helpful to debug the parser."),
        parser.add_argument("-d", "--dry-run", action="store_true",
                            help="Don't actually search for undefined. "
                                 "Helpful to debug the parser."),

        parser.set_defaults(func=self.run)

    def run(self, args):
        """Run subparser"""

        abi = AbiRegex(args.dir, debug=args.debug,
                       search_string=args.search_string)

        abi_symbols = SystemSymbols(abi=abi, hints=args.show_hints,
                                    sysfs=args.sysfs_dir)

        abi_symbols.check_undefined_symbols(dry_run=args.dry_run,
                                            found=args.found,
                                            max_workers=args.jobs,
                                            chunk_size=args.max_chunk_size)


def main():
    """Main program"""

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-d", "--debug", type=int, default=0, help="debug level")
    parser.add_argument("-D", "--dir", default=ABI_DIR, help=DEBUG_HELP)

    subparsers = parser.add_subparsers()

    AbiRest(subparsers)
    AbiValidate(subparsers)
    AbiSearch(subparsers)
    AbiUndefined(subparsers)

    args = parser.parse_args()

    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")

    if "func" in args:
        args.func(args)
    else:
        sys.exit(f"Please specify a valid command for {sys.argv[0]}")


REST_DESC = """
Produce output in ReST format.

The output is done on two sections:

- Symbols: show all parsed symbols in alphabetic order;
- Files: cross reference the content of each file with the symbols on it.
"""

# Call main method
if __name__ == "__main__":
    main()
