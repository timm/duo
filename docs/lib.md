```py
import traceback,re

class ok:
  tries,fails = 0,0  #  tracks the record so far
  def __init__(i,fun=None):
    def score(t,f): 
      return f"#TEST PASS = {t-f} FAIL = {f}"
    if not fun:     
      return print(score(ok.tries, ok.fails))
    try:
      ok.tries += 1
      print("### ",fun.__name__)
      fun()
      print(score(ok.tries, ok.fails),':',fun.__name__)
    except Exception:
      ok.fails += 1
      print(ok.fails,ok.tries)
      import traceback
      print(traceback.format_exc())
      print(score(ok.tries, ok.fails),':',fun.__name__)

def within(x,y,z):
  return y>= x and y <= z
```
# -------------------------------------------------
# some convenient iterators

```py
def source(x):
  def items(z):
    for y in z: yield y
  def strings(z):
    for y in z.splitlines(): yield y
  def csv(z):
    with open(z) as fp:
      for y in fp: yield y.strip()
  f = items
  if isinstance(x,str):
     f = csv if x[-3:]=='csv' else strings
  for z in f(x): yield z
```
# -------------------------------------------------
# error handling

```py
def now(t,m):
  if not t:
    sys.stderr.write('#E> '+str(m)+'\n')
    sys.exit()

def ins(lst,x):
  for y in lst:
    if y in x: return True
```
## Pretty print dictionaries
Show keys in sorted order, don't show 
hidden fields (those starting with "\_").

```py
def dprint(d, pre="",no="_"):
  def q(z):
    if isinstance(z,float): return "%5.3f" % z
    if callable(z): return "f(%s)" % z.__name__
    return str(z)
  l=sorted([(k,v) for k,v in d if k[0] != no])
  return pre+'{'+", ".join([('%s=%s' % (k,q(v))) 
                            for k,v in l]) +'}'
```

## Class that knows how to show off
```py
class Pretty:
  def __repr__(i):
    return dprint(i.__dict__.items(), 
                  i.__class__.__name__)
```

## Simple Structs
```py
class o(Pretty):
  def __init__(i,**d) : i.__dict__.update(**d)
```

Convert lines into lists, killing whitespace
and comments. skip over lines of the wrong size.

```py
def rows(src):
  linesize = None
  for n, line in enumerate(src):
    line = re.sub(r'([\n\t\r ]|#.*)','', line.strip())
    if line:
      line = line.split(",")
      if linesize is None:
        linesize = len(line)
      if len(line) == linesize:
        yield line
      else:
        now(False, "E> skipping line %s" % n)

def cols(src):
  todo = None
  for cells in src:
    todo = todo or [n for n, cell in enumerate(cells)
                    if not "?"in cell]
    yield [cells[n] for n in todo]
```
