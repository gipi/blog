<!--
.. title: blog migration to Nikola
.. slug: blog-migration-to-nikola
.. date: 2021-07-01 07:27:25 UTC
.. tags: meta
.. category: 
.. link: 
.. description: 
.. type: text
-->

After running for a couple of years using ``jekill`` as a static site generator
I decided to switch to [``nikola``](https://getnikola.com/) for a couple of reasons: first of all because
is implemented in ``python``, a language that I know more than ``ruby`` and this
allows me to improve the platform and customize it more to suite my needs.

<!-- TEASER_END -->


For example now is possible to describe circuit directly in the post and have a
beautiful ``svg`` image to be generated for me, for example using
[schemdraw](https://schemdraw.readthedocs.io/), the following code

```python
{{% raw %}}{{% pyplots %}}
import matplotlib
matplotlib.use('Agg')

import schemdraw
from schemdraw import elements as elm

d = schemdraw.Drawing()
d += elm.Ground()
d += elm.SourceV().label('500mV')

d += elm.Resistor().right().label('20k$\Omega$')
d += (Vin := elm.Dot())
d += elm.Line().length(.5)
d += (O1 := elm.Opamp().anchor('in1'))
d += elm.Line().left().length(0.75).at(O1.in2)
d += elm.Ground()
d += elm.Line().up().at(Vin.start).length(2)
d += elm.Resistor().right().label('100k$\Omega$')
d += elm.Line().down().toy(O1.out)
d += elm.Dot()
d += elm.Line().right().at(O1.out).length(5)
d += (O2 := elm.Opamp().anchor('in2'))
d += (Vin2 := elm.Line().left().at(O2.in1).length(0.5))
d += elm.Dot()
d += elm.Resistor().left().label('30k$\Omega$')
d += elm.Ground()
d += elm.Line().up().at(Vin2.end).length(1.5)
d += elm.Resistor().right().label('90k$\Omega$')
d += elm.Line().down().toy(O2.out)
d += elm.Dot()
d += elm.Line().right().at(O2.out).length(1).label('$v_{out}$', loc='rgt')
d.draw()
{{% /pyplots %}}{{% /raw %}}
```

generates this image:
{{% pyplots %}}
import matplotlib
matplotlib.use('Agg')

import schemdraw
from schemdraw import elements as elm

d = schemdraw.Drawing()
d += elm.Ground()
d += elm.SourceV().label('500mV')

d += elm.Resistor().right().label('20k$\Omega$')
d += (Vin := elm.Dot())
d += elm.Line().length(.5)
d += (O1 := elm.Opamp().anchor('in1'))
d += elm.Line().left().length(0.75).at(O1.in2)
d += elm.Ground()
d += elm.Line().up().at(Vin.start).length(2)
d += elm.Resistor().right().label('100k$\Omega$')
d += elm.Line().down().toy(O1.out)
d += elm.Dot()
d += elm.Line().right().at(O1.out).length(5)
d += (O2 := elm.Opamp().anchor('in2'))
d += (Vin2 := elm.Line().left().at(O2.in1).length(0.5))
d += elm.Dot()
d += elm.Resistor().left().label('30k$\Omega$')
d += elm.Ground()
d += elm.Line().up().at(Vin2.end).length(1.5)
d += elm.Resistor().right().label('90k$\Omega$')
d += elm.Line().down().toy(O2.out)
d += elm.Dot()
d += elm.Line().right().at(O2.out).length(1).label('$v_{out}$', loc='rgt')
d.draw()
{{% /pyplots %}}

or the following code

```python
{{% raw %}}{{% wavedrom %}}
{ "signal": [
 { "name": "CK",   "wave": "P.......",                                              "period": 2  },
 { "name": "CMD",  "wave": "x.3x=x4x=x=x=x=x", "data": "RAS NOP CAS NOP NOP NOP NOP", "phase": 0.5 },
 { "name": "ADDR", "wave": "x.=x..=x........", "data": "ROW COL",                     "phase": 0.5 },
 { "name": "DQS",  "wave": "z.......0.1010z." },
 { "name": "DQ",   "wave": "z.........5555z.", "data": "D0 D1 D2 D3" }
]}
{{% /wavedrom %}}{{% /raw %}}
```

generates instead this

{{% wavedrom %}}
{ "signal": [
 { "name": "CK",   "wave": "P.......",                                              "period": 2  },
 { "name": "CMD",  "wave": "x.3x=x4x=x=x=x=x", "data": "RAS NOP CAS NOP NOP NOP NOP", "phase": 0.5 },
 { "name": "ADDR", "wave": "x.=x..=x........", "data": "ROW COL",                     "phase": 0.5 },
 { "name": "DQS",  "wave": "z.......0.1010z." },
 { "name": "DQ",   "wave": "z.........5555z.", "data": "D0 D1 D2 D3" }
]}
{{% /wavedrom %}}
