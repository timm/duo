## Sym Class

```py
from col import Col

class Sym(Col):
  def __init__(i,*l,**d):
    super().__init__(*l, **d)
    i.seen = {}
    i.mode, i.most = "",0
  def add1(i,x) :
    new = i.seen[x] = i.seen.get(x,0) + 1
    if new > i.most:
      i.most, i.mode = new, x
    return x
  def norm1(i,x):    return x
  def dist1(i, x,y): return 0 if x==y else 1
```  