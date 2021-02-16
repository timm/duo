#!/usr/bin/env python3
# vim: ts=2 sw=2 sts=2 et tw=81:
"""
DUO = data miners used / used-by optimizers.
(c) Tim Menzies, 2021 MIT License, https://opensource.org/licenses/MIT.
"""
from random import seed as seed
from random import random as _r
import re, math, types, random, inspect

class o:
  def __init__(i, **d): i.__dict__.update(**d)
  def __repr__(i): return "{"+ ', '.join(
      [f":{k} {v}" for k, v in sorted(i.__dict__.items()) 
       if  not o.funp(v) and k[0] != "_"])+"}"
  def __add__(i, here):
    for k,v in here.items():
      if o.funp(v) and k[0] != "_":
        i.__dict__[k] = o.method(i,v)
    return i
  def method(i,f): return lambda *l, **kw: f(i, *l, **kw)
  def funp(x)    : return isinstance(x,types.FunctionType)

THE = o(seed=1, skip="?", cohen=.2, id=0, betters=32,
        less="<",more=">",path="data",file="auto93.csv",
        Xchop=.5, best=.75, sep=",", ignore=r'([\n\t\r ]|#.*)')
seed(THE.seed)

def Counts(): 
  return o(f={}, h={}, n=0)

def Row(lst): 
  def ys(i,t): return [i.cells[c.pos] for c in t.cols.y]
  def _better(i,j,t):
    s1,s2,n = 0,0,len(t.cols.y)
    for col in t.cols.y:
      pos,w = col.pos, col.w
      a,b   = i.cells[pos], j.cells[pos]
      a,b   = col.norm(a), col.norm(b)
      s1   -= math.e**(w*(a-b)/n)
      s2   -= math.e**(w*(b-a)/n)
    return s1/n < s2/n
  def betters(i,t):
    i.n = i.n or sum(_better(i,random.choice(t.rows), t) 
                     for _ in range(THE.betters))/THE.betters
    return i.n
  return o(cells=lst, n=None, _tag=False) + locals()

def Tbl(): 
  def adds(i,src):
    for lst in src:
      if i.cols.all: 
        i.rows += [Row( [c.add(x) for c,x in zip(i.cols.all, lst)] )]
      else: 
        i.cols.all = [i.cols.add(pos,txt) for pos,txt in enumerate(lst)]
    i.rows = sorted(i.rows, key=lambda r: r.betters(i))
    for n,row in enumerate(i.rows):
      row.tag = n > len(i.rows)*THE.best 
    return i
  return o(cols=Cols(), rows=[]) + locals()

def Cols(): 
  def add(i,pos,txt):
    if   THE.skip in txt                                       : f = Skip
    elif THE.less in txt or THE.more in txt or txt[0].isupper(): f = Num
    else                                                       : f = Sym
    now = f(pos=pos, txt=txt, w=-1 if THE.less in txt else 1)
    if   THE.skip in txt                                       : also = []
    elif THE.less in txt or THE.more in txt                    : also = i.y
    else                                                       : also = i.x
    also  += [now]
    return now
  return o(all=[], y=[], x=[]) + locals()

def Span(x, y):
  def has(i,x,y): return i.down <= x <i.up
  return o(down=x, up=y, _also=Sym()) + locals()

def Skip(pos=0, txt="", w=1):
  def add(i,x): 
    if x != THE.skip: i.n += 1; return x
  return o(pos=pos, txt=txt, w=w, n=0)  + locals()

def Sym(pos=0, txt="", w=1):
  def ent(i): return -sum(v/i.n*math.log(v/i.n,2) for v in i.seen.values())
  def div(i, _): return [Span(x,x) for x in i.seen.keys()]
  def combined(i, j):
    if i.mode == j.mode:
      k = Sym(pos=i.pos, txt=i.txt, w=i.w)
      for x,n in {**i.seen, **j.seen}.items(): k.add(x,n)
      return k
  def add(i,x,n=1): 
    if x != THE.skip: 
      i.n += n
      now = i.seen[x] = i.seen.get(x, 0) + n
      if now > i.most: i.most, i.mode = now, x
    return x
  return o(pos=pos, txt=txt, w=w, n=0, seen={}, most=0, mode=None) + locals()

def Num(pos=0, txt="", w=1):
  def mid(i)   : n,a = _all(i); return a[int(n/2)]
  def var(i)   : n,a = _all(i); return (a[int(.9*n)] - a[int(n/10)]) / 2.56
  def norm(i,x): _,a = _all(i); return (x - a[0]) / (a[-1] - a[0])
  def _all(i)   : 
    i._all = i._all if i.ok else sorted(i._all)
    i.ok = True
    return len(i._all), i._all
  def add(i, x): 
    if x != THE.skip:
      i._all += [x]; i.n+= 1; i.ok = False
    return x
  def div(i,t): 
    xy = sorted([(r.cells[pos], r.tag) for r in t.rows 
                if r.cells[pos] != THE.skip])
    width = len(xy)**THE.Xchop
    while width < 4 and width < len(xy) / 2: width *= 1.2
    now = Span(xy[0][0], xy[0][0])
    tmp = [now]
    for j,(x,y) in enumerate(xy):
      if j < len(xy) - width:
        if now._also.n >= width:
          if x != xy[j+1][0] and now.up - now.down > i.var()*THE.cohen:
            now  = Span(now.up, x)
            tmp += [now]
      now.up = x
      now._also.add(y)
    out = _merge(tmp)
    out[ 0].down = -math.inf
    out[-1].up   =  math.inf
    return out
  def _merge(b4):
    j, tmp, n = 0, [], len(b4)
    while j < n:
      a = b4[j]
      if j < n - 1:
        b  = b4[j+1]
        if now := a._also.combined(b._also):
          a = Span(a.down, b.up)
          a._also = now
          j += 1
      tmp += [a]
      j   += 1
    return _merge(tmp) if len(tmp) < len(b4) else b4
  return o(pos=pos, txt=txt, w=w, _all=[], ok=True, n=0) + locals()

def csv(file):
  def atom(x):
    try: return int(x)
    except Exception:
      try: return float(x)
      except Exception: return x
  with open(file) as fp:
    for a in fp: 
      yield [atom(x) for x in re.sub(THE.ignore, '', a).split(THE.sep)]

# t=Tbl().adds(csv(THE.path + "/" + THE.file))
# #print(t.cols.y)
# #print(t.cols.y)
# for row in t.rows[:5]: print(row.ys(t),row.tag,row.n)
# print("")
# for row in t.rows[-5:]: print(row.ys(t),row.tag,row.n)
# for col in t.cols.x: 
#   print(f"\n {col.txt}", col.pos)
#   print(col.div(t))
#
import  inspect 
import argparse

def cli(fun):
  parser = argparse.ArgumentParser(
    prog            = fun.__name__, 
    description     = fun.__doc__.split("\n\n")[0],
    formatter_class = argparse.RawDescriptionHelpFormatter)
  for k,v in inspect.signature(fun).parameters.items():
    val, txt, choices, isa = v.default, v.annotation, None, isinstance
    if isa(val,(list,tuple)): 
       choices, val = val, val[0]
       notes = f"{txt}; default= {val}, range= {choices}" 
    else:
       notes = f"{txt}; default= {val}" 
    meta,ako= (("I",int)   if isa(val, int)   else (
               ("F",float) if isa(val, float) else ("S",str)))
    add = lambda **d: parser.add_argument("-"+k,help=notes,**d)
    if   val is False: add(action='store_true')
    elif val is True:  add(action='store_false')
    elif choices:      add(default=val, metavar=meta, type=ako, choices=choices)
    else:              add(default=val, metavar=meta, type=ako)
  return fun(**vars(parser.parse_args()))

def ageAndShoeSize(
       dob  :  "date of birth" = 1960,
       elated : "make happy" = False,
       where: "birth place"= ["nsw","vic"],
       shoes :  "shoesize" = 10):
  """Good times for all.
  (c) Tim here now 2021"""
  print( f"{where} dob + shoes = {dob+shoes} elated= {elated}")

if __name__=="__main__":
  cli(ageAndShoeSize)

