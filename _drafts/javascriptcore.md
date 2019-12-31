---
layout: post
comments: true
title: "Notes on JavascriptCore"
tags: [browser, gdb]
---

In this post I want to add some pratical notes (and maybe a new tool)
to the [paper from saelo](http://phrack.com/papers/attacking_javascript_engines.html)
about exploiting modern browsers; in particular Webkit.

As in his paper, I'll deep dive into the source code of that version of webkit.

## Fundamental datatypes

Here a brief recap of something already covered by saelo just to have
a self-consistent writeup, however I advice you to read the paper linked
above.

First of all we need to understand the datatypes; take in mind that the
codebase is in ``C++`` and the namespace for the majority of the classes
that we'll encounter will be ``JSC``, so I won't include it explicitely.

The first and most fundamental is the ``JSValue``, that is like the encoding
used internally by JavascriptCore for its datatype; what does it mean? it means
that since this is a Javascript engine, it must have a way to represent primitive
values; the main trick to distinguish between data type is the tagging of the
actual value in memory.

```
0x00 00000000 empty (internal value)
0x02 00000010 null
0x04 00000100 delete (internal value)
0x06 00000110 false
0x07 00000111 true
0x0a 00001010 undefined
         ' '-------------> TagBitTypeOther
          `--------------> TagBitUndefined
```


An interesting part is how the webkit's code deals with some of characteristics
of ``C++`` language: missing ``super`` and ``instanceof``:

 - ``super`` is implemented using the ``ClassInfo``
 - ``instanceof`` is implemented also via ``JSType`` enum


```c++
enum JSType : uint8_t {
    UnspecifiedType,
    UndefinedType,
    BooleanType,
    NumberType,
    NullType,

    // The CellType value must come before any JSType that is a JSCell.
    CellType,
    ...
    // The ObjectType value must come before any JSType that is a subclass of JSObject.
    ObjectType,
    FinalObjectType,
    JSCalleeType,
    JSFunctionType,
    ...
}
```


### JSCell

``JSCell`` it's the base class for all the runtime data types that need to be
garbage collected somehow.

 ``JSObject`` instead is 

but there are a couple of others classes important for the following

### Butterfly

``Butterfly`` it's a class without properties, mainly used to "cast" and wrap
the data structure holding the actual data

The way in which the pointer to a butterfly is used cause the code that returns
the pointer to it to make some magic with pointer arithmetics:

```c++
inline Butterfly* Butterfly::createUninitialized(VM& vm, JSCell* intendedOwner, size_t preCapacity, size_t propertyCapacity, bool hasIndexingHeader, size_t indexingPayloadSizeInBytes)
{
    void* temp;
    size_t size = totalSize(preCapacity, propertyCapacity, hasIndexingHeader, indexingPayloadSizeInBytes);
    RELEASE_ASSERT(vm.heap.tryAllocateStorage(intendedOwner, size, &temp));
    Butterfly* result = fromBase(temp, preCapacity, propertyCapacity);
    return result;
}

static Butterfly* JSC::Butterfly::fromBase(void* base, size_t preCapacity, size_t propertyCapacity)
{
    return reinterpret_cast<Butterfly*>(static_cast<EncodedJSValue*>(base) + preCapacity + propertyCapacity + 1);
}
```

indeed the size is calculated in the following way

```c++
static size_t totalSize(size_t preCapacity, size_t propertyCapacity, bool hasIndexingHeader, size_t indexingPayloadSizeInBytes)
{
    ASSERT(indexingPayloadSizeInBytes ? hasIndexingHeader : true);
    ASSERT(sizeof(EncodedJSValue) == sizeof(IndexingHeader));
    return (preCapacity + propertyCapacity) * sizeof(EncodedJSValue) + (hasIndexingHeader ? sizeof(IndexingHeader) : 0) + indexingPayloadSizeInBytes;
}

inline size_t JSObject::butterflyTotalSize()
{
    Structure* structure = this->structure();
    Butterfly* butterfly = this->butterfly();
    size_t preCapacity;
    size_t indexingPayloadSizeInBytes;
    bool hasIndexingHeader = this->hasIndexingHeader();

    if (UNLIKELY(hasIndexingHeader)) {
        preCapacity = butterfly->indexingHeader()->preCapacity(structure);
        indexingPayloadSizeInBytes = butterfly->indexingHeader()->indexingPayloadSizeInBytes(structure);
    } else {
        preCapacity = 0;
        indexingPayloadSizeInBytes = 0;
    }

    return Butterfly::totalSize(preCapacity, structure->outOfLineCapacity(), hasIndexingHeader, indexingPayloadSizeInBytes);
}
```

### Structure

``Structure``: it identifies the class the object belongs to (via the ``m_classInfo`` attribute)
and describe the "layout" of the javascript object, i.e. the actual values
that identify the ``Butterfly``; moreover, it contains the actual table (data type ``PropertyTable``
in the field ``m_propertyTableUnsafe``) with the list of attributes that are defined and at what offsets.




``m_keyCount`` gives the number of properties available and if ``m_propertyTableUnsafe`` is ``NULL``
obvioulsy we don't have properties.

**Note:** it seems that properties of the ``JSCell`` are assigned from the corresponding values in the
``Structure`` associated during creation(?), I think for performance reason.

To understand where the properties are located looks in the code

```
WriteBarrierBase<Unknown>* JSObject::locationForOffset(PropertyOffset offset)
{
    if (isInlineOffset(offset))
        return &inlineStorage()[offsetInInlineStorage(offset)];
    return &outOfLineStorage()[offsetInOutOfLineStorage(offset)];
}
```

we have the **inline** storage

```
inline bool JSC::isInlineOffset(PropertyOffset offset)
{
    checkOffset(offset);
    return offset < firstOutOfLineOffset;
}

PropertyStorage JSObject::inlineStorageUnsafe()
{
    return bitwise_cast<PropertyStorage>(this + 1);
}

PropertyStorage JSObject::inlineStorage()
{
    ASSERT(hasInlineStorage());
    return inlineStorageUnsafe();
}
```

and the **outline** storage

```
static const PropertyOffset firstOutOfLineOffset = 100;

ConstPropertyStorage outOfLineStorage() const
{
    return m_butterfly.get(this)->propertyStorage();
}

inline size_t JSC::offsetInOutOfLineStorage(PropertyOffset offset)
{
    validateOffset(offset);
    ASSERT(isOutOfLineOffset(offset));
    return -static_cast<ptrdiff_t>(offset - firstOutOfLineOffset) - 1;
}
```

With all of this in mind, it's good to know that exists a method to calculate
the **base** of the butterfly instance

```c++
inline void* Butterfly::base(Structure* structure)
{
    return base(indexingHeader()->preCapacity(structure), structure->outOfLineCapacity());
}
```

but it's possible also to access elements like an array (``IndexingType.h``)

```c++
JSValue JSObject::tryGetIndexQuickly(unsigned i) const
{
    Butterfly* butterfly = m_butterfly.get(this);
    switch (indexingType()) {
    case ALL_BLANK_INDEXING_TYPES:
    case ALL_UNDECIDED_INDEXING_TYPES:
        break;
    case ALL_INT32_INDEXING_TYPES:
        if (i < butterfly->publicLength()) {
            JSValue result = butterfly->contiguous()[i].get();
            ASSERT(result.isInt32() || !result);
            return result;
        }
        break;
    case ALL_CONTIGUOUS_INDEXING_TYPES:
        if (i < butterfly->publicLength())
            return butterfly->contiguous()[i].get();
        break;
    case ALL_DOUBLE_INDEXING_TYPES: {
        if (i >= butterfly->publicLength())
            break;
        double result = butterfly->contiguousDouble()[i];
        if (result != result)
            break;
        return JSValue(JSValue::EncodeAsDouble, result);
    }
    case ALL_ARRAY_STORAGE_INDEXING_TYPES:
        if (i < butterfly->arrayStorage()->vectorLength())
            return butterfly->arrayStorage()->m_vector[i].get();
        break;
    default:
        RELEASE_ASSERT_NOT_REACHED();
        break;
    }
    return JSValue();
}
```

```c++
#define ARRAY_WITH_ARRAY_STORAGE_INDEXING_TYPES \
    ArrayWithArrayStorage:                      \
    case ArrayWithSlowPutArrayStorage
    
#define ALL_ARRAY_STORAGE_INDEXING_TYPES                \
    NonArrayWithArrayStorage:                           \
    case NonArrayWithSlowPutArrayStorage:               \
    case ARRAY_WITH_ARRAY_STORAGE_INDEXING_TYPES

```

```c++
class IndexingHeader {

private:
    union {
        struct {
            uint32_t publicLength; // The meaning of this field depends on the array type, but for all JSArrays we rely on this being the publicly visible length (array.length).
            uint32_t vectorLength; // The length of the indexed property storage. The actual size of the storage depends on this, and the type.
        } lengths;
        
        struct {
            ArrayBuffer* buffer;
        } typedArray;
    } u;
};
```

**Note:** the ``Butterfly`` uses for taking outoflinestorage and indexing properties a wrapper
datatype named ``IndexingHeader`` *moved by 1*

## Arrays

From ``ArrayStorage.h``

```c++
namespace JSC {

// This struct holds the actual data values of an array. A JSArray object points to its contained ArrayStorage
// struct by pointing to m_vector. To access the contained ArrayStorage struct, use the getStorage() and 
// setStorage() methods. It is important to note that there may be space before the ArrayStorage that 
// is used to quick unshift / shift operation. The actual allocated pointer is available by using:
//     getStorage() - m_indexBias * sizeof(JSValue)
// All slots in ArrayStorage (slots from 0 to vectorLength) are expected to be initialized to a JSValue or,
// for hole slots, JSValue().
struct ArrayStorage {
    ...
};

} // namespace JSC

```

From ``IndexingType.h``

```c++
/*
    Structure of the IndexingType
    =============================
    Conceptually, the IndexingType looks like this:

    struct IndexingType {
        uint8_t isArray:1;                    // bit 0
        uint8_t shape:4;                      // bit 1 - 3
        uint8_t mayHaveIndexedAccessors:1;    // bit 4
    };

    The shape values (e.g. Int32Shape, ContiguousShape, etc) are an enumeration of
    various shapes (though not necessarily sequential in terms of their values).
    Hence, shape values are not bitwise exclusive with respect to each other.
*/
```

The way the array-like objects are classified are a little tricky

 - **contiguous:** the entries are ``JSValue`` instances
 - **int32**, **double**, etc: the entries are stored as not encoded values

```c++
static inline bool JSC::hasAnyArrayStorage(IndexingType indexingType)
{
    return static_cast<uint8_t>(indexingType & IndexingShapeMask) >= ArrayStorageShape;
}

static inline bool JSC::hasIndexedProperties(IndexingType indexingType)
{
    return (indexingType & IndexingShapeMask) != NoIndexingShape;
}

inline bool Structure::hasIndexingHeader(const JSCell* cell) const
{
    if (hasIndexedProperties(indexingType()))
        return true;

    if (!isTypedView(m_classInfo->typedArrayStorageType))
        return false;

    return jsCast<const JSArrayBufferView*>(cell)->mode() == WastefulTypedArray;
}
```

## GDB manual session

Let's create a simple object in Javascript, using the javascript console ``jsc``

```
>>> a = {a: 1, b:2, c:3}
[object Object]
>>> describe(a)
Cell: 0x55e56899be40 (0x55e5689e8d00:[Object, {a:0, b:1, c:2}, NonArray, Proto:0x55e5689c3ff0, Leaf]), ID: 348
```

and after attaching to it with ``gdb`` we can inspect the memory

```
gef➤  x/60xg 0x55e56899be40
0x55e56899be40: 0x010016000000015c      0x0000000000000000
0x55e56899be50: 0xffff000000000001      0xffff000000000002
0x55e56899be60: 0xffff000000000003      0x0000000000000000
0x55e56899be70: 0x0000000000000000      0x0000000000000000
gef➤  print *('JSC::JSCell'*) 0x55e56899be40
$9 = {
  static StructureFlags = 0x0, 
  static needsDestruction = 0x0, 
  static TypedArrayStorageType = JSC::NotTypedArray, 
  m_structureID = 0x15c, 
  m_indexingType = 0x0, 
  m_type = JSC::FinalObjectType, 
  m_flags = 0x0, 
  m_cellState = JSC::CellState::NewWhite
}
```

```
gef➤  print *('JSC::Structure'*)(('JSC::MarkedBlock'*)( 0x55e56899be40 & ~(16*1024 - 1)))->m_weakSet.m_vm->heap->m_structureIDTable.m_table.get()[348]
$22 = {
  <JSC::JSCell> = {
    static StructureFlags = 0x0,
    static needsDestruction = 0x0,
    static TypedArrayStorageType = JSC::NotTypedArray,
    m_structureID = 0x1,
    m_indexingType = 0x0,
    m_type = JSC::CellType,
    m_flags = 0x20,
    m_cellState = JSC::CellState::NewWhite
  },
  ...
  m_blob = {
    u = {
      fields = {
        structureID = 0x15c,
        indexingType = 0x0,
        type = JSC::FinalObjectType,
        inlineTypeFlags = 0x0,
        defaultCellState = JSC::CellState::NewWhite
      },
      words = {
        word1 = 0x15c,
        word2 = 0x1001600
      },
      doubleWord = 0x10016000000015c
    }
  },
  m_outOfLineTypeFlags = 0x0,
  m_globalObject = {
    <JSC::WriteBarrierBase<JSC::JSGlobalObject>> = {
      m_cell = 0x55e568983700
    }, <No data fields>},
  m_prototype = {
    <JSC::WriteBarrierBase<JSC::Unknown>> = {
      m_value = 0x55e5689c3ff0
    }, <No data fields>},
  m_cachedPrototypeChain = {
    <JSC::WriteBarrierBase<JSC::StructureChain>> = {
      m_cell = 0x0
    }, <No data fields>},
  m_previousOrRareData = {
    <JSC::WriteBarrierBase<JSC::JSCell>> = {
      m_cell = 0x55e5689e3e00
    }, <No data fields>},
  m_nameInPrevious = {
    m_ptr = 0x55e56894a850
  },
  m_classInfo = 0x7fae22daea00 <JSC::JSFinalObject::s_info>,
  m_transitionTable = {
    static UsingSingleSlotFlag = 0x1,
    m_data = 0x1
  },
  m_propertyTableUnsafe = {
    <JSC::WriteBarrierBase<JSC::PropertyTable>> = {
      m_cell = 0x55e5689925c0
    }, <No data fields>},
  m_inferredTypeTable = {
    <JSC::WriteBarrierBase<JSC::InferredTypeTable>> = {
      m_cell = 0x0
    }, <No data fields>},
  m_transitionWatchpointSet = {
    static IsThinFlag = 0x1,
    static StateMask = 0x6,
    static StateShift = 0x1,
    m_data = 0x3
  },
  m_offset = 0x2,
  m_inlineCapacity = 0x6,
  m_lock = {
    <WTF::LockBase> = {
      static isHeldBit = 0x1,
      static hasParkedBit = 0x2,
      m_byte = {
        value = {
          <std::__atomic_base<unsigned char>> = {
            _M_i = 0x0
          }, <No data fields>}
      }
    }, <No data fields>},
  m_bitField = 0x4a00000
}
```

Take a look at the butterflies: from the ``jsc``'s prompt insert an object

```js
>>> a = {a:1, b:2, c:3, d:4, e:5, f:6, g:7}
[object Object]
>>> b = {h:8, i:9, l:10, m:11, n:12, o:13, p:14}
[object Object]
>>> describe(a)
Cell: 0x563afd783d80 (0x563afd82f100:[Object, {a:0, b:1, c:2, d:3, e:4, f:5, g:100}, NonArray, Proto:0x563afd7abff0, Leaf]), ID: 378
>>> describe(b)
Cell: 0x563afd783d40 (0x563afd82ed00:[Object, {h:0, i:1, l:2, m:3, n:4, o:5, p:100}, NonArray, Proto:0x563afd7abff0, Leaf]), ID: 385
>>> a[0] = 0xabad1d3a
2880249146
>>> a.kebab = 34
34
>>> a.jeova = 17
17
>>> a.miao = 99
99
```

```
gef➤  set $obj = (('JSC::JSObject'*) 0x563afd783d80)
gef➤  x/10xg $obj
0x563afd783d80: 0x0100160600000188      0x0000563afd81a748
0x563afd783d90: 0xffff000000000001      0xffff000000000002
0x563afd783da0: 0xffff000000000003      0xffff000000000004
0x563afd783db0: 0xffff000000000005      0xffff000000000006
0x563afd783dc0: 0x0100160000000173      0x0000000000000000
gef➤  x/20xg $obj->butterfly()->base($obj->structure())
0x563afd81a720: 0xffff000000000063      0xffff000000000011
0x563afd81a730: 0xffff000000000022      0xffff000000000007
0x563afd81a740: 0x0000000400000001      0x41e575a3a7400000
0x563afd81a750: 0x7ff8000000000000      0x7ff8000000000000
0x563afd81a760: 0x7ff8000000000000      0x0000000000000000
0x563afd81a770: 0x0000000000000000      0x0000000000000000
0x563afd81a780: 0x0000000000000000      0x0000000000000000
0x563afd81a790: 0x0000000000000000      0x0000000000000000
0x563afd81a7a0: 0x0000000000000000      0x0000000000000000
0x563afd81a7b0: 0x0000000000000000      0x0000000000000000
gef➤  x/20xg $obj->butterfly()
0x563afd81a748: 0x41e575a3a7400000      0x7ff8000000000000
0x563afd81a758: 0x7ff8000000000000      0x7ff8000000000000
0x563afd81a768: 0x0000000000000000      0x0000000000000000
0x563afd81a778: 0x0000000000000000      0x0000000000000000
0x563afd81a788: 0x0000000000000000      0x0000000000000000
0x563afd81a798: 0x0000000000000000      0x0000000000000000
0x563afd81a7a8: 0x0000000000000000      0x0000000000000000
0x563afd81a7b8: 0x0000000000000000      0x0000000000000000
0x563afd81a7c8: 0x0000000000000000      0x0000000000000000
0x563afd81a7d8: 0x0000000000000000      0x0000000000000000
```

## GEF

Now that we have done some homeworks, we can try to power up the game creating a tool
(or improving one in our case) in order to make all simpler for future adventures: we can
try to extend ``gef`` ([github repo here](https://github.com/hugsy/gef)) a ``gdb`` extension(?) for security activities.

Remember if you have problem when you are writing code for gef that is possible to enable
the debugging so to have a clean traceback when errors happen

```
gef➤  gef config gef.debug true
gef➤  gef config gef.debug
─────────────────────────────── GEF configuration setting: gef.debug ───────────────────────────────
gef.debug (bool) = True

Description:
        Enable debug mode for gef
```

and to avoid to restart ``gdb`` when you change the script code you can do ``source /path/to/script.py``
to reload it; take in mind that all the classes and functions are available in the python environment.

## Case study: CVE-2016-4622

Now that we have a deeper understanding of the ``JSC`` internals should be easier understand
what saelo was talking about.

To automatize the analysis you can use the following ``gdb``'s [script]({{ site.baseurl }}/public/code/javascriptcore/bp.gdb)

```
>>> a = [];for (var i = 0; i < 100; i++)a.push(i + 13.37);var b = a.slice(0, {valueOf: function() { a.length = 0;c=[obj];return 4;}});b
13.37,14.37,8.4879831644e-314,4.6843036111784e-310
```


## Links

 - [printers.py](http://www.cs.ru.nl/~gdal/dotfiles/.gdb/printers/python/libstdcxx/v6/printers.py)
 - [Thinking outside the JIT Compiler: Understanding and bypassing StructureID Randomization with generic and old-school methods](https://i.blackhat.com/eu-19/Thursday/eu-19-Wang-Thinking-Outside-The-JIT-Compiler-Understanding-And-Bypassing-StructureID-Randomization-With-Generic-And-Old-School-Methods.pdf)
 - [Hack The Real: An exploitation chain to break Safari browser](https://gts3.org/2019/Real-World-CTF-2019-Safari.html)
