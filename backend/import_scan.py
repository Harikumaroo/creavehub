import os, sys, traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

fails = []
count = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    # skip migrations and __pycache__
    if 'migrations' in dirpath.split(os.sep):
        continue
    for fname in filenames:
        if not fname.endswith('.py'):
            continue
        if fname == '__init__.py':
            continue
        full = os.path.join(dirpath, fname)
        rel = os.path.relpath(full, ROOT)
        module = rel.replace(os.sep, '.')[:-3]
        count += 1
        try:
            __import__(module)
            print('OK', module)
        except Exception as e:
            print('FAIL', module, type(e).__name__, str(e))
            fails.append((module, traceback.format_exc()))

print('\nScanned', count, 'modules,', len(fails), 'failures')
if fails:
    for mod, tb in fails:
        print('---\nModule:', mod)
        print(tb)
    sys.exit(2)
