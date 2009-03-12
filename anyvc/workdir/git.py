"""
    git backend
    ----------------

    :copyright: 2007-2008 Ronny Pfannschmidt
    :license: LGPL2 or later
"""



from cmdbased import CommandBased
from cmdbased import relative_to
from file import StatedPath as Path
import re

class Git(CommandBased):
    """
    experimental
    copyed processing from http://www.geekfire.com/~alex/pida-git.py by alex
    """
    cmd = 'git'
    detect_subdir = '.git'

    state_map = {
        #XXX: sane mapping?!
        'H': 'clean', #git calls it cached (ie added to the index,
        'M': 'unmerged',
        'R': 'removed', #XXX: figure a way to decide
        'C': 'changed',
        'K': 'to be killed',
        '?': 'ignored',
        }

    cache_map = {
        'modified' : 'modified',
        'new file':  'added',
        'deleted' : 'removed',
    }

    def get_diff_args(self, paths=(), **kw):
        return ['diff', '--no-color'] + self.process_paths(paths)

    def process_paths(self, paths):
        return map(relative_to(self.base_path), paths)

    def get_commit_args(self, message, paths=(), **kw):
        if paths:
            # commit only for the supplied paths
            return ['commit', '-m', message, '--'] + list(self.process_paths(paths))
        else:
            # commit all found changes
            # this also adds all files not tracked and not in gitignore 
            # this also commits deletes ?!
            return ['commit', '-a', '-m', message]

    def get_revert_args(self, paths=(), recursive=False, **kw):
        return ['checkout','HEAD'] + self.process_paths(paths)

    def get_status_args(self, **kw):
        return ['ls-files',
                '-c', '-d', '-o',
                '-k', '-m', '-t',
                ]

    def parse_status_item(self, item, cache):
        state , name = item[0], item[2:].rstrip()
        return Path(name, self.state_map[state], self.base_path)

    
    def get_remove_args(self, paths=(), recursive=False, execute=False, **kw):
        return ['rm'] +  self.process_paths(paths)

    def get_rename_args(self, source, target):
        return ['mv', source, target]

    def cache_impl(self, recursive, **kw):
        """
        only runs caching if it knows, how
        """
        args = self.get_cache_args(**kw)
        if args:
            return self.execute_command(args, result_type=str, **kw)
        else:
            return []


    def get_cache_args(self, **kw):
        return ["status"]

    def parse_cache_items(self, items):
        untracked = re.search("include in what will be committed\)\n#\n(#\t[\w\.\-/]*\n)+",items)        
        index = re.search("to unstage\)\n#\n(#\t[\w\.\- :>/]*\n)+",items)        
        changed = re.search("update what will be committed\)\n#\n(#\t[\w\.\-: /]*\n)+",items)
        if untracked:
            state = 'unknown'
            for fn in re.findall("#\t([\w\.\-/]*)\n",untracked.group()):
                yield fn,state
        if changed:
            for state in re.findall("#\t([\w\.\-:/ ]*)",changed.group()):
                (state , fn ) = state.split(':')
                yield fn.strip(),self.cache_map[state.strip()]
        if index:
           for state in re.findall("#\t([\w\.\-:/> ]*)\n",index.group()):
                (state , fn ) = state.split(':')
                if  state == "renamed":
                    oldf,newf = fn.split('->')
                    yield newf.strip(),(state,oldf.strip())
                else:
                    yield fn.strip(),self.cache_map[state.strip()]

#        if not index and not untracked and not changed:
            
    def parse_status_items(self, items, cache):
        for item in items:
            state , name = item[0], item[2:].rstrip()
            if name in cache:
                if cache[name][0] == "renamed":
                    yield Path(name ,"added", self.base_path)
                    yield Path(cache[name][1], "removed", self.base_path)
                elif state != 'C':               
                    yield Path(name, cache[name], self.base_path)
            else:
                yield Path(name, self.state_map[state], self.base_path)



