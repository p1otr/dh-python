# Copyright © 2010-2020 Piotr Ożarowski <piotr@debian.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import email
import logging
import platform
import os
import re
from functools import partial
from os.path import exists, isdir, join
from subprocess import PIPE, Popen

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.abspath(join(os.path.dirname(__file__), '..')))

from dhpython import PKG_PREFIX_MAP, PUBLIC_DIR_RE,\
    PYDIST_DIRS, PYDIST_OVERRIDES_FNAMES, PYDIST_DPKG_SEARCH_TPLS
from dhpython.version import get_requested_versions, Version
from dhpython.tools import memoize

log = logging.getLogger('dhpython')

PYDIST_RE = re.compile(r"""
    (?P<name>[A-Za-z][A-Za-z0-9_.\-]*)             # Python distribution name
    \s*
    (?P<vrange>(?:-?\d\.\d+(?:-(?:\d\.\d+)?)?)?) # version range
    \s*
    (?P<dependency>(?:[a-z][^;]*)?)              # Debian dependency
    (?:  # optional upstream version -> Debian version translator
        ;\s*
        (?P<standard>PEP386)?                    # PEP-386 mode
        \s*
        (?P<rules>(?:s|tr|y).*)?                 # translator rules
    )?
    """, re.VERBOSE)
REQUIRES_RE = re.compile(r'''
    (?P<name>[A-Za-z][A-Za-z0-9_.]*)     # Python distribution name
    \s*
    (?P<enabled_extras>(?:\[[^\]]*\])?)  # ignored for now
    \s*
    \(?  # optional parenthesis
    (?:  # optional minimum/maximum version
        (?P<operator><=?|>=?|==|!=|~=)
        \s*
        (?P<version>(\w|[-.])+)
        (?:  # optional interval minimum/maximum version
            \s*
            ,
            \s*
            (?P<operator2><=?|>=?|==|!=)
            \s*
            (?P<version2>(\w|[-.])+)
        )?
    )?
    \)?  # optional closing parenthesis
    \s*
    (?:;  # optional environment markers
        \s*
        (?P<environment_marker>[a-z_]+)
        \s*
        (?P<environment_marker_op><=?|>=?|[=!~]=|===)
        \s*
        (?P<environment_marker_quote>['"])
        (?P<environment_marker_value>.*)
        (?P=environment_marker_quote)
    )?
    ''', re.VERBOSE)
EXTRA_RE = re.compile(r'''
    ;
    \s*
    extra
    \s*
    ==
    \s*
    (?P<quote>['"])
    (?P<section>[a-zA-Z0-9-_.]+)
    (?P=quote)
    ''', re.VERBOSE)
REQ_SECTIONS_RE = re.compile(r'''
    ^
    \[
    (?P<section>[a-zA-Z0-9-_.]+)?
    \s*
    (?::
        \s*
        (?P<environment_marker>[a-z_]+)
        \s*
        (?P<environment_marker_op><=?|>=?|[=!~]=|===)
        \s*
        (?P<environment_marker_quote>['"])
        (?P<environment_marker_value>.*)
        (?P=environment_marker_quote)
        \s*
    )?
    \]
    \s*
    $
    ''', re.VERBOSE)
DEB_VERS_OPS = {
    '==': '=',
    '<':  '<<',
    '>':  '>>',
    '~=': '>=',
}


def validate(fpath):
    """Check if pydist file looks good."""
    with open(fpath, encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            if not PYDIST_RE.match(line):
                log.error('invalid pydist data in file %s: %s',
                          fpath.rsplit('/', 1)[-1], line)
                return False
    return True


@memoize
def load(impl):
    """Load iformation about installed Python distributions.

    :param impl: interpreter implementation, f.e. cpython2, cpython3, pypy
    :type impl: str
    """
    fname = PYDIST_OVERRIDES_FNAMES.get(impl)
    if exists(fname):
        to_check = [fname]  # first one!
    else:
        to_check = []

    dname = PYDIST_DIRS.get(impl)
    if isdir(dname):
        to_check.extend(join(dname, i) for i in os.listdir(dname))

    fbname = '/usr/share/dh-python/dist/{}_fallback'.format(impl)
    if exists(fbname):  # fall back generated at dh-python build time
        to_check.append(fbname)  # last one!

    result = {}
    for fpath in to_check:
        with open(fpath, encoding='utf-8') as fp:
            for line in fp:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                dist = PYDIST_RE.search(line)
                if not dist:
                    raise Exception('invalid pydist line: %s (in %s)' % (line, fpath))
                dist = dist.groupdict()
                name = safe_name(dist['name'])
                dist['versions'] = get_requested_versions(impl, dist['vrange'])
                dist['dependency'] = dist['dependency'].strip()
                if dist['rules']:
                    dist['rules'] = dist['rules'].split(';')
                else:
                    dist['rules'] = []
                result.setdefault(name, []).append(dist)
    return result


def guess_dependency(impl, req, version=None, bdep=None,
                     accept_upstream_versions=False):
    bdep = bdep or {}
    log.debug('trying to find dependency for %s (python=%s)',
              req, version)
    if isinstance(version, str):
        version = Version(version)

    # some upstreams have weird ideas for distribution name...
    name, rest = re.compile('([^!><=~ \(\)\[;]+)(.*)').match(req).groups()
    # TODO: check stdlib and dist-packaged for name.py and name.so files
    req = safe_name(name) + rest

    data = load(impl)
    req_d = REQUIRES_RE.match(req)
    if not req_d:
        log.info('please ask dh_python3 author to fix REQUIRES_RE '
                 'or your upstream author to fix requires.txt')
        raise Exception('requirement is not valid: %s' % req)
    req_d = req_d.groupdict()
    name = req_d['name']
    details = data.get(name.lower())
    env_marker_alts = ''
    if details:
        for item in details:
            if version and version not in item.get('versions', version):
                # rule doesn't match version, try next one
                continue

            env_marker_alts = ''
            if req_d['environment_marker']:
                action = check_environment_marker_restrictions(
                    req,
                    req_d['environment_marker'],
                    req_d['environment_marker_op'],
                    req_d['environment_marker_value'])
                if action is False:
                    return
                elif action is True:
                    pass
                else:
                    env_marker_alts = ' ' + action

            if not item['dependency']:
                return  # this requirement should be ignored
            if item['dependency'].endswith(')'):
                # no need to translate versions if version is hardcoded in
                # Debian dependency
                return item['dependency'] + env_marker_alts
            if req_d['version'] and (item['standard'] or item['rules']) and\
                    req_d['operator'] not in (None, '!='):
                o = _translate_op(req_d['operator'])
                v = _translate(req_d['version'], item['rules'], item['standard'])
                d = "%s (%s %s)%s" % (
                    item['dependency'], o, v, env_marker_alts)
                if req_d['version2'] and req_d['operator2'] not in (None,'!='):
                    o2 = _translate_op(req_d['operator2'])
                    v2 = _translate(req_d['version2'], item['rules'], item['standard'])
                    d += ", %s (%s %s)%s" % (
                        item['dependency'], o2, v2, env_marker_alts)
                elif req_d['operator'] == '~=':
                    o2 = '<<'
                    v2 = _translate(_max_compatible(req_d['version']), item['rules'], item['standard'])
                    d += ", %s (%s %s)%s" % (
                        item['dependency'], o2, v2, env_marker_alts)
                return d
            elif accept_upstream_versions and req_d['version'] and \
                    req_d['operator'] not in (None,'!='):
                o = _translate_op(req_d['operator'])
                d = "%s (%s %s)%s" % (
                    item['dependency'], o, req_d['version'], env_marker_alts)
                if req_d['version2'] and req_d['operator2'] not in (None,'!='):
                    o2 = _translate_op(req_d['operator2'])
                    d += ", %s (%s %s)%s" % (
                        item['dependency'], o2, req_d['version2'],
                        env_marker_alts)
                elif req_d['operator'] == '~=':
                    o2 = '<<'
                    d += ", %s (%s %s)%s" % (
                        item['dependency'], o2,
                        _max_compatible(req_d['version']), env_marker_alts)
                return d
            else:
                if item['dependency'] in bdep:
                    if None in bdep[item['dependency']] and bdep[item['dependency']][None]:
                        return "{} ({}){}".format(
                            item['dependency'], bdep[item['dependency']][None],
                            env_marker_alts)
                    # if arch in bdep[item['dependency']]:
                    # TODO: handle architecture specific dependencies from build depends
                    #       (current architecture is needed here)
                return item['dependency'] + env_marker_alts

    # search for Egg metadata file or directory (using dpkg -S)
    dpkg_query_tpl, regex_filter = PYDIST_DPKG_SEARCH_TPLS[impl]
    dpkg_query = dpkg_query_tpl.format(ci_regexp(safe_name(name)))

    log.debug("invoking dpkg -S %s", dpkg_query)
    process = Popen(('/usr/bin/dpkg', '-S', dpkg_query),
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        result = set()
        stdout = str(stdout, 'utf-8')
        for line in stdout.split('\n'):
            if not line.strip():
                continue
            pkg, path = line.split(':', 1)
            if regex_filter and not re.search(regex_filter, path):
                continue
            result.add(pkg)
        if len(result) > 1:
            log.error('more than one package name found for %s dist', name)
        elif not result:
            log.debug('dpkg -S did not find package for %s', name)
        else:
            return result.pop() + env_marker_alts
    else:
        log.debug('dpkg -S did not find package for %s: %s', name, stderr)

    pname = sensible_pname(impl, name)
    log.info('Cannot find package that provides %s. '
             'Please add package that provides it to Build-Depends or '
             'add "%s %s" line to %s or add proper '
             'dependency to Depends by hand and ignore this info.',
             name, safe_name(name), pname, PYDIST_OVERRIDES_FNAMES[impl])
    # return pname


def check_environment_marker_restrictions(req, marker, op, value):
    """Check wither we should include or skip a dependency based on its
    environment markers.

    Returns: True  - to keep a dependency
             False - to skip it
             str   - to append "| foo" to generated dependencies
    """
    # TODO: Replace with an AST that can handle complex logic
    if ' or ' in value or ' and ' in value:
        log.info('Ignoring complex environment marker: %s', req)
        return False

    # TODO: Use dynamic values when building arch-dependent
    # binaries, otherwise static values
    # TODO: Hurd values?
    supported_values = {
        'implementation_name': ('cpython', 'pypy'),
        'os_name': ('posix',),
        'platform_system': ('GNU/kFreeBSD', 'Linux'),
        'platform_machine': (platform.machine(),),
        'platform_python_implementation': ('CPython', 'PyPy'),
        'sys_platform': (
            'gnukfreebsd8', 'gnukfreebsd9', 'gnukfreebsd10',
            'gnukfreebsd11', 'gnukfreebsd12', 'gnukfreebsd13',
            'linux'),
    }
    if marker in supported_values:
        sv = supported_values[marker]
        if op in ('==', '!='):
            if ((op == '==' and value not in sv)
                    or (op == '!=' and value in sv)):
                log.debug('Skipping requirement (%s != %s): %s',
                          value, sv, req)
                return False
        else:
            log.info(
                'Skipping requirement with unhandled environment marker '
                'comparison: %s', req)
            return False

    elif marker in ('python_version', 'python_full_version',
                        'implementation_version'):
        env_ver = value
        int_ver = value.split('.')
        if marker == 'python_version':
            version_parts = 2
        elif marker == 'python_full_version':
            version_parts = 3
        else:
            version_parts = len(int_ver)

        if '*' in env_ver:
            if int_ver.index('*') != len(int_ver) -1:
                log.info('Skipping requirement with intermediate wildcard: %s',
                         req)
                return False
            int_ver.pop()
            env_ver = '.'.join(int_ver)
            if op == '==':
                if marker == 'python_full_version':
                    marker = 'python_version'
                    version_parts = 2
                else:
                    op == '=~'
            elif op == '!=':
                if marker == 'python_full_version':
                    marker = 'python_version'
                    version_parts = 2
                else:
                    log.info('Ignoring wildcard != requirement, not '
                             'representable in Debian: %s', req)
                    return True
            else:
                log.info('Skipping requirement with %s on a wildcard: %s',
                         op, req)
                return False

        int_ver = [int(x) for x in int_ver]
        if len(int_ver) < version_parts:
            int_ver.append(0)
            env_ver += '.0'
        next_ver = int_ver.copy()
        next_ver[version_parts - 1] += 1
        next_ver = '.'.join(str(x) for x in next_ver)
        prev_ver = int_ver.copy()
        prev_ver[version_parts - 1] -= 1
        prev_ver = '.'.join(str(x) for x in prev_ver)

        if op == '<':
            return '| python3 (>> {})'.format(env_ver)
        elif op == '<=':
            return '| python3 (>> {})'.format(next_ver)
        elif op == '>=':
            return '| python3 (<< {})'.format(env_ver)
        elif op == '>':
            return '| python3 (<< {})'.format(next_ver)
        elif op in ('==', '==='):
            # === is arbitrary equality (PEP 440)
            if marker == 'python_version' or op == '==':
                return '| python3 (<< {}) | python3 (>> {})'.format(
                        env_ver, next_ver)
            else:
                log.info(
                    'Skipping requirement with %s environment marker, cannot '
                    'model in Debian deps: %s', op, req)
                return False
        elif op == '~=':  # Compatible equality (PEP 440)
            ceq_next_ver = int_ver[:2]
            ceq_next_ver[1] += 1
            ceq_next_ver = '.'.join(str(x) for x in ceq_next_ver)
            return '| python3 (<< {}) | python3 (>> {})'.format(
                    env_ver, ceq_next_ver)
        elif op == '!=':
            log.info('Ignoring != comparison in environment marker, cannot '
                     'model in Debian deps: %s', req)
            return True

    elif marker == 'extra':
        # Handled in section logic of parse_requires_dist()
        return True
    else:
        log.info('Skipping requirement with unknown environment marker: %s',
                 marker)
        return False
    return True


def parse_pydep(impl, fname, bdep=None, options=None,
                depends_sec=None, recommends_sec=None, suggests_sec=None):
    depends_sec = depends_sec or []
    recommends_sec = recommends_sec or []
    suggests_sec = suggests_sec or []

    public_dir = PUBLIC_DIR_RE[impl].match(fname)
    ver = None
    if public_dir and public_dir.groups() and len(public_dir.group(1)) != 1:
        ver = public_dir.group(1)

    guess_deps = partial(guess_dependency, impl=impl, version=ver, bdep=bdep,
                         accept_upstream_versions=getattr(
                             options, 'accept_upstream_versions', False))

    result = {'depends': [], 'recommends': [], 'suggests': []}
    modified = section = False
    env_action = True
    processed = []
    with open(fname, 'r', encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            if not line or line.startswith('#'):
                processed.append(line)
                continue
            if line.startswith('['):
                m = REQ_SECTIONS_RE.match(line)
                section = m.group('section')
                env_action = True
                if m.group('environment_marker'):
                    env_action = check_environment_marker_restrictions(
                        line,
                        m.group('environment_marker'),
                        m.group('environment_marker_op'),
                        m.group('environment_marker_value'))
                processed.append(line)
                continue
            if section:
                if section in depends_sec:
                    result_key = 'depends'
                elif section in recommends_sec:
                    result_key = 'recommends'
                elif section in suggests_sec:
                    result_key = 'suggests'
                else:
                    processed.append(line)
                    continue
            else:
                result_key = 'depends'

            dependency = guess_deps(req=line)
            if env_action is False:
                dependency = None
            elif isinstance(env_action, str):
                dependency = ', '.join(
                    part.strip() + ' ' + env_action
                    for part in dependency.split(','))

            if dependency:
                result[result_key].append(dependency)
                modified = True
            else:
                processed.append(line)
    if modified and public_dir:
        with open(fname, 'w', encoding='utf-8') as fp:
            fp.writelines(i + '\n' for i in processed)
    return result


def parse_requires_dist(impl, fname, bdep=None, options=None, depends_sec=None,
                        recommends_sec=None, suggests_sec=None):
    """Extract dependencies from a dist-info/METADATA file"""
    depends_sec = depends_sec or []
    recommends_sec = recommends_sec or []
    suggests_sec = suggests_sec or []

    public_dir = PUBLIC_DIR_RE[impl].match(fname)
    ver = None
    if public_dir and public_dir.groups() and len(public_dir.group(1)) != 1:
        ver = public_dir.group(1)

    guess_deps = partial(guess_dependency, impl=impl, version=ver, bdep=bdep,
                         accept_upstream_versions=getattr(
                             options, 'accept_upstream_versions', False))
    result = {'depends': [], 'recommends': [], 'suggests': []}
    section = None
    with open(fname, 'r', encoding='utf-8') as fp:
        metadata = email.message_from_string(fp.read())
    requires = metadata.get_all('Requires-Dist', [])
    for req in requires:
        m = EXTRA_RE.search(req)
        if m:
            section = m.group('section')
        if section:
            if section in depends_sec:
                result_key = 'depends'
            elif section in recommends_sec:
                result_key = 'recommends'
            elif section in suggests_sec:
                result_key = 'suggests'
            else:
                continue
        else:
            result_key = 'depends'
        dependency = guess_deps(req=req)
        if dependency:
            result[result_key].append(dependency)
    return result


def safe_name(name):
    """Emulate distribute's safe_name."""
    return re.compile('[^A-Za-z0-9.]+').sub('_', name).lower()


def sensible_pname(impl, egg_name):
    """Guess Debian package name from Egg name."""
    egg_name = safe_name(egg_name).replace('_', '-')
    if egg_name.startswith('python-'):
        egg_name = egg_name[7:]
    return '{}-{}'.format(PKG_PREFIX_MAP[impl], egg_name.lower())


def ci_regexp(name):
    """Return case insensitive dpkg -S regexp."""
    return ''.join("[%s%s]" % (i.upper(), i) if i.isalpha() else i for i in name.lower())


PRE_VER_RE = re.compile(r'[-.]?(alpha|beta|rc|dev|a|b|c)')
GROUP_RE = re.compile(r'\$(\d+)')


def _pl2py(pattern):
    """Convert Perl RE patterns used in uscan to Python's

    >>> print(_pl2py('foo$3'))
    foo\g<3>
    """
    return GROUP_RE.sub(r'\\g<\1>', pattern)


def _max_compatible(version):
    """Return the maximum version compatible with `version` in PEP440 terms,
    used by ~= requires version specifiers.

    https://www.python.org/dev/peps/pep-0440/#compatible-release

    >>> _max_compatible('2.2')
    '3'
    >>> _max_compatible('1.4.5')
    '1.5'
    >>> _max_compatible('1.3.alpha4')
    '2'
    >>> _max_compatible('2.1.3.post5')
    '2.2'

    """
    v = Version(version)
    v.serial = None
    v.releaselevel = None
    if v.micro is not None:
        v.micro = None
        return str(v + 1)
    v.minor = None
    return str(v + 1)


def _translate(version, rules, standard):
    """Translate Python version into Debian one.

    >>> _translate('1.C2betac', ['s/c//gi'], None)
    '1.2beta'
    >>> _translate('5-fooa1.2beta3-fooD',
    ...     ['s/^/1:/', 's/-foo//g', 's:([A-Z]):+$1:'], 'PEP386')
    '1:5~a1.2~beta3+D'
    >>> _translate('x.y.x.z', ['tr/xy/ab/', 'y,z,Z,'], None)
    'a.b.a.Z'
    """
    for rule in rules:
        # uscan supports s, tr and y operations
        if rule.startswith(('tr', 'y')):
            # Note: no support for escaped separator in the pattern
            pos = 1 if rule.startswith('y') else 2
            tmp = rule[pos + 1:].split(rule[pos])
            version = version.translate(str.maketrans(tmp[0], tmp[1]))
        elif rule.startswith('s'):
            # uscan supports: g, u and x flags
            tmp = rule[2:].split(rule[1])
            pattern = re.compile(tmp[0])
            count = 1
            if tmp[2:]:
                flags = tmp[2]
                if 'g' in flags:
                    count = 0
                if 'i' in flags:
                    pattern = re.compile(tmp[0], re.I)
            version = pattern.sub(_pl2py(tmp[1]), version, count)
        else:
            log.warn('unknown rule ignored: %s', rule)
    if standard == 'PEP386':
        version = PRE_VER_RE.sub(r'~\g<1>', version)
    return version


def _translate_op(operator):
    """Translate Python version operator into Debian one.

    >>> _translate_op('==')
    '='
    >>> _translate_op('<')
    '<<'
    >>> _translate_op('<=')
    '<='
    """
    return DEB_VERS_OPS.get(operator, operator)


if __name__ == '__main__':
    impl = os.environ.get('IMPL', 'cpython3')
    for i in sys.argv[1:]:
        if os.path.isfile(i):
            try:
                print(', '.join(parse_pydep(impl, i)['depends']))
            except Exception as err:
                log.error('%s: cannot guess (%s)', i, err)
        else:
            try:
                print(guess_dependency(impl, i) or '')
            except Exception as err:
                log.error('%s: cannot guess (%s)', i, err)
