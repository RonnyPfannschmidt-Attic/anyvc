class Darcs(CommandBased):
    #TODO: ensure this really works in most cases
    #XXX: path processing?

    cmd = 'darcs'
    detect_subdir = '_darcs'

    def get_commit_args(self, message, paths=(), **kw):
        return ['record', '-a', '-m', message] + list(paths)

    def get_revert_args(self, paths=()):
        return ['revert', '-a'] + list(paths)

    def get_status_args(self, **kw):
        return ['whatsnew', '--boring', '--look-for-adds']

    state_map = {
        "a": 'unknown',
        "A": 'added',
        "M": 'modified',
        "C": 'conflict',
        "R": 'removed'
    }

    move_regex = re.compile(" (?P<removed>.*?) -> (?P<added>.*?)$")


    def parse_status_item(self, item, cache):
        if item.startswith('What') or item.startswith('No') or not item.strip():
            return
        match = self.move_regex.match(item)
        if match:
            return None, (match.group('removed'),  match.group('added'))

        elements = item.split(None, 2)[:2] #TODO: handle filenames with spaces
        state = self.state_map[elements[0]]
        file = os.path.normpath(elements[1])
        return state, file

    def get_rename_args(self, source, target):
        return ['mv', source, target]



