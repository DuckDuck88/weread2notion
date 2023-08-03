import difflib


class DiffChecker:
    def __init__(self, path1, path2):
        self.path1 = path1
        self.path2 = path2

    def check(self):
        file1 = open(self.path1)
        file2 = open(self.path2)
        lines1 = file1.readlines()
        lines1 = list(map(lambda x: x.strip(), lines1))
        lines2 = file2.readlines()
        lines2 = list(map(lambda x: x.strip(), lines2))
        file1.close()
        file2.close()
        errors = 0
        for line in lines1:
            if (line not in lines2):
                print(f'<<<{line}')
                errors += 1
            else:
                ind = lines2.index(line)
                lines2.pop(ind)
        if (len(lines2) == 0 and errors == 0):
            print('the two filles are identical')
            return
        for line in lines2:
            print(f'>>>{line}')


if __name__ == '__main__':
    s1 = 'test1.txt'
    s2 = 'test2.txt'
    # checker = DiffChecker(s1, s2)
    # checker.check()
    d = difflib.HtmlDiff()
    diff = d.make_file(open(s1).readlines(), open(s2).readlines())
    d2 = difflib.Differ()
    diff2 = d2.compare(open(s1).readlines(), open(s2).readlines())
    with open('diff.html', 'w') as f:
        f.write(diff)
    print(''.join(diff2))
    diff3 = difflib.ndiff(open(s1).readlines(), open(s2).readlines())
    print(''.join(diff3))
