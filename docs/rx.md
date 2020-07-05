# Rx
A treatment "`Rx`" is a label (`i.rx`) and a set of 
values (`i.all`).  

Similar treatments can be `group`ed together 
into sets of values with the same `rank`

- [Notes](#notes) : 
  - [Overview](#overview) : 
  - [Example](#example) : 
- [Rx](#rx-class) : class
- [Statistical Tests](#statistical-tests) : 
  - [CliffsDelta](#cliffsdelta) : 
  - [Bootstrap](#bootstrap) : 
- [Output](#output) : 
  - [Group](#group) : 

---------------


---------------


## Notes
### Overview

- Things in the same rank are statistically 
  indistinguishable, as judged by all three of:
  1. A very fast non-parametric `D` test 
      - Sort the numns, ignore divisions less that
        30% of "spread" (90th-10th percentile range); 
  2. A (slightly more thorough) non-parametric effect 
    size test (the Cliff's Delta);
      -  Twp lists are different if, usually, 
         things from one list do not fall into the middle 
         of the other.
  3. (very thorough) non-parametric 
    significance test (the Bootstrap);
       - See if hundreds of sample-with-replacements
         sets from two lists and  different properties to 
         the overall list.

Of the above, the third is far slower than the rest. Often, if it is
omitted, the results are often the same as just using 1+2.  So when
each treatment has 1000s of values, it would be reasonable to skip
it. Without bootstrapping,  256 treatments with 1000 values
can be sorted in less than 2 seconds. But with that skipping
that same process takes half an hour.

### Example

This code is asking for an analysis of five treatments 
`x1,x2,x3,x4,x5`:

        n = 256
        group(    
           dict(
             x1 = [ 0.34, 0.49 ,0.51, 0.6]*n,
             x2 = [0.6  ,0.7 , 0.8 , 0.89]*n,
             x3 = [0.13 ,0.23, 0.33 , 0.35]*n,
             x4 = [0.6  ,0.7,  0.8 , 0.9]*n,
             x5 = [0.1  ,0.2,  0.3 , 0.4]*n),
           width= 30,
           chops= [.25,  .5, .75],
           marks= ["-", "-", " "])

In the above, note that the `chops` and `marks` tells the code
to report the `25,50,75th` percentile.

This code reports that these treatments divide into three  groups (`0,1,2`):

        0  x5 (   ----*---    |              ), 0.200,  0.300,  0.400
        0  x3 (    ----*      |              ), 0.230,  0.330,  0.350
        1  x1 (              -*--            ), 0.490,  0.510,  0.600
        2  x2 (               |      ----*-- ), 0.700,  0.800,  0.890
        2  x4 (               |      ----*-- ), 0.700,  0.800,  0.900

---------------

## Rx: class

```py
from lib import Thing, xtile
import random

class Rx(Thing):
  dull  = [0.147,0.33, 0.474][0]
  b     = 500
  conf  = 0.05
  cohen = 0.3
  def __init__(i, rx="", all=[], lo=0,hi=1,  
                         width = 50,
                         chops = [0.1 ,0.3,0.5,0.7,0.9],
                         marks = [" " ,"-"," ","-"," "]):
    i.rx   = rx
    i.all  = sorted([x for x in all if x != "?"])
    i.lo   = min(i.all[0],lo)
    i.hi   = max(i.all[-1],hi)
    i.n    = len(i.all)
    i.med  = i.all[int(i.n/2)]
    i.parts= [i]
    i.rank = 0
    i.width, i.chops, i.marks = width, chops, marks
```
Treatments are sorted on their `med` value.
```py
  def __lt__(i,j): 
    return i.med < j.med
```
Two treatments are statistically indistinguishable
if a non-parametric effect size test (`cliffsDelta`)
and a non-parametric significance test (`bootstrap`)
say that there are no differences between them.

```py
  def __eq__(i,j):
    return cliffsDelta(i.all,j.all) and bootstrap(i.all,j.all)
```
Treatments can be combined or printed.
```py
  def __add__(i,j):
    k =  Rx(all = i.all + j.all,
            lo=min(i.lo, j.lo), 
            hi=max(i.hi, j.hi))
    k.parts = i.parts + j.parts
    return k
  def __repr__(i):
    return '%10s %s' % (i.rx, xtile(i.all, i.lo, i.hi,
                                    width = i.width,
                                    chops = i.chops,
                                    marks = i.marks))
```
## Statistical Tests
### CliffsDelta
For every item in `lst1`, find its position in `lst2` Two lists are
different if, usually, things from one list do not fall into the
middle of the other.

This code employees a few tricks to make all this run fast (e..g
pre-sort the lists, work over `runs` of same values).

```py
def cliffsDelta(lst1, lst2, dull=Rx.dull):
  def runs(lst):
    for j,two in enumerate(lst):
      if j == 0: one,i = two,0
      if one!=two:
        yield j - i,one
        i = j
      one=two
    yield j - i + 1,two
  #---------------------
  m, n = len(lst1), len(lst2)
  lst2 = sorted(lst2)
  j = more = less = 0
  for repeats,x in runs(sorted(lst1)):
    while j <= (n - 1) and lst2[j] <  x: j += 1
    more += j*repeats
    while j <= (n - 1) and lst2[j] == x: j += 1
    less += (n - j)*repeats
  d= (more - less) / (m*n)
  return abs(d)  <= dull
```
### Bootstrap
Two  lists y0,z0 are the same if the same patterns can be seen in
all of them, as well as in 100s to 1000s  sub-samples from each.
From p220 to 223 of the Efron text  'introduction to the bootstrap'.

This function checks for  different properties between (a) the two
lists and (b) hundreds of sample-with-replacements sets.

```py
def bootstrap(y0,z0,conf=Rx.conf,b=Rx.b):
  
  class Sum(): # Quick & dirty class to summarize sets of values.
    def __init__(i,some=[]):
      i.sum = i.n = i.mu = 0 ; i.all=[]
      for one in some: i.put(one)
    def put(i,x):
      i.all.append(x);
      i.sum +=x; i.n += 1; i.mu = float(i.sum)/i.n
    def __add__(i1,i2): return Sum(i1.all + i2.all)
```
Define the property that we will check for.
```py
  def testStatistic(y,z):
     tmp1 = tmp2 = 0
     for y1 in y.all: tmp1 += (y1 - y.mu)**2
     for z1 in z.all: tmp2 += (z1 - z.mu)**2
     s1    = float(tmp1)/(y.n - 1)
     s2    = float(tmp2)/(z.n - 1)
     delta = z.mu - y.mu
     if s1+s2:
       delta =  delta/((s1/y.n + s2/z.n)**0.5)
     return delta
```
Sampling with replacement
```py
  def one(lst): return lst[ int(any(len(lst))) ]
  def any(n)  : return random.uniform(0,n)
```
Now the actual work begins.
```py
  y,z  = Sum(y0), Sum(z0)
  x    = y + z
  baseline = testStatistic(y,z)
  yhat = [y1 - y.mu + x.mu for y1 in y.all]
  zhat = [z1 - z.mu + x.mu for z1 in z.all]
  bigger = 0
  for i in range(b):
    if testStatistic(Sum([one(yhat) for _ in yhat]),
                     Sum([one(zhat) for _ in zhat])) > baseline:
      bigger += 1
  return bigger / b >= conf
```
## Output
### Group
Given a dictionary of values, sort the values by their median
then iteratively merge together adjacent similar items.

```py
def group(d, cohen = 0.3, 
             width = 50,
             chops = [0.1 ,0.3,0.5,0.7,0.9],
             marks = [" " ,"-"," ","-"," "]):
  def merge(lst, lvl=0):
```
Do one pass, see what we can combine.
```py
    j,tmp = 0,[]
    while j < len(lst):
      x = lst[j]
      if j < len(lst) - 1: 
        y = lst[j+1]
        if abs(x.med - y.med) <= tiny or x == y:
          tmp += [x+y] # merge x and y
          j   += 2
          continue
      tmp += [x]
      j   += 1
```
Now either recurse to find more merges, or print out the results.
```py
    if len(tmp) < len(lst):
      return merge(tmp, lvl+1) 
    else:
      for n,group in enumerate(lst):
        for rx in group.parts:
          rx.rank = n
          print(n, rx) 
      return lst
```
Now the work begins:
```py
  p    = lambda n: a[ int( n*len(a) )]
  a    = sorted([x for k in d for x in d[k]])
  tiny = (p(.9) - p(.2))/2.56 * Rx.cohen
  return merge(sorted([Rx(rx    = k,    all = d[k], 
                          lo    = a[0], hi  = a[-1],
                          width = width,
                          chops = chops,
                          marks = marks) 
               for k in d]))
```






