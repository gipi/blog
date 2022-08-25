<!--
.. title: Reversing C++, Qt based applications using Ghidra
.. slug: reversing-c++-qt-applications-using-ghidra
.. date: 2022-05-27 12:27:43 UTC
.. tags: reversing, Qt, ghidra, C++
.. category: 
.. link: 
.. description: 
.. type: text
-->

This post is going to be too ambitious probably: I want to introduce you to
reversing ``C++`` code, applying this knowledge in particular to ``Qt``
applications and since we are at it, explaining some ``ghidra`` scripting to
automate the process.

<!-- TEASER_END -->

Here a little table of contents to jump where needed

 - [Introduction to reversing ``C++`` code](#introduction)
    - [Classes](#classes)
    - [Methods](#methods)
    - [Templates](#templates)
 - [Qt](#qt)
    - [common data types](#qt-datatype)
    - [``QObject``s](#qobjects)
    - [``QML``&Resources](#qml-resources)
 - [Ghidra](#ghidra)
    - [warm up](#warm-up)
    - [Address spaces](#address-spaces)
    - [Symbol&Namespace](#symbol-namespace)
    - [Selections](#selections)
    - [Memory block](#memory-block)
    - [Data](#data)
    - [References](#references)
    - [Functions](#functions)
    - [Analysis](#analysis)
    - [Analysing opcodes](#opcodes)
    - [Scripting](#scripting)


<a name="introduction"></div>
## Introduction to reversing C++ code

Reversing ``C++`` code is a little more involved with respect to reversing
simple ``C`` code, but at end of the day it's not impossible. ``C++`` is sure a
more "complicated language" if compared with ``C``, in particular for the
possibility to instantiate classes, that are ``struct``s on steroid but also for
the more advanced "features" like polymorphism, inheritance and templating.

But, also after all that, remember that however a language is defined, objects will be layed out in memory
(hopefully) in continous chunks and methods will be always called as usual,
maybe with an extended usage of function pointers.

If you want to know in detail how the ``ABI`` for the ``C++`` language works,
[here the specification](https://itanium-cxx-abi.github.io/cxx-abi/abi.html);
this covers memory layout for ``C++`` data objects (predefined, user-defined and
compiler-generated, e.g. **virtual tables**) but also function calling
interfaces, exception handling interfaces, global naming, and various object
code conventions. Probably I'll expand a little more later when needed.

**Note:** if, like me, sometimes you try to compile some code to double check
that makes sense of your expectations, make sure to strip the binary and use
some optimization (like ``-O2``) so to have the compiler to "simplify" a bunch
of nested constructors calls. In case you need something quick to play with take
in mind that [compiler explorer](https://godbolt.org/) exists.

In the following sections I'm going to explore the low-level "implementation" of
the building blocks of ``C++``, it's assumed that you know how reverse generic
``C`` code, what follows builds on that.


<a name="classes"></div>
### Classes layout

The first thing that differentiate ``C++`` from ``C`` is the possibility to
instantiate classes: a class is an encapsulation of data types and functions that act on them;
this last point has some complication given from the ``virtual`` keyword: it allows for **runtime polymorphism**, i.e.,
it tells the compiler to resolve the function call at runtime (read more [here](https://en.cppreference.com/w/cpp/language/virtual)).

In order to allow this to happen, the compiler generates a so called **virtual
table**, containing an array of function pointers, and place its address at the
start of the memory region allocated for the instance of the class.

The data associated with the classed is placed just after that; obviously if the
class has not virtual functions defined, no virtual table is necessary and only
the data will be present. Another complication regarding classes is the
possibility of having an inheritance tree: a class can derive from one or more
classes and the compiler must generate a "blueprint" accordingly.

What does it mean? if you have a class defined as follow

```c++

class A {
    memberType1 memberA1;
    ...
    memberTypeN memberAN;

    virtual methodA1();
    ...
    virtual methodAM();
};

class B {
    memberType1 memberB1;
    ...
    memberTypeN memberBP;

    virtual methodB1();
    ...
    virtual methodBQ();
};

class C : A, B {
    memberType1 memberC1;
    ...
    memberTypeR memberCR;

    virtual methodC1();
    ...
    virtual methodCS();
}
```

the layout in memory will be something like the following (where the offset is
loosely intended as the index in the "right" array describing the object in
memory)


| offset | description |
|--------|-------------|
| 0      | vtable C:A  |
| 1      | memberA1    |
| ...    | ...         |
| AN     | memberAN    |
| AN + 1 | vtable B:A  |
| AN + 2 | memberB1    |
| ...    | ...         |
| AN + 1 + BP | memberBP |
| AN + BP + 2 | memberC1 |
| ...    | ...         |
| AN + BP + 1 + CR | memberCR |

**Obviously, depending on the size of a given datatype, could be present
padding**.

Note that the virtual methods of ``C`` will be appended to the virtual table of
the first parent's


``ghidra`` has the possibility to define classes in the "Symbol tree" panel;
when you define a class you are defining two things, a ``GhidraClass`` instance
that is a ``Namespace`` and a ``struct`` associated with it (it would be
hopefully clearer in the section regarding ``ghidra``).

There is no support for virtual tables out of the box, you have to manually add
the first entry of the structure with an array of pointers.

<a name="methods"></div>
### Methods

The virtual functions contained in the virtual tables are a particular case of
methods associated with a class instance, a large number of methods are not
virtual and must be deducted from their behaviour.

In particular methods are functions "attached" to an instance of a class (if not static) and
behave like normal functions in the ``C`` language if not for the **implicit**
parameter named ``this`` that is possible to access when you are inside the
method; when you look at the code when reversing you'll have this parameter 
passed (usually) as a first argument with type equal to a pointer to the struct associated
with the class. In
``ghidra`` is possible to indicate that the function belongs to a class
moving the function to the
``Namespace`` of the class (implicitely created with the class?) via the
"rename" functionality, using a scheme like ``<class name>::<function name>``
or moving the function by hand into the namespace in the "Symbol tree" panel.

**Note:** after you assigned a namespace to a function, when you rename the
function itself, you won't see the namespace prepended to function's name
anymore but it's on the namespace's drop down menu just below (of course); if
you want to change the namespace the function belongs you have to select from
the drop down menu "Global" and prepend the namespace and the two colons to the
function's name. I think also that ``ghidra`` accepts nested namespaces but the
class handling of that is tricky (I must investigate further).

Once you have done that you can "Edit function signature" and indicate
``__thiscall`` for the calling convention: automatically it will assign the
first argument in the right way (probably there is a bug: it doesn't change only
the first argument but prepend it to the list causing a wrong number of
arguments assigned to the function)·

This is not valid if the return value is not "simple": from the [specification](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#this-parameters)

    If the return type is a class type that is non-trivial for the purposes of
    calls, the caller passes an address as an implicit parameter. The callee
    then constructs the return value into this address. bla bla bla

this means that you have to add another argument before ``this`` but it's pretty
simple to catch once you know about it and you are pretty sure the class the method belongs because
it's not returning nothing and you know it must return something. Also, in this
case change the return value to void, in same cases not doing that can generate
confusion with ``ghidra``.

**Note:** it seems that ``__thiscall`` is generated automatically in
``Ghidra/Features/Decompiler/src/decompile/cpp/architecture.cc`` from the
``<default_proto>`` entry in the ``<architecture>.cspec``.

Regarding the handling of ``C++`` methods, the signature of external functions
(i.e. functions that are imported from external libraries) is deducted from the
"mangled" name of the imported symbol: to allow for polymorphism, that is
functions with the same name but different signature, the "real" name of a
function encodes the argument that the function receives (but not the return
value). I didn't investigate but it seems that ``ghidra`` doesn't know if a
method belongs to a class or if it's static unless are constructors (i.e. named ``ClassName::ClassName``),
so be aware to
this fact when you see analyze code involving imported functions.

**Note:** usually ``ghidra`` automatically "translate" to the correct name for a
function, but you have to indicate the right compiler spec at import time; how
do you know which is the correct one? you have to guess my friend.

**Note:** this is a general advise regarding reversing functions: read about the
calling convention and parameters passing convention of the architecture you are
working with, because when you see something non-sensical probably ``ghidra``
hasn't guessed something right or maybe is a bug (for example in my experience,
when a ``long long`` is passed as argument in ``ARM``, it uses two registers,
starting from an even register index, so if it's the second argument and the
first is an ``int``, you have ``r0`` for the first argument and ``r2``, ``r3``
for the second, leaving ``r1`` untouched).

Since I'm writing this post after an activity of reversing involving ``ARM``
binaries, the examples below involve that architecture, to see how the calling
convention is defined for it see [Procedure Call Standard for the
ARM® Architecture](https://caxapa.ru/thumbs/656023/IHI0042F_aapcs.pdf)
and [The ARM-THUMB Procedure Call Standard](https://www.cs.cornell.edu/courses/cs414/2001FA/armcallconvention.pdf).

<a name="templates"></div>
### Templates

A feature of ``C++`` are the so called **templates**: pratically is possible to
define an "abstract" implementation of an algorithm/data having as a free
"variable" a data type; this means that ``template``s generate code "inline", not in external libraries,
the only thing that you will see will be some calls to weird named functions like
[``_List_node_base::_M_hook()``](https://code.woboq.org/boost/include/c++/5.3.0/bits/stl_list.h.html#std::__detail::_List_node_base)
that are the internal implementation of the complex data structure the code is
the implementation of.
The idea is that usually a data structure has an internal "private"
implementation (Pimpl?) and so you won't see method of this class but the
internal one: in the section about ``Qt`` you'll see an example of that with the
``QList``/``QListData`` class.

So you should probably tries
to get a look at widely used data structure in the ``STL`` and see their
implementation to have the feeling of what you should expect,
for example [``shared_ptr``](https://code.woboq.org/gcc/libstdc++-v3/include/bits/shared_ptr.h.html)
is a good candidate because
is a data type you'll probably encounter in reversing.

Take in mind that templates can also take a variable number of arguments
(they are called [variadic template](https://en.wikipedia.org/wiki/Variadic_template))
and are used **a lot** in ``Qt``. This is more of a hint if you are going to
read a lot of ``C++`` source code, that if you are not used to it can be
overwhelming at first.

<a name="qt"></div>
## Qt source code

Before passing to ``Qt`` let me give you some tips to navigate code you want to
understand: first of all you need a tool to navigate the code, and for studying
this library I used [``sourcetrail``](https://github.com/CoatiSoftware/Sourcetrail)
but bad enough it's not maintained anymore :(.

In order to use it you have to obtain a "database" containing the list of files
and you can bake one compiling the library from source via some extra tools;
first of all you have
to configure it (the process is a little tricky): after you have cloned it

```
$ ./init-repository -f --module-subset=default,-qtwebengine
$ git submodule foreach --recursive "git clean -dfx" && git clean -dfx
$ mkdir qt5-build/ && cd qt5-build
$ ../configure -developer-build -opensource -nomake examples -nomake tests --recheck-all -confirm-license \
    -fontconfig -sql-sqlite -no-sql-odbc -system-freetype -qt-zlib -qt-libpng \
    -qt-libjpeg -no-compile-examples  -no-opengl -no-feature-concurrent \
    -no-feature-xml -no-feature-testlib \
    -skip qt3d -skip qtactiveqt -skip qtandroidextras -skip qtcanvas3d \
    -skip qtcharts -skip qtconnectivity -skip qtdatavis3d -skip qtdoc \
    -skip qtgamepad -skip qtgraphicaleffects -skip qtimageformats \
    -skip qtlocation -skip qtmacextras -skip qtmultimedia -skip qtnetworkauth \
    -skip qtpurchasing -skip qtquickcontrols -skip qtquickcontrols2 \
    -skip qtremoteobjects -skip qtscript -skip qtscxml -skip qtsensors \
    -skip qtserialbus -skip qtserialport -skip qtsvg -skip qtspeech \
    -skip qttools -skip qttranslations -skip qtvirtualkeyboard -skip qtwayland \
    -skip qtwebchannel -skip qtwebsockets -skip qtwebview -skip qtwinextras \
    -skip qtx11extras -skip qtxmlpatterns -skip qtwebengine
```

Then you can build and generate the database that can be opened with
``sourcetrail`` using [bear](https://github.com/rizsotto/Bear)

```
$ bear -- make -j2
```

Remember that any time you start ``bear`` it overwrites the
``compile_commands.json`` generated file, you can use the ``--append`` flag to
avoid that.

**Note:** This process is not perfect, for example, I was not able to build
completely the library, failed at some point but the generated database was
usable. Another point where the process can fail is loading into
``sourcetrail``, if the database is too big it's possible to have a crash :)
this is the reason I removed **a lot** of stuff during the configuration steps.

For example a reason of failure is the compiler: for me, only using ``g++-8`` I
was able to start the compilation

```
diff --git a/mkspecs/common/g++-base.conf b/mkspecs/common/g++-base.conf
index c337696304..2df381a399 100644
--- a/mkspecs/common/g++-base.conf
+++ b/mkspecs/common/g++-base.conf
@@ -15,7 +15,7 @@ QMAKE_CC                = $${CROSS_COMPILE}gcc
 QMAKE_LINK_C            = $$QMAKE_CC
 QMAKE_LINK_C_SHLIB      = $$QMAKE_CC
 
-QMAKE_CXX               = $${CROSS_COMPILE}g++
+QMAKE_CXX               = $${CROSS_COMPILE}g++-8
 
 QMAKE_LINK              = $$QMAKE_CXX
 QMAKE_LINK_SHLIB        = $$QMAKE_CXX
```

An alternative is the online code viewer [Woboq](https://code.woboq.org/qt5/),
you don't have to do anything and it's ready to navigate but you don't have the
visual cues about attributes and methods that you have with ``sourcetrail``.

### Other ways

 - [Easily getting type information of a common ELF library into Ghidra](https://reversing.technology/2021/06/16/ghidra_DWARF_gdt.html)
 - [gdt](https://github.com/0x6d696368/ghidra-data/blob/master/typeinfo/README.md)

<a name="qt-datatype"/>
## A little overview of Qt datatypes

Before starting reversing it's necessary to have a minimal understanding of the
data types used in this library. Let's start with strings: ``Qt`` uses a data
type name ``QString``; as I said above, generally "complicated" data structures
"hide" the data and let you interact via methods, in the case of the ``QString``
you have an internal pointer ``typedef``ed to be a subclass of ``QArrayData``, a
generic container(?) that handles also the reference counting of the object
itself: here some snippet of the source code

```C++

struct Q_CORE_EXPORT QArrayData
{
    QtPrivate::RefCount ref;
    int size;
    uint alloc : 31;
    uint capacityReserved : 1;
    qptrdiff offset; // in bytes from beginning of header
    ...
    static const QArrayData shared_null[2];
    static QArrayData *sharedNull() noexcept { return const_cast<QArrayData*>(shared_null); }
};

template <class T>
struct QTypedArrayData : QArrayData { ... };

typedef QTypedArrayData<ushort> QStringData;

class Q_CORE_EXPORT QString
{
    public:
        typedef QStringData Data;
        ...
        Data *d;
        ...
};
```

From this convoluted construction we can deduce that the ``QString`` class is
simply a wrapper around a pointer of type ``Data`` (that by a couple of
definition later) is linked to ``QArrayData``. This last data type contains all
the information to dereference the data contained into it:

 - ``ref`` is the reference counter, when 0 the object can be removed from
   memory, if -1 means the object is static
 - ``size`` is the data size
 - ``alloc`` how many bytes are actually allocated
 - ``capacityReserved`` I don't know
 - ``offset`` is where the actual data is located with respect to the start of
   the struct

**Note:** ``QArrayData`` is an example of packing and alignment of ``struct``s.

```
(gdb) ptype /o QArrayData
/* offset    |  size */  type = struct QArrayData {
/*    0      |     4 */    class QtPrivate::RefCount {
                             public:
/*    0      |     4 */        QBasicAtomicInt atomic;
                               /* total size (bytes):    4 */
                           } ref;
/*    4      |     4 */    int size;
/*    8: 0   |     4 */    uint alloc : 31;
/*   11: 7   |     4 */    uint capacityReserved : 1;
/* XXX  4-byte hole  */
/*   16      |     8 */    qptrdiff offset;
                           static const QArrayData shared_null[2];

                           /* total size (bytes):   24 */
                         }
```

Read more here: "[The Lost Art of Structure Packing](http://www.catb.org/esr/structure-packing/)".

The interesting thing is that when you initialize an empty ``QString``, the ``d``
attribute is built from ``shared_null``

```C++
inline QString::QString() noexcept : d(Data::sharedNull()) {}
```

so when you see something like this in the decompiler panel

```
somevariable = QArrayData::shared_null;
```

it's propably initializing an empty string.

An interesting application of the internal of ``QString`` regards string literals implemented via
``QStringLiteral``: observe this macro

```C++
#define Q_REFCOUNT_INITIALIZE_STATIC { Q_BASIC_ATOMIC_INITIALIZER(-1) }

#define QT_UNICODE_LITERAL(str) u"" str
#define QStringLiteral(str) \
    ([]() noexcept -> QString { \
        enum { Size = sizeof(QT_UNICODE_LITERAL(str))/2 - 1 }; \
        static const QStaticStringData<Size> qstring_literal = { \
            Q_STATIC_STRING_DATA_HEADER_INITIALIZER(Size), \
            QT_UNICODE_LITERAL(str) }; \
        QStringDataPtr holder = { qstring_literal.data_ptr() }; \
        return QString(holder); \
    }()) \
    /**/

#define Q_STATIC_STRING_DATA_HEADER_INITIALIZER_WITH_OFFSET(size, offset) \
    { Q_REFCOUNT_INITIALIZE_STATIC, size, 0, 0, offset } \
    /**/

#define Q_STATIC_STRING_DATA_HEADER_INITIALIZER(size) \
    Q_STATIC_STRING_DATA_HEADER_INITIALIZER_WITH_OFFSET(size, sizeof(QStringData)) \
    /**/
```

For a more involved explanation see "[QStringLiteral explained](https://woboq.com/blog/qstringliteral.html)".

Why am I telling you this? simply because messages inside the application (that
are using ``QString``) are
not going to have references to the ``char``s of the string itself but to the
``QArrayData`` that points to it; after a while you will be able to see
sequences of ``0xffffffff`` (``-1``) as indication of
static objects allocations. Take in mind that could be some data not
"string"-related since the real data type should be ``QTypedArrayData`` that is
a template but that fact is "lost in translation" in the binary.


An example of code that you can encounter is the following

```
void FUN_00172460(int **param_1,int param_2)

{
  bool bVar1;
  int *piVar2;
  
  piVar2 = *(int **)(param_2 + 0x24);
  *param_1 = piVar2;
  if (1 < *piVar2 + 1U) {
    DataMemoryBarrier(0xb);
    do {
      bVar1 = (bool)hasExclusiveAccess(piVar2);
    } while (!bVar1);
    *piVar2 = *piVar2 + 1;
    DataMemoryBarrier(0xb);
    return;
  }
  return;
}

```

if you set the ``param_1`` to be a ``QString`` you see that this code simply
    copy the pointer of the data from the second parameter to the first and
    increase the reference counter; the ``if`` is necessary in order to check if
    the object is static (``ref`` = -1) or "dead" (``ref`` = 0).

Indeed the "real code" is like the following (note here that although this is a
class method, the ``this`` parameter is not the first one since the return value
is a "not simple" object); note how the ``QArrayData`` pointer is copied to the
``_d`` field of the returning ``QString``

```c++
void UserInfo::getSomeString(QString *result,UserInfo *this)

{
  bool bVar1;
  QArrayData *pQVar2;
  
  pQVar2 = (this->plan_string)._d;
  result->_d = pQVar2;
  if (1 < pQVar2->ref + 1U) {
    DataMemoryBarrier(0xb);
    do {
      bVar1 = (bool)hasExclusiveAccess(pQVar2);
    } while (!bVar1);
    pQVar2->ref = pQVar2->ref + 1;
    DataMemoryBarrier(0xb);
    return;
  }
  return;
}

```

The instruction ``DataMemoryBarrier(0xb)`` is an actual machine instruction
(``dmb``) used in ``ARM`` to enforce data consistency among cpus.

It's very important to recognize this pattern of reference counting because you'll encounter it
everywhere.

A very similar class is

```C++
class Q_CORE_EXPORT QByteArray
{
    private:
        typedef QTypedArrayData<char> Data;
 ...
}
```

If you need to reverse ``Qt`` application, probably you are going to encounter
``QSettings``, it's a [global](https://doc.qt.io/qt-6/qsettings.html#details) object that you can query
for values (usually used for configuration); it's internal structure it's not
    important (should be empty) since it actions are performed via ``QVariant``
    that you can think as a "catch-all" object ([here the documentation](https://doc.qt.io/qt-6/qvariant.html#details))

From the documentation

    QSettings stores settings. Each setting consists of a QString that specifies
    the setting's name (the key) and a QVariant that stores the data associated
    with the key

Just below the definition of ``QVariant``, as you can see it's pratically a
``union`` on steroids (remember that a ``union`` is the
longest-contained-element wide, so ``data`` is  8bytes since it contains a
``long long``, but be aware that this could be different from other architectures):

```C++
class Q_CORE_EXPORT QVariant
{
 ...
    struct Private
    {
    ...
        union Data
        {
            char c;
            uchar uc;
            short s;
            signed char sc;
            ushort us;
            int i;
            uint u;
            long l;
            ulong ul;
            bool b;
            double d;
            float f;
            qreal real;
            qlonglong ll;
            qulonglong ull;
            QObject *o;
            void *ptr;
            PrivateShared *shared;
        } data;
        uint type : 30;
        uint is_shared : 1;
        uint is_null : 1;
    };
    ...
    public:
        Private d;
    ...
};
```

Another data structure you are going to encounter is the ``QList``
([documentation](https://doc.qt.io/qt-5/qlist.html#details)), a data
container that behaves like a list.

By its definition you can see that is a template

```C++

template <typename T>
class QList
{
   ...
    struct Node { void *v;
        Q_INLINE_TEMPLATE T &t()
        { return *reinterpret_cast<T*>(QTypeInfo<T>::isLarge || QTypeInfo<T>::isStatic
                                       ? v : this); }
    };
   ...
    union { QListData p; QListData::Data *d; };
   ...
};

struct Q_CORE_EXPORT QListData {
   ...
    struct Data {
        QtPrivate::RefCount ref;
        int alloc, begin, end;
        void *array[1];
    };
   ...
    Data *d;
   ...
};
```

so at the end of the day, ``QList`` is simply a wrapper around a ``QListData::Data`` pointer
and that is the data structure that you'll see passing around.

Moreover being ``QList`` a template, you won't see calls to
``QList<someobject>::begin()`` but inlined code like

```C++
template <typename T>
class QList<T> {
    ...
    inline iterator begin() { detach(); return reinterpret_cast<Node*>(p.begin()); }
    ...
    inline void detach() { if (d->ref.isShared()) detach_helper(); }
    ...
};

class QListData {
    ...
    inline void **begin() const noexcept { return d->array + d->begin; }
    ...
};

template <typename T>
Q_OUTOFLINE_TEMPLATE void QList<T>::detach_helper()
{
    detach_helper(d->alloc);
}

template <typename T>
Q_OUTOFLINE_TEMPLATE void QList<T>::detach_helper(int alloc)
{
    Node *n = reinterpret_cast<Node *>(p.begin());
    QListData::Data *x = p.detach(alloc);
    QT_TRY {
        node_copy(reinterpret_cast<Node *>(p.begin()), reinterpret_cast<Node *>(p.end()), n);
    } QT_CATCH(...) {
        p.dispose();
        d = x;
        QT_RETHROW;
    }

    if (!x->ref.deref())
        dealloc(x);
}
```

this last function is still a template but it's not inlined, so you should see a function calling
``QListData::detach()`` inside; it's a difficult process the first time but if
the "realized" ``QList`` is used elsewhere you will be able to easily resolve
the ``begin()`` call promptly. 

This is how it looks like

```C++
void QList<QNetworkAddressEntry>_detach_helper(QListData *list,int alloc)

{
  bool bVar1;
  Data *d;
  Data *pDVar2;
  int iVar3;
  void **ppvVar4;
  void **this;
  
  ppvVar4 = list->_d->array + list->_d->begin;
  d = (Data *)list;
  QListData::detach(&list->_d,alloc);
  pDVar2 = list->_d;
  iVar3 = pDVar2->end;
  for (this = pDVar2->array + pDVar2->begin; pDVar2->array + iVar3 != this; this = this + 1) {
    QNetworkAddressEntry::QNetworkAddressEntry
              ((QNetworkAddressEntry *)this,(QNetworkAddressEntry *)ppvVar4);
    ppvVar4 = ppvVar4 + 1;
  }
  if (d->ref != 0) {
    if (d->ref == -1) {
      return;
    }
    DataMemoryBarrier(0xb);
    do {
      iVar3 = d->ref + -1;
      bVar1 = (bool)hasExclusiveAccess(d);
    } while (!bVar1);
    d->ref = iVar3;
    DataMemoryBarrier(0xb);
    if (iVar3 != 0) {
      return;
    }
  }
  Qlist<QNetworkAddressEntry>_dealloc(d);
  return;
}

```

As you can see the memory reference management is always there.

<a name="qobjects"/>
## QObjects

Now in this section will reach the highest achievement in reversing ``Qt`` based
binaries, understanding the ``QObject`` trickery, i.e. the base class used
throughout all the ``Qt`` library.

All what I'm going to describe you could seem unnecessary but I assure you that
is going to help you analyze a binary using this library in unexpected ways,
take in mind that all the reflexivity tha library has builtin (via ``QObject``'s internals)
is going  to tell
you exactly all the methods, signals and properties of a given subclass of
``QObject``.

First of all, a class that inherits from ``QObject`` is a normal ``C++`` class,
but it has also attached another ``struct`` that describes it, ``QMetaObject``

```C++
struct Q_CORE_EXPORT QMetaObject
{
 ...
    struct { // private data
        SuperData superdata;
        const QByteArrayData *stringdata;
        const uint *data;
        typedef void (*StaticMetacallFunction)(QObject *, QMetaObject::Call, int, void **);
        StaticMetacallFunction static_metacall;
        const SuperData *relatedMetaObjects;
        void *extradata; //reserved for future use
    } d;
 ...
};
```

the way this ``struct`` is "attached" to the class itself is a little more involved:
in particular you need ``moc``, the "MetaObject compiler": you see, some
constructs on ``Qt`` code is not legal ``C++`` code, in order to allow all this
machinery to work you need to have you ``Qt`` code pre-compiled with ``moc`` so
to obtain new ``C++`` files that then can be compiled by your loved
``C++`` compiler.

Every class that wants this malackery needs to use the macro ``Q_OBJECT``

```C++
/* qmake ignore Q_OBJECT */
#define Q_OBJECT \
public: \
    QT_WARNING_PUSH \
    Q_OBJECT_NO_OVERRIDE_WARNING \
    static const QMetaObject staticMetaObject; \
    virtual const QMetaObject *metaObject() const; \
    virtual void *qt_metacast(const char *); \
    virtual int qt_metacall(QMetaObject::Call, int, void **); \
    QT_TR_FUNCTIONS \
private: \
    Q_OBJECT_NO_ATTRIBUTES_WARNING \
    Q_DECL_HIDDEN_STATIC_METACALL static void qt_static_metacall(QObject *, QMetaObject::Call, int, void **); \
    QT_WARNING_POP \
    struct QPrivateSignal {}; \
    QT_ANNOTATE_CLASS(qt_qobject, "")
```

that for what matters to us, sets the first three functions in the virtual table of the
class to be

| Function                                                | Description                                                                    |
|---------------------------------------------------------|--------------------------------------------------------------------------------|
|    ``QMetaObject *metaObject()``                        | it simply returns the corresponding ``QMetaObject`` associated with this class |
|    ``void *qt_metacast(const char *)``                  | it's the function used for casting |
|    ``int qt_metacall(QMetaObject::Call, int, void **)`` | it's the function that "resolves" attributes, methods and signals |

These methods are important because allow us to obtain important information
about the class, in particular

 - ``metaObject()`` it's the method that returns the ``QMetaObject`` instance,
   so it has a direct reference to the ``QMetaObject`` vtable
 - ``qt_metacast()`` can tell us the name of the class and possible inheritance
 - ``qt_metacall()`` is probably a big ``switch()`` construct with each ``case``
   resolving a signal or method of a given instance

**Note:** the two functions that I usually see following after these three are two destructors.

**Note:** the data type just after the virtual table is a pointer to
``QObjectData``, it's like private data but I won't elaborate further on it.

Once you have a reference to the ``QMetaObject`` struct you can extract all the
information of a class, indeed (taking inspiration from these posts
[1](https://woboq.com/blog/how-qt-signals-slots-work.html)
and [2](https://woboq.com/blog/how-qt-signals-slots-work-part2-qt5.html))
we have for example for the class used as example in the documentation, the
following generated metadata: the data just after ``content`` is the header the
indicate where and how many instances of each property (methods, properties,
enums, etc...) there are

```c++
static const uint qt_meta_data_Counter[] = {

 // content:
       7,       // revision
       0,       // classname
       0,    0, // classinfo
       2,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       1,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    1,   24,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       4,    1,   27,    2, 0x0a /* Public */,

 // signals: parameters
    QMetaType::Void, QMetaType::Int,    3,

 // slots: parameters
    QMetaType::Void, QMetaType::Int,    5,

       0        // eod
};
```

From this info is possible to obtain, for example, all the methods, their names and arguments.

<!--

https://doc.qt.io/qt-6/properties.html
https://doc.qt.io/qt-6/qtqml-typesystem-objecttypes.html
-->

Being a library used to build event-driven GUIs, it uses signals extensively,
so it's important to understand how the code connect together different classes
when a signal is raised. In ``Qt`` a signal is a message that an object can send,
most of the time to inform of a status change.

A related concept is the **slot**:a slot is a function that is used to accept and respond to a signal.
The high level APIs used to connect signals and slots are the following

```
    static QMetaObject::Connection connect(const QObject *sender, const char *signal,
                        const QObject *receiver, const char *member, Qt::ConnectionType = Qt::AutoConnection);

    static QMetaObject::Connection connect(const QObject *sender, const QMetaMethod &signal,
                        const QObject *receiver, const QMetaMethod &method,
                        Qt::ConnectionType type = Qt::AutoConnection);

    inline QMetaObject::Connection connect(const QObject *sender, const char *signal,
                        const char *member, Qt::ConnectionType type = Qt::AutoConnection) const;
```

you can navigate yourself the [QtObject::connect()](https://code.woboq.org/qt5/include/qt/QtCore/qobject.h.html#_ZN7QObject7connectEPKN9QtPrivate15FunctionPointerIT_E6ObjectES2_PKNS1_IT0_E6ObjectES7_N2Qt14ConnectionTypeE)
implementation
or the [QtPrivate::FunctionPointer](https://code.woboq.org/qt5/include/qt/QtCore/qobjectdefs_impl.h.html#QtPrivate::FunctionPointer) template madness;
meanwhile I copy it here for quick reference the relevant part

```c++
// qtbase/src/corelib/kernel/qobjectdefs_impl.h
...
    /*
      The FunctionPointer<Func> struct is a type trait for function pointer.
        - ArgumentCount  is the number of argument, or -1 if it is unknown
        - the Object typedef is the Object of a pointer to member function
        - the Arguments typedef is the list of argument (in a QtPrivate::List)
        - the Function typedef is an alias to the template parameter Func
        - the call<Args, R>(f,o,args) method is used to call that slot
            Args is the list of argument of the signal
            R is the return type of the signal
            f is the function pointer
            o is the receiver object
            and args is the array of pointer to arguments, as used in qt_metacall

       The Functor<Func,N> struct is the helper to call a functor of N argument.
       its call function is the same as the FunctionPointer::call function.
     */
...
    template<class Obj, typename Ret, typename... Args> struct FunctionPointer<Ret (Obj::*) (Args...)>
    {
        typedef Obj Object;
        typedef List<Args...>  Arguments;
        typedef Ret ReturnType;
        typedef Ret (Obj::*Function) (Args...);
        enum {ArgumentCount = sizeof...(Args), IsPointerToMemberFunction = true};
        template <typename SignalArgs, typename R>
        static void call(Function f, Obj *o, void **arg) {
            FunctorCall<typename Indexes<ArgumentCount>::Value, SignalArgs, R, Function>::call(f, o, arg);
        }
    };
...

template <typename Func1, typename Func2>
static inline QMetaObject::Connection connect(
    const typename QtPrivate::FunctionPointer<Func1>::Object *sender, Func1 signal,
    const typename QtPrivate::FunctionPointer<Func2>::Object *receiver, Func2 slot,
    Qt::ConnectionType type = Qt::AutoConnection)
{
  typedef QtPrivate::FunctionPointer<Func1> SignalType;
  typedef QtPrivate::FunctionPointer<Func2> SlotType;

  //compilation error if the arguments does not match.
  Q_STATIC_ASSERT_X(int(SignalType::ArgumentCount) >= int(SlotType::ArgumentCount),
                    "The slot requires more arguments than the signal provides.");
  Q_STATIC_ASSERT_X((QtPrivate::CheckCompatibleArguments<typename SignalType::Arguments,
                                                         typename SlotType::Arguments>::value),
                    "Signal and slot arguments are not compatible.");
  Q_STATIC_ASSERT_X((QtPrivate::AreArgumentsCompatible<typename SlotType::ReturnType,
                                                       typename SignalType::ReturnType>::value),
                    "Return type of the slot is not compatible with the return type of the signal.");

  const int *types = nullptr;
  if (type == Qt::QueuedConnection || type == Qt::BlockingQueuedConnection)
      types = QtPrivate::ConnectionTypes<typename SignalType::Arguments>::types();

  QtPrivate::QSlotObjectBase *slotObj = new QtPrivate::QSlotObject<Func2,
        typename QtPrivate::List_Left<typename SignalType::Arguments, SlotType::ArgumentCount>::Value,
        typename SignalType::ReturnType>(slot);


  return connectImpl(sender, reinterpret_cast<void **>(&signal),
                     receiver, reinterpret_cast<void **>(&slot), slotObj,
                     type, types, &SignalType::Object::staticMetaObject);
```

What's importat to remember from all of that is the call to ``connectImpl()``:
at the end from the decompiler you will see something like the following

```
  slot = BatteryManager::activity;
  signal = &slot;
  sender = this->batteryManager; <--- this emits the signal
  slotPtr = BatteryManager::standbyEnabledChanged; <--- this is the signal we want to connect
  receiver = this->field56_0xd8;
  _slot = (QSlotObjectBase *)operator.new(0x10);
  _slot->m_ref = 1;
  _slot->m_impl = FUN_000789e8; <--- this is glue code
  // some other values on _slot
  QObject::connectImpl(
    &conn,
    sender,(void **)signal,
    receiver,&slotPtr,_slot,
    0,NULL, (QMetaObject *)&BatteryManager::MetaObject_vtable);
```

to double check that all makes sense take in mind that the ``MetaObject_vtable``
must be of the same type of the ``sender`` and remember that since this call
returns something "complex" the first argument is the returning object (i.e.
``QMetaObject::Connection``), also, this a ``static`` method so no ``this`` is
required.

Once that you have obtained the methods of the object is possible to reach their
actual implementation via the ``qt_metacall()`` function: it's the third entry in the
``metavtable`` that resolves everything at runtime, its signature is

```
<object>::qt_static_metacall(QObject *object, QMetaObject::Call call, int index, void** args);
```

where ``object`` is the object obviously, ``call`` is what is requested via the
``Enum`` 

```c++
    enum Call {
        InvokeMetaMethod,
        ReadProperty,
        WriteProperty,
        ResetProperty,
        QueryPropertyDesignable,
        QueryPropertyScriptable,
        QueryPropertyStored,
        QueryPropertyEditable,
        QueryPropertyUser,
        CreateInstance,
        IndexOfMethod,
        RegisterPropertyMetaType,
        RegisterMethodArgumentMetaType
    };
```

Meanwhile the meaning of ``index`` and ``args`` is depending on the context: if ``call`` is ``InvokeMetaMethod``
then ``index`` is the identifier of the signal/method/slot you are trying to
invoke and **from our perspective can allow to resolve the functions easily**.

**Note** however that it's not the only point where the signal are activated, to
find them you have to look for all the ``QMetaObject::activate()`` filtering
with the right ``metavtable`` and ``index``. This probably can be automated :)

<a name="qml-resources"/>
## QML&Resources

the Qt QML module provides a framework for developing applications and libraries
with the QML language. QML is designed to be easily extensible through C++ code.

The ``QML`` is intended to be used to define the ``UI`` of the application via
``json``-like syntax

```xml
import QtQuick 2.0

Rectangle {
    width: 100
    height: 100

    gradient: Gradient {
        GradientStop { position: 0.0; color: "yellow" }
        GradientStop { position: 1.0; color: "green" }
    }
}
```

A lot of elements are already predefined but it's possible to define new types and UI elements
[from C++](https://doc.qt.io/qt-6/qtqml-cppintegration-definetypes.html), the
low-level API to do that is ``qmlregister()`` and probably I'll update the post
in the future with more about that.

Another part is the [Qt resource system](https://doc.qt.io/qt-5/resources.html), that is a platform independent mechanism
for storing binary files in the application's executable. The resource system is
based on tight cooperation between ``qmake``, ``rcc`` and ``QFile``.

The resources associated with an application are specified in a ``.qrc`` file
that is an ``XML``-based file format that lists files on the disk

```xml
<!DOCTYPE RCC><RCC version="1.0">
<qresource>
    <file>images/copy.png</file>
    <file>images/cut.png</file>
    <file>images/new.png</file>
    <file>images/open.png</file>
    <file>images/paste.png</file>
    <file>images/save.png</file>
</qresource>
</RCC>
```

Resource data can either be compiled into the binary or a binary resource loadable at runtime (externally).

For a resource to be compiled into the binary, the ``.qrc`` file must be
mentioned in the application's ``.pro`` file so that ``qmake`` knows about it.
``qmake`` will produce ``make`` rules to generate a file called
``qrc_application.cpp`` that is linked into the application.

The ``rcc`` tool is used to embed resources into a Qt application during the
build process. It works by generating a C++ source file containing data
specified in a ``.qrc`` file.

But since in this post I'm interested in reverse engineering, here the way all
this stuff is implemented: via the function ``qRegisterResourceData()`` that has
the following signature

```
bool qRegisterResourceData(int version, const unsigned char *tree,
                                         const unsigned char *name, const
                                         unsigned char *data)
```

where

 - ``tree`` is a filesystem tree, where the leaf nodes are the actual files with
   contents
 - ``name`` is an array of ``unicode`` strings where the names of the elements of the
   ``tree`` are contained
 - ``data`` is the actual content of the files.

Since the resources are like global data they are initialized at program startup
via the ``__DT_INIT_ARRAY`` in functions named something like
``_INIT_<integer>``. This allows to find all the global allocated ``QString``.

If you are interested in knowing the format of the argument of
``qRegisterResourceData()`` you have to look at the ``rcc`` source code and in
particular at ``RCCResourceLibrary::output()`` method and its internal calls to

 - ``writeDataBlobs()``
 - ``writeDataNames()``
 - ``writeDataStructure()``

but since we are here let me explain how the data is organized: the most
important is ``tree`` that is generated by ``writeDataStructure()`` with each
entry written via ``RCCFileInfo::writeDataInfo()``; the data structure for each
entry is 22 bytes long

| offset | directory | file |
|--------|-----------|------|
| 0      | name      | name |
| 4      | flags     |      |
| 6      | # child   | country |
| 8      |           | lang |
| 10     | 1st child offset | data offset |
| 14     | last mode | last mode |

**Take in mind that is all big endian**.

Each one of these entries represent a node in a filesystem tree, the file are
the leaf nodes, the other type of nodes are the components of the path where the
files are. So to retrieve the name of the nodes the ``name`` parameter of
``qRegisterResourceData()`` is used, to retrieve the data instead the ``data``
parameter is used.

Take in mind that the data can be compressed via ``qCompress()``, i.e. it
prepends 4 bytes with the uncompressed length (encoded big-endian) and then the
zlib compressed data.

<a name="ghidra"/>
## Ghidra

Now we are going to do something practical, using ``ghidra`` and the information
in the previous sections, we'll develop some scripts to automate all the things.

<a name="warm-up"/>
### Warm up

First of all some useful information about ``ghidra`` scripting: it's possible
to write script for ``ghidra`` in two languages: ``Java`` (the language
``ghidra`` is written) and ``python``; my examples use the latter because I
prefer that.

The most important [APIs](https://ghidra.re/ghidra_docs/api/ghidra/program/flatapi/FlatProgramAPI.html) available are under

```
ghidra.program.flatapi.FlatProgramAPI
ghidra.app.script.GhidraScript
```

To build the decompiler documentation

```
$ cd ./Ghidra/Features/Decompiler/src/decompile/cpp
$ make doc
$ xdg-open ../doc/html/index.html
```


If you want to factorize your code in a module of its own and you want to access
the globals provided by ``ghidra`` you have to add ([issue about it](https://github.com/NationalSecurityAgency/ghidra/issues/1919))

```python
from __main__ import *
```

As a threat, here a table with some important Java classes

| type | description | APIs of interest |
|------|-------------|------------------|
|``Program`` | object which stores all information related to a single program ([API doc](https://ghidra.re/ghidra_docs/api/ghidra/program/model/listing/Program.html)) | ``currentProgram`` |
|``Address`` | An address represents a location in a program ([API doc](https://ghidra.re/ghidra_docs/api/ghidra/program/model/address/Address.html)) | ``currentAddress`` [``toAddr()``](https://ghidra.re/ghidra_docs/api/ghidra/program/flatapi/FlatProgramAPI.html#toAddr(int)) |
|``MemoryBlock`` | Interface that defines a block in memory ([API doc](https://ghidra.re/ghidra_docs/api/ghidra/program/model/mem/MemoryBlock.html)) | [``createMemoryBlock()``](https://ghidra.re/ghidra_docs/api/ghidra/program/flatapi/FlatProgramAPI.html#createMemoryBlock(java.lang.String,ghidra.program.model.address.Address,byte[],boolean)) |
|``Namespace`` | Symbol class for namespaces. ([API doc](https://ghidra.re/ghidra_docs/api/ghidra/program/model/symbol/Namespace.html)) | [``currentProgram.getNamespace()``](https://ghidra.re/ghidra_docs/api/ghidra/program/flatapi/FlatProgramAPI.html#getNamespace(ghidra.program.model.symbol.Namespace,java.lang.String)) [``NamespaceUtils``](https://ghidra.re/ghidra_docs/api/ghidra/app/util/NamespaceUtils.html) |
|``Symbol`` | Interface for a symbol, which associates a string value with an address | [``createLabel()``](https://ghidra.re/ghidra_docs/api/ghidra/program/flatapi/FlatProgramAPI.html#createLabel(ghidra.program.model.address.Address,java.lang.String,boolean,ghidra.program.model.symbol.SourceType)) |
|``HighSymbol`` | A symbol within the decompiler's model of a particular function ([API doc](https://ghidra.re/ghidra_docs/api/ghidra/program/model/pcode/HighSymbol.html)) | |
|``ExternalManager`` | External manager interface. Defines methods for dealing with external programs and locations within those programs [API doc](https://ghidra.re/ghidra_docs/api/ghidra/program/model/symbol/ExternalManager.html) | ``currentProgram.getExternalManager()`` |
|``Reference`` | Base class to hold information about a referring address. Derived classes add what the address is referring to. A basic reference consists of a "from" address, the reference type, the operand index for where the reference is, and whether the reference is user defined ([API doc](https://ghidra.re/ghidra_docs/api/ghidra/program/model/symbol/Reference.html)) | [``getReferencesTo()``](https://ghidra.re/ghidra_docs/api/ghidra/program/model/symbol/Reference.html) |
|``DataType`` | The interface that all datatypes must implement ([API doc](https://ghidra.re/ghidra_docs/api/ghidra/program/model/data/DataType.html)) | [``getDataTypes()``](https://ghidra.re/ghidra_docs/api/ghidra/program/flatapi/FlatProgramAPI.html#getDataTypes(java.lang.String)) [``currentProgram.getDataTypeManager()``](https://ghidra.re/ghidra_docs/api/ghidra/program/database/ProgramDB.html#getDataTypeManager()) [``Variable.getDataType()``](https://ghidra.re/ghidra_docs/api/ghidra/program/model/listing/Variable.html#getDataType()) [``VariableUtilities``](https://ghidra.re/ghidra_docs/api/ghidra/program/model/listing/VariableUtilities.html) [``createData()``](https://ghidra.re/ghidra_docs/api/ghidra/program/flatapi/FlatProgramAPI.html#createData(ghidra.program.model.address.Address,ghidra.program.model.data.DataType)) |
|``FunctionManager`` | The manager for functions ([API doc](https://ghidra.re/ghidra_docs/api/ghidra/program/model/listing/FunctionManager.html))| ``currentProgram.getFunctionManager()`` |

An important concept in ``ghidra`` is ``Namespace`` 

**Note:** ``Function``, ``GhidraClass`` and ``Library`` are implementation of the interface ``Namespace``

<!--
[script to find similar structs](https://github.com/RenaKunisaki/GhidraScripts/blob/4593b93eff7840ce3d2fb219712a524ab398cb0a/FindStruct.py) currentProgram.getDataTypeManager().getAllStructures()
-->

### Calling convention

Before starting using ``ghidra`` a little note: you **must** know how the
variable are passed around in memory and how function calling is implemented in
the architecture of the binary you are disecting otherwise little errors by
tools can throw hours of your time in the trashcan.


<a name="address-spaces"/>
### Address spaces

To refer to "entity" in ``ghidra`` an ``Address`` is used, you can think of it
of something like an offset but it's not enough since  an ``Address`` is
associated to an ``AddressSpace``: there are a few of these

 - **ram:** Modelling the main processor address bus
 - **register:** Modelling a processors registers
 - **unique:** used as a pool for temporary registers
 - **stack:** virtual space stack space, implemented by the class
   [``SpacebaseSpace``](https://www.lockshaw.io/static/ghidra/decompiler/doc/classSpacebaseSpace.html) in the decompiler; in general is used for a lot of
   analysis situations it is convenient to extend the notion of an address space
   to mean bytes that are indexed relative to some base register.
 - **constant:** modelling constant values in pcode expressions
 - **other:** for special/user-defined address spaces


<a name="symbol-namespace"/>
### Symbol&Namespace

The documentation states that a ``Symbol`` is the association of an address with
a string, so it's a more specialized version of a ``Namespace``, that I can
loosely describe as a "category"; in particular when you have a class

```
>>> ss = getSymbol("ScreenShare", None)
>>> type(ss)
<type 'ghidra.program.database.symbol.ClassSymbol'>
>>> ss1 = getNamespace(None, "ScreenShare")
>>> ss1
ScreenShare (GhidraClass)
>>> type(ss1)
<type 'ghidra.program.database.symbol.GhidraClassDB'>
>>> ss1.getSymbol()
ScreenShare
>>> ss1.getSymbol() == ss
True
```

``GhidraClass``: interface for representing class objects in the program,
derives from ``Namespace``

``ClassSymbol``: symbols that represent "classes", extends ``Symbol`` (but it
doesn't have an address associated to it ¯\_(ツ)_/¯).


**Note:** a label is a ``Symbol``, indeed label doesn't exist as a type in the
``ghidra``'s APIs. They exist different "types" associated to a symbol.

Be aware that ``getSymbol()`` gets only global defined symbols, if you want to
obtain symbol associated with the analysis of a function you have to look to
[``HighSymbol``](https://ghidra.re/ghidra_docs/api/ghidra/program/model/pcode/HighSymbol.html).

<a name="selections"/>
### Selections

``currentSelection`` gives you the ``ProgramSelection`` that can be split into
``AddressRange`` with an iterator, usually you have a contiguos piece of memory
so you are going to use ``getFirstRange()``.

Suppose you are selecting a table of pointers to function and you want the list
of it

```
>>> startAddress = currentSelection.getFirstRange().getMinAddress()
>>> count = currentSelection.getFirstRange().getLength()/4
>>> [getFunctionAt(toAddr(getDataAt(startAddress.add(_*4)).getInt(0))) for _ in range(count)]
[ScreenShare::metaObject, qt_metacast, FUN_001496cc, FUN_0014d2b0, FUN_0014da88, <EXTERNAL>::QObject::event, <EXTERNAL>::QObject::eventFilter, <EXTERNAL>::QObject::timerEvent, <EXTERNAL>::QObject::childEvent, <EXTERNAL>::QObject::customEvent, <EXTERNAL>::QObject::connectNotify, <EXTERNAL>::QObject::disconnectNotify]
```

It's also possible to set the selection

```
>>> setCurrentSelection(ProgramSelection(*list(table.getCases()[-2:])))
```


<a name="memory-block"/>
### Memory block

``ghidra`` main usage is reversing binaries and binaries represent static
information about memory organization of running processes: usually you have
indication of region of memory (in same cases with names attached), probably
with permissions where the data in the binary is going to be loaded at runtime.

``ghidra`` represents these regions using memory blocks, accessible in the GUI
via ``Window > Memory Map``.

**Note:** there is a particular memory block named ``EXTERNAL`` that is used for
example for thunked functions and indeed when you look at the name of such
functions you see a prefixed ``EXTERNAL::``: take in mind that **is not a
namespace** but the name of the memory map.

The memory blocks are from where you can read the data from the binary: here a
couple of functions

| Function |
|-------------------------|
| ``int getInt(Address)`` |
| ``byte getByte(Address)`` |
| ``byte[] getBytes(Address, int length)`` |

but if you need to read a "large" chunk of data I advice
for a function like this
```
import jarray

def get_bytes_from_binary(address, length):
    v = jarray.zeros(length, 'b')
    currentProgram.getMemory().getBytes(address, v)

    return v.tostring()
```

<a name="data"/>
### Datatypes

You can query the datatypes with ``getDataTypes()`` that returns a list with
data types with a given name, but something overlooked is the fact that data
types are organized under "categories", that are the folders you see in the "Data
Type manager" panel, if you want to query with respect to the category you can
use ``currentProgram.getDataTypeManager().getDataType(<category>)`` taking in
mind that categories use an explicit path structure

```
>>> list(getDataTypes("QArrayData"))
[/QArrayData
pack(disabled)
Structure QArrayData {
   0   int   4   ref   ""
   4   int   4   size   ""
}
Size = 8   Actual Alignment = 1
, /Demangler/QArrayData
pack(disabled)
Structure QArrayData {
}
Size = 1   Actual Alignment = 1
]
>>> currentProgram.getDataTypeManager().getDataType("/QArrayData")
/QArrayData
pack(disabled)
Structure QArrayData {
   0   int   4   ref   ""
   4   int   4   size   ""
}
Size = 8   Actual Alignment = 1
```

A little note here: to obtain the actual **value** (i.e. an integer, an address
etc...) you have to call ``getValue()`` (yes, it seems obvious but you have to
explore the documentation to notice that ^_^).

A part from the data types you already start with, you can define more complex types from simpler ones,
the most common use case is the definition of a ``struct`` via the ``StructureDataType``

```
>>> from ghidra.program.model.data import StructureDataType
>>> from ghidra.program.model.data import IntegerDataType
>>> from ghidra.program.model.data import DataTypeConflictHandler
>>> structure = StructureDataType("miao", 0)
>>> structure.insertAtOffset(0, IntegerDataType.dataType, 4, "kebab", "")
  0  0  int  4  kebab  ""
>>> structure.insertAtOffset(4, IntegerDataType.dataType, 4, "sauce", "")
  1  4  int  4  sauce  ""
>>> currentProgram.getDataTypeManager().addDataType(structure, DataTypeConflictHandler.REPLACE_HANDLER)
/miao
pack(disabled)
Structure miao {
   0   int   4   kebab   ""
   4   int   4   sauce   ""
}
Size = 8   Actual Alignment = 1
```

Take in mind that you need to save explicitely a new data type
into the database via the ``DataTypeManager``

```
>>> from ghidra.program.model.data import DataTypeConflictHandler
>>> data_type_manager = currentProgram.getDataTypeManager()
>>> data_type_manager.addDataType(structure, DataTypeConflictHandler.DEFAULT_HANDLER)
```

use ``DataTypeConflictHandler.REPLACE_HANDLER`` if you want a substitution
without questions asked, otherwise you could end up with ``conflict`` datatypes.

Obviously is possible to associate an address to some data type via
``createData()`` or retrieve the data via ``getDataAt()``.

If you want to create data types directly from ``C``

```
# from <https://github.com/NationalSecurityAgency/ghidra/issues/1986>
def createDataTypeFromC(declaration):
    from ghidra.app.util.cparser.C import CParser
    from ghidra.program.model.data import DataTypeConflictHandler
    dtm = currentProgram.getDataTypeManager()
    parser = CParser(dtm)
    new_dt = parser.parse(declaration)
    transaction = dtm.startTransaction("Adding new data")
    dtm.addDataType(new_dt, None)
    dtm.endTransaction(transaction, True)

```

**Note:** the data type must be requeried after this call.

**Note2:** bad enough it doesn't work for data types that are not "primitive"
since it's not capable of using already defined types in other archives,
moreover it fucks up packing! so unless you have very basic declaration I advise
to defined data types programmatically.

Since a lot of data types depend on the actual architecture you are on (I'm
looking at you pointers) you can query ``ghidra`` and ask for the size of
certain data types, for example the integers

```
>>> currentProgram.getCompilerSpec().getDataOrganization().getIntegerSize()
4
```


If you want to set some field to big-endian

```
>>> from ghidra.program.model.data import EndianSettingsDefinition
>>> datatype = getDataType("mystruct")
>>> field1 = datatype.components[0]
>>> field1_settings = field1.getDefaultSettings()
>>> field1_settings.setLong('endian', EndianSettingsDefinition.BIG)
```

**Note:** it seems that you **must** save it and then edit the endianess and
then requery it.

**Note:** in the struct editor it seems impossible to edit this setting
manually.

<a name="references"/>
### References

With references you have the possibility to query ``ghidra`` about relations
about different addresses

```
>>> getReferencesTo(currentAddress)
array(ghidra.program.model.symbol.Reference, [From: 0015a33c To: 0015a358 Type: CONDITIONAL_COMPUTED_JUMP Op: -1 ANALYSIS])
```

It's also possible to ask for references to data types

```
>>> print struct
/ScreenShare_vtable_t
pack(disabled)
Structure ScreenShare_vtable_t {
   0   int   4   metaObject   ""
   4   int   4   qt_metacast   ""
   8   int   4   FUN_001496cc   ""
   12   int   4   FUN_0014d2b0   ""
   16   int   4   FUN_0014da88   ""
   20   int   4   event   ""
   24   int   4   eventFilter   ""
   28   int   4   timerEvent   ""
   32   int   4   childEvent   ""
   36   int   4   customEvent   ""
   40   int   4   connectNotify   ""
   44   int   4   disconnectNotify   ""
}
Size = 48   Actual Alignment = 1
>>> from ghidra.util.datastruct import ListAccumulator
>>> from ghidra.app.plugin.core.navigation.locationreferences import ReferenceUtils
>>> lst = ListAccumulator()
>>> ReferenceUtils.findDataTypeReferences(lst, struct, "FUN_0014da88", currentProgram, None)
>>> print type(list(lst)[0])
<type 'ghidra.app.plugin.core.navigation.locationreferences.LocationReference'>
>>> reference = list(lst)[0]
>>> reference.getProgramLocation()
>>> reference.getLocationOfUse()
00233e58
>>> context = list(lst)[0].context
>>> type(context)
<type 'ghidra.app.plugin.core.navigation.locationreferences.LocationReferenceContext'>
>>> context.getPlainText()
u'92: (*(code *)piVar1->_vtable->FUN_0014da88)();'
```

<a name="functions"/>
### Functions

Usually code is organized in "blocks of execution" that can be identified as
functions, and obvously ``ghidra`` as its own way of dealing with that.

This section is more about the "interface" to a function not the analysis of
its internal behaviour, that is subject of a section a little below.
So here you'll se how to retrieve a function, how to set the signature
and calling convention and so on.

An example of the sometime-difficult-to-work-with ``ghidra`` is that I have
yet to find an easy way to, for example, get a function by name reliably, the
code I come up with is the following

```python
def get_function_by_name(name, namespace=None):
    """Little hacky way of finding the function by name since getFunction() by FlatAPI
    doesn't work."""
    candidates = [_ for _ in currentProgram.getFunctionManager().getFunctionsNoStubs(True) if name == _.name]

    if namespace:
        candidates = [_ for _ in candidates if _.getParentNamespace().getName() == namespace]

    if len(candidates) != 1:
        raise ValueError("We expected to find only one of '%s' instead we have %s" % (name, candidates))

    return candidates[0]
```

Another important piece of code is something that returns the references to a given address

```python
def getXref(target_addr):
    """return the xrefs defined towards the target_addr as a list
    having as entries couple of the form (call_addr, calling function)
    where the latter is None when is not defined."""

    references = getReferencesTo(target_addr)

    callers = []

    for xref in references:
        call_addr = xref.getFromAddress()
        caller = getFunctionContaining(call_addr)

        if caller is None:
            logger.warning("found reference to undefined at {}".format(call_addr))

        callers.append((call_addr, caller))

    return callers
```

<!--
```python
>>> currentProgram.getExternalManager().getExternalLibraryNames()
array(java.lang.String, [u'<EXTERNAL>', u'libz.so.1', u'libcrypto.so.1.1', u'libcrypt.so.2', u'libprotobuf.so.22', u'libqt-rappor.so.1', u'libudev.so.1', u'libQt5WebSockets.so.5', u'libsystemd.so.0', u'libQt5DBus.so.5', u'libQt5Svg.so.5', u'libKF5Archive.so.5', u'libQt5Xml.so.5', u'libpdfium.so', u'libpthread.so.0', u'libQt5Quick.so.5', u'libQt5Qml.so.5', u'libQt5Gui.so.5', u'libQtWebAppHttpServer.so.1', u'libQt5Network.so.5', u'libQt5Core.so.5', u'libstdc++.so.6', u'libm.so.6', u'libgcc_s.so.1', u'libc.so.6'])
```
-->

If you want to define programmatically the signature of a function this is the
convoluted way to do that

```python
>>> from ghidra.program.model.data import FunctionDefinitionDataType
>>> from ghidra.program.model.data import IntegerDataType
>>> from ghidra.program.model.data import ParameterDefinitionImpl
>>> from ghidra.program.model.data import PointerDataType
>>> from ghidra.program.model.data import VoidDataType
>>> from ghidra.program.model.data import GenericCallingConvention
>>> sig = FunctionDefinitionDataType("miao")
>>> param1 = ParameterDefinitionImpl('kebab', IntegerDataType.dataType, 'comment')
>>> param2 = ParameterDefinitionImpl('falafel', PointerDataType(VoidDataType.dataType), 'comment bis')
>>> sig.setArguments([param1, param2])
>>> sig.setGenericCallingConvention(GenericCallingConvention.thiscall)
>>> sig
undefined thiscall miao(int kebab, void * falafel)
```

**Note:** ``PointerDataType()`` can be used without ``.dataType`` (why?)

Now if you want to apply the fucking signature you have to call a fucking command (see this [issue](https://github.com/NationalSecurityAgency/ghidra/issues/1126))

```
>>> from ghidra.app.cmd.function import ApplyFunctionSignatureCmd
>>> from ghidra.program.model.symbol import SourceType
>>> f = getFunctionAt(toAddr(0x0036af14))
>>> runCommand(ApplyFunctionSignatureCmd(f.entryPoint, sig, SourceType.USER_DEFINED))
```

It's instead easy to move a function in a class Namespace:

```python
>>> ht = getNamespace(None, 'HttpManager')
>>> f = getFunctionAt(toAddr(0x0036af14))
>>> f.setParentNamespace(ht)
```

**Note:** It's also possible to change the calling convention directly from the
function using a string via [``setCallingConvention()``](https://ghidra.re/ghidra_docs/api/ghidra/program/model/listing/Function.html#setCallingConvention(java.lang.String)).
You can also define a data type from a function definition (vtable anyone?)

```
>>> from ghidra.program.model.data import FunctionDefinitionDataType
>>> from ghidra.program.model.data import PointerDataType
>>> functionDefinitionDatatype = FunctionDefinitionDataType(function, False)
>>> functionDefinitionDatatype
undefined stdcall FUN_001924a0(QObject * param_1, int param_2)
>>> PointerDataType(functionDefinitionDatatype)
FUN_001924a0 *
```

Sometimes you have **thunked functions** and you want to
retrieve the original mangled name

```
                             **************************************************************
                             *                       THUNK FUNCTION                       *
                             **************************************************************
                             thunk undefined __thiscall operator<<(QDataStream * this
                               Thunked-Function: <EXTERNAL>::QDataStream
                               assume TMode = 0x0
             undefined         r0:1            <RETURN>
             QDataStream *     r0:4 (auto)     this
             longlong          Stack[0x0]:8    param_1
                             <EXTERNAL>::QDataStream::operator<<             XREF[2]:     operator<<:00038620(T), 
                                                                                          operator<<:00038628(c), 
                                                                                          005a4054(*)  
         EXTERNAL:00719da8                               ??                 ??
         EXTERNAL:00719da9                               ??                 ??
         EXTERNAL:00719daa                               ??                 ??
         EXTERNAL:00719dab                               ??                 ??

```

```
>>> func = getFunctionAt(currentAddress)
>>> thunk = func.getThunkedFunction(True)
>>> thunk.getSymbol().getSymbolStringData()
u',_ZN11QDataStreamlsEx'
>>> from ghidra.app.util.demangler import DemanglerUtil
>>> DemanglerUtil.demangle(currentProgram, thunk.getSymbol().getSymbolStringData()[1:])
undefined QDataStream::operator<<(long long)
```

**Note:** the last command removed the ``_`` prepending the mangled name, otherwise
it doesn't demangle ¯\_(ツ)_/¯

<a name="analysis"/>
## ``ghidra`` analysis under the hood

This and the following sections are more involved with internals of how
``ghidra`` "understands" things and so it's not directly related to the act of
reversing but can be pretty useful to wrap your head around and knowing that
some information exists somewhere to look for.

The main assumption here is that ``ghidra``, when analizes the code, has two
different possible interpretation of what is happening: **code** and **data**
(this is true also in real binaries and code execution); you can see the
instructions creating a directed graph between them, where the jump from one
node to the other **can** be data-dependent, but you can also see the
instructions as edges that link transition of data from one state to another.

When you are talking about code in ``ghidra`` you use the ``Pcode``, when you
are talking about data you are using ``Varnode``, probably is a little more
complex than that but let things simpler.

To remeber that relation, take in mind this methods to pass from one to another

```
varnode.getDef() -> PcodeOp
pcodeop.getInputs() -> Varnode[]
```

<!--
Pcode, Ghidra's IL, is a register transfer language. Pcode exists in two
primary forms: **raw** and **refined**.

https://www.lockshaw.io/static/ghidra/decompiler/doc/index.html
-->


Take in mind that all of these concepts apply to functions analysis and that
to analyze variables you need to commit locally them, like using
``HighFunctionDBUtil.commitLocalNamesToDatabase(high_func, SourceType.USER_DEFINED)``.

Here a table with some definitions

| Entity | Description |
|--------|-------------|
| ``Varnode`` | sequence of bytes in an address space, represented as a triple (address space, offset, size); It's a central concept for the decompiler, it forms the individual nodes in the decompiler's data-flow representation of functions. |
| ``VarnodeAST`` | is a node in an ``AbstractSyntaxTree``; it keeps track of its defining ``PcodeOp`` (in-edge) (``VarnodeAST.getDef()``) and ``PcodeOp``s which use it (out-edges) (``VarnodeAST.getDescendendants()``) |
| ``HighVariable`` | is a set of varnodes that represent the storage of an entire variable in high-level language being output by the decompiler |
| ``HighFunction`` | high-level abstraction associated with a low-level function made up of assembly instructions |

<a name="opcodes"/>
### Analyzing opcodes

In the section above I described some code to get the ``xrefs`` from a function to another,
in particular we are able to get the tuple (``address``, ``function``) where
this reference come from; if we want to extract information about the arguments
with which the function is called with can use the ``Pcode`` directly like in
this example:

```python
>>> from ghidra.app.decompiler import DecompileOptions
>>> from ghidra.app.decompiler import DecompInterface
>>> from ghidra.util.task import ConsoleTaskMonitor
>>> monitor = ConsoleTaskMonitor()
>>> ifc = DecompInterface()
>>> options = DecompileOptions()
>>> ifc.setOptions(options)
True
>>> ifc.openProgram(currentProgram)
True
>>> func = getFunctionContaining(currentAddress)
>>> func
KeyboardBridgeServer::connectedChanged
>>> res = ifc.decompileFunction(func, 60, monitor)
>>> res
ghidra.app.decompiler.DecompileResults@46c33206
>>> high_func = res.getHighFunction()
>>> high_func.getPcodeOps(toAddr(0x00c8d64))
java.util.AbstractMap$2$1@4511ac6b
>>> pcodeops = high_func.getPcodeOps(toAddr(0x00c8d64))
>>> op = pcodeops.next()
>>> op
 ---  CALL (ram, 0x3b0e0, 8) , (unique, 0x10000009, 4) , (unique, 0x1000000d, 4) , (const, 0x0, 4) , (const, 0x0, 4)
>>> op.getInputs()
array(ghidra.program.model.pcode.Varnode, [(ram, 0x3b0e0, 8), (unique, 0x10000009, 4), (unique, 0x1000000d, 4), (const, 0x0, 4), (const, 0x0, 4)])
```

moreover, now we have the tool to extract the information about local variables
defined in the function by the decompiler

```
>>> [_.getName()  for _ in res.getHighFunction().getLocalSymbolMap().getSymbols()]
[u'ret', u'bVar1', u'cVar3', u'pQVar2', u'iVar4', u'pQVar6', u'pQVar5',
  u'type_of_message', u'local_34', u'local_30', u'local_2c', u'local_28',
  u'local_24', u'local_20', u'connection', u'local_1c', u'inStream']
```
Now, to apply this to something practical, something we talked about before, let
me show how to extract the arguments from a call to ``qRegisterResourceData()``:
suppose we are "lucky" and the decompiler shows us the following situation

```
void _INIT_3(void)

{
  qRegisterResourceData(3,"","","");
  __aeabi_atexit(&DAT_005a7ec4,&LAB_000464a8,&DAT_005a7c44);
  return;
}

```

if I place the cursor at the function name in the decompiler panel I can obtain
    the operation with its arguments

```
>>> currentLocation.getToken().getPcodeOp()
 ---  CALL (ram, 0x3a294, 8) , (const, 0x3, 4) , (unique, 0x1000001e, 4) , (unique, 0x1000001a, 4) , (unique, 0x10000022, 4)
```

**Note:** for some strange reason, the address where the Pcode is can be
extracted via ``getSeqnum()``

```
>>> call.getSeqnum()
(ram, 0x3e80c, 59, 6)
```

Remember, this function takes four arguments, the first one is the integer
representing the version, the other three are pointers; the integer one is
trivial to retrieve (note that the 0th argument of the opcode is the address of
the function to call)

```
>>> op = currentLocation.getToken().getPcodeOp()
>>> op.getInput(1)
(const, 0x3, 4)
>>> type(op.getInput(1))
<type 'ghidra.program.model.pcode.VarnodeAST'>
>>> op.getInput(1).getAddress()
const:00000003
>>> op.getInput(1).getOffset()
3L
```

and here the thing: remember when I told you a ``Varnode`` is a triple? this
is in the ``const`` address space, at address ``0x3`` and 4bytes wide.

Now look for the second argument

```
>>> ptr = op.getInput(2)
>>> type(ptr)
<type 'ghidra.program.model.pcode.VarnodeAST'>
>>> ptr.getDef()
(unique, 0x1000001e, 4) COPY (const, 0x44c454, 4)
>>> ptr.getDef().getInput(0)
(const, 0x44c454, 4)
```

here we don't have a direct constant but a ``COPY`` of the constant inside the
variable; you can inspect the variable to get more information out of it

```
>>> ptr.getHigh()
ghidra.program.model.pcode.HighOther@132988de
>>> ptr.getHigh().getName()
u'UNNAMED'
>>> ptr.getHigh().getDataType()
uchar *
```

in particular it is a ``uchar`` pointer.

This seems simple, but not always the decompiler is able to have clean data
definition and you can end up in situations like the following where some data
defined over the one we are interested in, causes the analysis to mess
up the "arithmetics": the second argument is still a pointer but the problem is
that the pointer is in the middle of an already defined string, so the
decompiler get around doing some casting

```
void _INIT_2(void)

{
  qRegisterResourceData
            (3,(uchar *)((int)
                         L"<imagine gibberish data here>"
                        + 0x475),"","");
  __aeabi_atexit(&DAT_005a7ec0,FUN_000463d0,&DAT_005a7c44);
  return;
}
```

If I place the cursor over the function name you can manually disect the
arguments passed to it:

```
>>> currentLocation.getToken().getPcodeOp()
 ---  CALL (ram, 0x3a294, 8) , (const, 0x3, 4) , (unique, 0x10000022, 4) , (unique, 0x1000001a, 4) , (unique, 0x10000026, 4)
>>> call = currentLocation.getToken().getPcodeOp()
>>> call.getInputs()
array(ghidra.program.model.pcode.Varnode, [(ram, 0x3a294, 8), (const, 0x3, 4), (unique, 0x10000022, 4), (unique, 0x1000001a, 4), (unique, 0x10000026, 4)])
```

I'm interested in the second argument, i.e. the pointer to the string data

```
>>> ptr = call.getInput(2)
>>> ptr
(unique, 0x10000022, 4)
```

The first operation is a ``CAST``

```
>>> ptr.getDef()
(unique, 0x10000022, 4) CAST (unique, 0x10000036, 4)
```

it has only one input

```
>>> ptr.getDef().getInputs()
array(ghidra.program.model.pcode.Varnode, [(unique, 0x10000036, 4)])
>>> ptr.getDef().getInput(0)
(unique, 0x10000036, 4)
```

we can follow the chain to retrieve the operations that generated it

```
>>> ptr.getDef().getInput(0).getDef()
(unique, 0x10000036, 4) INT_ADD (unique, 0x10000032, 4) , (const, 0x475, 4)
```

it's ``INT_ADD`` with two operands, one is another ``Varnode``, the other a costant;
for the first we can descend the different operations until we obtain a
``const`` representing an address, i.e. ``0x404303`` that summed to the second
argument gives us the right address where the data lives

```
>>> ptr.getDef().getInput(0).getDef().getInput(0)
(unique, 0x10000032, 4)
>>> ptr.getDef().getInput(0).getDef().getInput(0).getDef()
(unique, 0x10000032, 4) CAST (unique, 0x1000001e, 4)
>>> ptr.getDef().getInput(0).getDef().getInput(0).getDef().getInput(0)
(unique, 0x1000001e, 4)
>>> ptr.getDef().getInput(0).getDef().getInput(0).getDef().getInput(0).getDef()
(unique, 0x1000001e, 4) COPY (const, 0x404303, 4)
>>> ptr.getDef().getInput(0).getDef().getInput(0).getDef().getInput(0).getDef().getInput(0)
(const, 0x404303, 4)
>>> ptr.getDef().getInput(0).getDef().getInput(1)
(const, 0x475, 4)
>>> toAddr(0x404303 + 0x475)
00404778
```

In general it's tricky to generalize a function to extract arguments from a
call, in particular because you can have argument passed using variables on the
stack (did you notice all the previous example used global defined data?).

Suppose I want to extract the string pointed from the field ``uri`` in the
following function call

```
struct {
    int versions;
    char* uri;

} kebab;

void somefunction() {
    /* something happening
      before */
    struct kebab api {
        .version = 4;
        .uri = "miao";
    };

    if (<some condition>) {
        /* stuff I don't care about */
    }

    QQmlPrivate::qmlregister(SingletonRegistration,&api);
}
```

Let's start with the obvious

```
>>> op.getInput(2)
(register, 0x2c, 4)
```

but we are not lucky trying to find something useful directly from this
``Varnode``

```
>>> type(op.getInput(2))
<type 'ghidra.program.model.pcode.VarnodeAST'>
>>> op.getInput(2)
(register, 0x2c, 4)
>>> op.getInput(2).getHigh()
ghidra.program.model.pcode.HighOther@15347f34
>>> op.getInput(2).getHigh().getDataType()
RegisterSingletonType *
>>> op.getInput(2).getHigh().getName()
u'UNNAMED'
>>> op.getInput(2).getHigh().getInstances()
array(ghidra.program.model.pcode.Varnode, [(register, 0x2c, 4)])
```

We can obtain the actual register used

```
>>> addr = op.getInput(2).getAddress()
>>> currentProgram.getRegister(addr)
r3
```

it should be ``r1`` but there are some operations that probably are hidden under
the rug; if we try with the operation that put the address in ``r3`` we have

```
>>> op.getInput(2).getDef()
(register, 0x2c, 4) PTRSUB (register, 0x54, 4) , (const, 0xffffff10, 4)
>>> currentProgram.getRegister(op.getInput(2).getDef().getInput(0))
sp
```

that is something pointing at the stack (register ``0x54``)! in particular at
offset ``-0xf0`` (the signed encoding of ``0xffffff10``). How we retrieve the
corresponding variable in the function?


```
>>> res.getHighFunction().getFunction().getAllVariables()
array(ghidra.program.model.listing.Variable, [[int * param_1@r0:4], [RegisterSingletonType api@Stack[-0xf0]:44], [undefined1
local_f4@Stack[-0xf4]:1], [undefined4 local_f8@Stack[-0xf8]:4], [undefined4
local_fc@Stack[-0xfc]:4], [undefined1 local_100@Stack[-0x100]:1], [undefined1 bVar1@HASH:4a0331695fe:1]])
```

**Note:** here we are asking the variables via ``Function``, not
``HighFunction`` since the former are the ones saved in the database of
``ghidra``

```
>>> variable = res.getHighFunction().getFunction().getAllVariables()[1]
>>> variable
[RegisterSingletonType api@Stack[-0xf0]:44]
>>> hex(variable.getMinAddress().getUnsignedOffset())
'0xffffff10L'
```

```
>>> variable = res.getHighFunction().getFunction().getStackFrame().getVariableContaining(-0xf0)
>>> variable
[RegisterSingletonType api@Stack[-0xf0]:44]
>>> ref_mgr = currentProgram.getReferenceManager()
>>> offset_field = variable.getStackOffset() + variable.getDataType().getComponent(4).getOffset()
>>> [_ for _ in ref_mgr.getReferencesTo(variable) if _.getFromAddress() < currentAddress and _.getStackOffset() == offset_field]
[From: 00070a20 To: Stack[-0xe0] Type: WRITE Op: 1 ANALYSIS]
>>> ref = [_ for _ in ref_mgr.getReferencesTo(variable) if _.getFromAddress() < currentAddress and _.getStackOffset() == offset_field][0]
>>> hex(ref.getStackOffset())
'-0xe0'
>>> ref.getFromAddress()
00070a20
```

but here we are encounter a blocking problem: if we try to recover a ``Pcode``
from the decompiler here, we have no luck, no instructions defined there.

It's the same problem described in [this post](https://buaq.net/go-112637.html) about reversing Go binaries'
strings.

**Note:** the ``Pcode`` from the listing panel and from the decompiler are
related but are not 1-to-1, probably the decompiler is "synthetizing" the
former.

However we can try to extract the fucking information that is present in the
listing panel

```
>>> from ghidra.program.model.listing import CodeUnitFormat, CodeUnitFormatOptions
>>> codeUnitFormat = CodeUnitFormat(
    CodeUnitFormatOptions(
        CodeUnitFormatOptions.ShowBlockName.ALWAYS,
        CodeUnitFormatOptions.ShowNamespace.ALWAYS,
        "",
        True, True, True, True, True, True, True
    )
)
>>> instr = getInstructionAt(ref.getFromAddress())
>>> instr
str r3,[sp,#0x58]
>>> codeUnitFormat.getRepresentationString(instr)
u'str r3=>.rodata:s_DeviceApp_004fa30c,[sp,#api.typeName+0x138]'
```

**Note:** this is what's called a **pro move**, it's not known to humanity if
it's reliable...

A similar situation can be observed about "blocks": usually it's useful to study
the code of a function using the contiguous blocks of instructions, connected
via control flow instructions.

In order to make an example, I'll try to analyze a ``switch``:
here the magic incantation that allows to obtain information about it

```
>>> tables = res.getHighFunction().getJumpTables()
>>> len(tables)
1
>>> table = tables[0]
>>> table.getSwitchAddress()
0015a33c
>>> table.getLabelValues()
array(java.lang.Integer, [0, 1, 2, 3, 4, 5, 6])
```

from it we can obtain the basic blocks (of ``Pcode``) that starts from the
switch itself and from each case

```
>>> ops = list(res.getHighFunction().getPcodeOps(table.getSwitchAddress()))
>>> [_.getParent() for _ in ops]
[basic@0015a334, basic@0015a334, basic@0015a33c, basic@0015a33c, basic@0015a33c]
>>> set([_.getParent() for _ in ops])
set([basic@0015a33c, basic@0015a334])
>>> get_block_at = lambda addr: [_ for _ in res.getHighFunction().getBasicBlocks() if _.contains(addr)][0]
>>> [get_block_at(_) for _ in table.getCases()]
[basic@0015a344, basic@0015a348, basic@0015a34c, basic@0015a350, basic@0015a354, basic@0015a358, basic@0015a35c]
>>> describe_block = lambda _block: (_block, (_block.getStart(), _block.getStop()),[_block.getIn(_in) for _in in range(_block.getInSize())], [_block.getOut(_out) for _out in range(_block.getOutSize())], list(_block.getIterator()))
```

But it exists an alternative way of obtaining the flow

```
>>> from ghidra.util.task import TaskMonitor
>>> bm.getCodeBlocksContaining(currentAddress, TaskMonitor.DUMMY)
>>> [bm.getCodeBlocksContaining(_, TaskMonitor.DUMMY) for _ in table.getCases()]
[array(ghidra.program.model.block.CodeBlock, [caseD_0  src:[0015a33c] dst:[0015a43c]]), array(ghidra.program.model.block.CodeBlock, [caseD_1 src:[0015a33c]  dst:[0015a4a0]]), array(ghidra.program.model.block.CodeBlock, [caseD_2  src:[0015a33c]  dst:[0015a44c]]),
array(ghidra.program.model.block.CodeBlock, [caseD_3  src:[0015a33c] dst:[0015a45c]]), array(ghidra.program.model.block.CodeBlock, [caseD_4 src:[0015a33c]  dst:[0015a46c]]), array(ghidra.program.model.block.CodeBlock, [caseD_5  src:[0015a33c]  dst:[0015a478]]),
array(ghidra.program.model.block.CodeBlock, [caseD_6  src:[0015a33c] dst:[0015a484]])]
```

This is the difficult to explain well in a post but the two different
representations of blocks are similar but not equals since the basic blocks are
generated from the decompiler ``Pcode``, meanwhile the other is generated from
the "raw" ``Pcode`` and are the same blocks (I think) used for the "Function graph"
window.

Last information: if you want to get the ``Varnode`` at the cursor location in
the decompiler panel this is the code for you

```
>>> from ghidra.app.decompiler.component import DecompilerUtils
>>> tokenAtCursor = currentLocation.getToken()
>>> var = DecompilerUtils.getVarnodeRef(tokenAtCursor)
```

### Visualizing table

Sometime is useful to show a table with an entry for address with some related
information, to do that
[``createTableChooserDialog()``](https://ghidra.re/ghidra_docs/api/ghidra/app/script/GhidraScript.html#createTableChooserDialog(java.lang.String,ghidra.app.tablechooser.TableChooserExecutor,boolean)) exists;
suppose we want to have all the calls to ``qmlregister()`` with the name of the class
the is going to register at runtime and I want to have shown in order to
find the constructor and stuff like that;

```python
from ghidra.app.tablechooser import TableChooserExecutor, AddressableRowObject, StringColumnDisplay

class ArgumentsExecutor(TableChooserExecutor):
    def execute(self, rowObject):
        # here some code to execute on the selected row
        return True

    def getButtonName(self):
        return "I'm late!"


class Argument(AddressableRowObject):
    def __init__(self, row):
        # using "address" raises "AttributeError: read-only attr: address"
        self.row = row

    def getAddress(self):
        return self.row[0]


class TypeColumn(StringColumnDisplay):
    def getColumnName(self):
        return u"Type"

    def getColumnValue(self, row):
        return row.row[1]


class ClassNameColumn(StringColumnDisplay):
    def getColumnName(self):
        return u"Class"

    def getColumnValue(self, row):
        return row.row[2]


tableDialog = createTableChooserDialog("qmlregister() calls", ArgumentsExecutor(), False)
tableDialog.addCustomColumn(TypeColumn())
tableDialog.addCustomColumn(ClassNameColumn())

for result in results:
    tableDialog.add(Argument(result))

tableDialog.show()
```

<a name="scripting"/>
## Scripting

Now that we have some ``ghidra`` scripting under our feet, let's try to implement
something useful; what I'll show you is probably improved in my [repository](https://github.com/gipi/ghidra_scripts).

I'm not sure that they work out the box for now since some data types are
assumed to exist at runtime, probably I'll improve them in the future.

**Note:** if you want to associate a key binding to a script you need to add
a line like

```
#@keybinding SHIFT-V
```

in your script and then tick the checkbox in the script listing.

### Vtable

Since there isn't a standard way of building virtual tables in ``ghidra`` I thought about
creating a simple script that from a selection of region containing function
pointers, creates a new ``struct`` using the metadata from the symbol you
labeled the starting address with: the convention I used is that the label will be of
the form ``<class name>::vtable``.

First of all the function that creates the data type: from the name of the
class creates a ``StructureDataType`` with a path strictly dependent from the
class name (for now the dimension is zero, we are going to append its components
one by one)

```python
def build_structure(class_name, startAddress, count):
    path = "{}_vtable_t".format(class_name)
    logger.info("building struct named {}".format(path))
    structure = StructureDataType(path, 0)
```

The code is going to loop for how many function pointers we have told it via the
``count`` parameter: each iteration is going to retrieve the function pointer at
a given offset, dereference the function itself if it exists or creates it.

```python
    for index in range(count):
        logger.debug(" index: {}".format(index))
        address = startAddress.add(index * 4)
        addr_func = toAddr(getDataAt(address).getInt(0))
        function = getFunctionAt(addr_func)

        if function is None:
            logger.info("no function at {}, creating right now!".format(address))
            function = createFunction(addr_func, None)  # use default name
```

if the function is not already in a namespace set to be the same of the class
and if it has the default name set the calling convention to ``__thiscall``

```python

        function_name = function.getName()

        # if it's a function with an already defined Namespace don't change that
        if function.getParentNamespace().isGlobal():
            # set the right Namespace
            namespace = getNamespace(None, class_name)
            function.setParentNamespace(namespace)

        # if is a function not touched from human try to set the calling convention
        # NOTE: for sure is __thiscall since it's a vtable but if the return
        #       value is an object this must go before the "this" pointer
        if function.getName().startswith("FUN_"):
            function.setCallingConvention('__thiscall')
```

obtain the function definition, obtain its datatype and in case update it

```python
        funcDefinition = FunctionDefinitionDataType(function, False)

        logger.debug(" with signature: {}".format(funcDefinition))

        ptr_func_definition_data_type = PointerDataType(funcDefinition)

        # we are going to save definition and all
        # but probably we should clean the old definitions
        # of data types?
        data_type_manager = currentProgram.getDataTypeManager()
        logger.debug("Replacing {}".format(funcDefinition))
        # we replace all the things since they are generated automagically anyway
        data_type_manager.addDataType(funcDefinition, DataTypeConflictHandler.REPLACE_HANDLER)
        data_type_manager.addDataType(ptr_func_definition_data_type, DataTypeConflictHandler.REPLACE_HANDLER)
```

and finally insert it in the virtual table and return it

```python
        structure.insertAtOffset(  # FIXME: in general 4 is not the right size
            index * 4,
            ptr_func_definition_data_type,
            4,
            function_name,
            "",
        )

    return structure
```

This routine is simpler: retrieve the class's ``struct`` doing some check that
it exists

```python
def set_vtable_datatype(class_name, structure):
    path = "/{}".format(class_name)
    class_type = currentProgram.getDataTypeManager().getDataType(path)

    if class_type is None or class_type.isZeroLength():
        raise ValueError("You must define the class '{}' with '_vtable' before".format(class_name))
```

or that its first field is named ``_vtable``

```python
    field = class_type.getComponent(0)
    field_name = field.getFieldName()

    if field_name != "_vtable":
        raise ValueError("I was expecting the first field to be named '_vtable'")
```

and then set the first field with the virtual table structure

```python
    logger.info("set vtable as a pointer to {}".format(structure.getName()))
    field.setDataType(PointerDataType(structure))
```

In the main body of the script we are taking the start address and the number of
the function pointers (note that this is not portable since we are assuming that
a pointer is four bytes wide)

```python
def main():
    startAddress = currentSelection.getFirstRange().getMinAddress()
    count = currentSelection.getFirstRange().getLength() / 4
```

then we take the symbol defined at the start of the selection checking that is
following the previously indicated convention

```python
    sym = getSymbolAt(startAddress)

    if sym is None or sym.getName() != "vtable" or sym.isGlobal():
        raise ValueError(
            "I was expecting a label here indicating the class Namespace, something like 'ClassName::vtable'")

    # FIXME: nested namespaces are not handled correctly
    class_name = sym.getParentNamespace().getName()
    if "::" in class_name:
        raise ValueError("Probably you want to handle manually this one: namespace '{}'".format(class_name))
```

then we use the two previous functions to do the thing

```python
    structure = build_structure(class_name, startAddress, count)

    data_type_manager = currentProgram.getDataTypeManager()
    logger.info("Replacing {}".format(structure.getName()))
    data_type_manager.addDataType(structure, DataTypeConflictHandler.REPLACE_HANDLER)

    set_vtable_datatype(class_name, structure)
```

Since the virtual table is automagically generated, the script everytime
overwrites it without any check.

### QString

The first thing that I explained, related to ``Qt`` was the ``QString``
data type, so let write some code that creates something that can be used like
normal strings: first of all, let define a class with some constants that we are
going to use later

```python
class QString:
	INDEX_QARRAYDATA_OFFSET = 3
	INDEX_QARRAYDATA_LENGTH = 1
```

then the initialization function, where we pass the address where we want to
create the ``QString``: save the address for later use

```python
	def __init__(self, address):
		self.address = address
```

try to get the ``QArrayData`` data type (this part needs improvement for sure,
since it's tricky to not step on work already done, for example consider someone
having already defined this data type but for some reason they decided to used a
different layout, if I was going to overwrite ``QArrayData`` in their project
probably their analysis would end in the garbage)

```python
		dataType = getDataTypes("QArrayData")

		if len(dataType) < 1:  # TODO: more check that the datatype is right
			raise ValueError("You must define the QArrayData type")

		self.dataType = dataType[0]
```

double check that the ``ref`` field makes sense for something static

```python
		# sanity check (probably some more TODO)
		if getInt(address) != -1:
			raise ValueError("We are expecting -1 for the 'ref' field")
```

and create the data accordingly (if it's already created it simply returns the
data)

```python
		# create data at the wanted position
		self._d = createData(address, self.dataType)
```

create the reference between the address of the QString and the string itself
(I don't like that creates the reference inside the ``ref`` field but for now I
can live with that)

```python
		# create reference
		rm = currentProgram.getReferenceManager()

		to_address = address.add(self.offset)

		rm.addOffsetMemReference(
			address,
			to_address,
			self.offset,
			RefType.DATA,
			SourceType.USER_DEFINED,
			0,
		)
```

Now it's time to create, or at least retrieve, the string associated with this
object (``QString`` stores internally data as ``utf16`` little endian)

```python
		self.data = getDataAt(to_address)

		# we try to define a unicode string but maybe
		# some others data was defined before so we simply
		# get the string and whatever
		if self.data is None:
			try:
				self.data = createUnicodeString(to_address)
				str_ = self.data.value
			except CodeUnitInsertionException as e:
				logger.warning("--- code conflict below ---")
				logger.exception(e)
				logger.warning("---------------------------")
				# we haven't any data defined, use unicode
				self.data = common.get_bytes_from_binary(to_address, self.size * 2)
				str_ = self.data.decode('utf-16le')
		else:
			str_ = self.data.value
```
and set a label mimicking the string itself

```python
		createLabel(address, 'QARRAYDATA_%s' % slugify(str_), True)
```

What remains are a couple of accessory methods used to retrieve the fields in
the ``QArrayData`` structure

```python
	@property
	def offset(self):
		return self._d.getComponent(self.INDEX_QARRAYDATA_OFFSET).value.getValue()

	@property
	def size(self):
		"""This is the value as is, if you need the length of the unicode encoded
		data you need to multiply this by 2."""
		return self._d.getComponent(self.INDEX_QARRAYDATA_LENGTH).value.getValue()

	@property
	def end(self):
		"""Return the address where the data pointed by this ends"""
		return self.address.add(self.offset + self.size * 2)

	@property
	def end_aligned(self):
		"""Return the address where the data pointed by this end but aligned"""
		return self.address.add((self.offset + (self.size + 1) * 2 + 3) & 0xfffffc)  # FIXME: generate mask
```

Now it's possible to use it on a script with the following lines

```python
def main(address):

    string = QString(address)
    # move the cursor at the adjacent location
    goTo(string.end_aligned)

main(currentAddress)
```

and you have a procedure to create a ``QString`` at the address where you have
the cursor and have it advancing at the end of the string when done.

### QML

As described in the section about ``QML``, ``Qt`` based binaries contain
resources inside them that the application loads at runtime by the use of the
function ``qRegisterResourceData()``; creating a script that from the address of
the function finds all the points where is called extracting its arguments it's
possible to dump all the resources.

I don't waste space in explaining it here line by line since it's pratically
explained in the section about the ``ghidra``'s APIs and the rest is matter of
extracting filesystem nodes, however you can find it on [github](https://github.com/gipi/ghidra_scripts/blob/main/QTResource.py).

### QObject

Same for a script regarding the extraction of metadata of a class that inherits
from ``QObject``: it's on [github](https://github.com/gipi/ghidra_scripts/blob/main/QTMetaObject.py), it needs improvements,
for example it's not yet able to retrieve the type of the arguments of a
function.

## Links

 - [Reversing ``C++`` notes](https://www.blackhat.com/presentations/bh-dc-07/Sabanal_Yason/Paper/bh-dc-07-Sabanal_Yason-WP.pdf)
 - https://doc.qt.io/qt-5/configure-options.html
 - [The Qt Resource System](https://doc.qt.io/qt-5/resources.html)
 - [Qt QML](https://doc.qt.io/qt-5/qtqml-index.html)
 - [Defining QML Types from C++](https://doc.qt.io/qt-5/qtqml-cppintegration-definetypes.html)
 - [How Qt Signals and Slots Work](https://woboq.com/blog/how-qt-signals-slots-work.html)
 - [What ``__cxa_guard_acquire`` does](https://manishearth.github.io/blog/2015/06/26/adventures-in-systems-programming-c-plus-plus-local-statics/)
 - [QML Syntax Basics](https://doc.qt.io/qt-5/qtqml-syntax-basics.html)
 - [Qt D-Bus](https://doc.qt.io/qt-5/qtdbus-index.html)
 - [GhidraSnippets](https://github.com/HackOvert/GhidraSnippets)
 - https://github.com/AllsafeCyberSecurity/awesome-ghidra
 - https://docs.microsoft.com/en-us/shows/c9-lectures-stephan-t-lavavej-standard-template-library-stl-/c9-lectures-introduction-to-stl-stephan-t-lavavej
 - https://caxapa.ru/thumbs/656023/IHI0042F_aapcs.pdf
 - [Ghidra: Version Tracking](https://www.youtube.com/watch?v=K83T7iVla5s)
 - [Resolving ARM Syscalls in Ghidra](https://syscall7.com/resolving-arm-syscalls-in-ghidra/)
 - [Automated Struct Identification with Ghidra](https://blog.grimm-co.com/2020/11/automated-struct-identification-with.html)
