b ArrayPrototype.cpp:823
commands
echo ---- start of arrayProtoFuncSlice, thisObj ---\n
    print thisObj
	jshex thisObj

    continue
end

b ArrayPrototype.cpp:830
commands
    echo --- just after end = argumentClampedIndexFromStartOrEnd\n
    echo thisObj\n
    jshex thisObj

    continue
end

b JSArray.cpp:704
commands
    echo --- inside fastSlice(), just before memcpy\n
    echo this\n
    jshex this
    echo resultButterfly\n
    x/20xg resultButterfly.contiguousDouble().data() - 1

    continue
end

b JSArray.cpp:709
commands
    echo --- at the end of fastSlice(), after memcpy()\n
    echo this\n
    jshex this
    echo resultButterfly\n
    x/20xg resultButterfly.contiguousDouble().data() - 1

    continue
end

b JSArray.cpp:429
commands
    echo --- inside setLength(), just before reallocateAndShrinkButterfly()\n
    echo this\n
    jshex this

    continue
end

b JSArray.cpp:430
commands
    echo --- inside setLength(), just after reallocateAndShrinkButterfly()\n
    echo this\n
    jshex this

    continue
end
