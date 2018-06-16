---
layout: post
comments: true
title: "Verilog cookbook"
tags: [WIP, verilog, cookbook]
---

**Verilog** is a specification language.

## Data type groups

### Variables

The bit-vector is the only data type available in this language

| Value | |
|-------|-|
| 0     | logic zero |
| 1     | logic one |
| X     | unknown logic value |
| Z     | high impedance |

It's possible to use a literal in the following form

```
<bits size>'<base><literal>
```

where

 - ``bits size`` indicate how many bits the literal is in decimal base
 - ``base`` can be ``b`` for binary, ``d`` for decimal, ``h`` for hexadecimal
 - ``literal`` is the value in the chosen base; ``_`` are ignored and it's possible to use ``x`` and ``z``

### Operations

It's possible to concatenate vectors

```
assign hilo = {hi, lo}
```

or to duplicate values

```
assign a = {16{1'b1}}
```

| Arithmetic | ``+`` ``-`` ``*`` ``/`` ``%`` ``**`` |
| Logical    | ``!`` ``&&`` ``||`` |
| Relational | ``>`` ``<`` ``>=`` ``<=`` |
| Bitwise    | ``~`` ``&`` ``|`` ``^`` ``^~`` |
| Reduction  | ``&`` ``~&`` ``|`` ``~|`` ``^`` ``^~`` |
| Shift      | ``>>`` ``<<`` ``>>>`` ``<<<`` |
| Concatenation | ``{`` ``}`` |
| Conditional | ``?:`` |

Probably is a good idea to avoid operators like ``/`` and choose wisely
the signal width.

### Constants

It's possible to define constants with the keyword ``DEFINE``.

### Nets

They represent connection between the different part of a circuit; the

Use the following to save you from default signal created when a typo slide in
your code

```
`default_nettype none
```

## Modules

The definition is in the form

```
module module_name#(parameter PARAMETER_1, )(
    input [3:0] signal_1,
    ...
    output [5:0] signal_N
);
    /* some code *

endmodule
```

that can be instanciated as follow

```
module_name instance_name(
    .signal_1(some_wire),
    ...
    .signal_N(some_other_wire)
);
```
