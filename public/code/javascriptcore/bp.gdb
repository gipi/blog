b ArrayPrototype.cpp:823
commands
echo ---- start of arrayProtoFuncSlice, thisObj ---\n
    print thisObj
    x/4xg thisObj
    echo thisObj->m_butterfly.get(thisObj)\n
    x/20xg thisObj->m_butterfly.get(thisObj) - 8

    continue
end

b ArrayPrototype.cpp:830
commands
    echo --- just after end = argumentClampedIndexFromStartOrEnd\n
    echo thisObj\n
    x/4xg thisObj
    echo butterfly\n
    x/20xg thisObj->m_butterfly.get(thisObj) - 8

    continue
end

b JSArray.cpp:704
commands
    echo --- inside fastSlice(), just before memcpy\n
    echo this\n
    x/4xg this
    echo m_butterfly.get(this)\n
    x/20xg m_butterfly.get(this)->contiguousDouble().data() - 1
    echo resultButterfly\n
    x/20xg resultButterfly.contiguousDouble().data() - 1

    continue
end

b JSArray.cpp:709
commands
    echo --- at the end of fastSlice(), after memcpy()\n
    echo this\n
    x/2xg this
    echo m_butterfly.get(this)\n
    x/20xg m_butterfly.get(this)->contiguousDouble().data() - 1
    echo resultButterfly\n
    x/20xg resultButterfly.contiguousDouble().data() - 1

    continue
end

b JSArray.cpp:429
commands
    echo --- inside setLength(), just before reallocateAndShrinkButterfly()
    echo this\n
    x/2xg this
    echo m_butterfly.get(this)\n
    x/20xg m_butterfly.get(this)->contiguousDouble().data() - 1

    continue
end

b JSArray.cpp:430
commands
    echo --- inside setLength(), just after reallocateAndShrinkButterfly()
    echo this\n
    x/2xg this
    echo m_butterfly.get(this)\n
    x/20xg m_butterfly.get(this)->contiguousDouble().data() - 1

    continue
end
