package com.leyinetwork.udf;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.amazonaws.athena.connector.lambda.handlers.UserDefinedFunctionHandler;

public class PythonUnpackHandler extends UserDefinedFunctionHandler {
    private static final String SOURCE_TYPE = "leyinetwork";
    private HashMap<String, Integer> codeSize = new HashMap<String, Integer>() {
        {
            put("I", 4); // unsigned int, 4 bytes
            put("H", 2); // unsigned short, 2 bytes
            put("q", 8); // long long, 8 bytes
            put("B", 1); // unsigned char, 1 bytes
        }
    };

    public PythonUnpackHandler() {
        super(SOURCE_TYPE);
    }

    public List test1(Integer p) {
        ArrayList<Long> sub1 = new ArrayList<Long>();
        sub1.add(1L);
        sub1.add(2L);

        return sub1;
    }

    public Integer test2(Integer p) {
        return 100;
    }

    public List testfunc(Integer p) {
        ArrayList<ArrayList<Long>> result = new ArrayList<ArrayList<Long>>();

        ArrayList<Long> sub1 = new ArrayList<Long>();
        sub1.add(1L);
        sub1.add(2L);

        ArrayList<Long> sub2 = new ArrayList<Long>();
        sub2.add(3L);
        sub2.add(4L);

        result.add(sub1);
        result.add(sub2);

        return result;
    }

    /**
     * 数据类型通常会以一个模式重复出现，例如解码模式为IHH, 则返回 [[I,H,H],[I,H,H],...] 这样的数据，直到buffer取完
     * 
     * java 中没有 unsigned，所以为了实现 unsigned，需要使用比原本类型更大的类型，通过位运算获取其 unsigned 的值 例如
     * unsigned byte & short -> int，unsigned int -> long
     * 在这里我把所有整数都转换到Long，这样不需要额外处理unsigned 的问题
     * 
     * 这个函数返回嵌套的list，无法被athena解析，因此不能直接暴露给UDF使用
     *
     * @param pattern 例如 IHH
     * @param data    一个base64字符串
     * @return List<List<Long>>
     */
    public List unpack(String pattern, String data) {
        ArrayList<ArrayList<Long>> result = new ArrayList<ArrayList<Long>>();

        byte[] decodedBytes = Base64.getDecoder().decode(data);

        int readIndex = 0;
        while (decodedBytes.length > readIndex) {
            int patternIndex = 0;
            ArrayList<Long> child = new ArrayList<Long>();
            while (pattern.length() > patternIndex) {
                String code = pattern.substring(patternIndex, patternIndex+1);

                // see python struct coding at https://docs.python.org/3/library/struct.html
                if (code == "x") { // padding
                    readIndex += 1;
                } else if (codeSize.containsKey(code)) { 
                    int size = codeSize.get(code);
                    child.add(extractBySize(decodedBytes, readIndex, size));
                    readIndex += size;
                } else {
                    throw new IllegalArgumentException("unsupported python struct code: " + code);
                }

                patternIndex += 1;
            }
            result.add(child);
        }

        return result;
    }

    private Long extractBySize(byte[] decodedBytes, int readIndex, int size) {
        ByteBuffer bb = ByteBuffer.allocate(8);
        bb.order(ByteOrder.LITTLE_ENDIAN);
        bb.put(decodedBytes, readIndex, size);
        Long l = bb.getLong(0);

        return l;
    }

    public List<Long> unpackflat(String pattern, String data) {
        List<List<Long>> result = unpack(pattern, data);
        ArrayList<Long> flat = new ArrayList<Long>();

        for (List<Long> sub : result) {
            for (Long l : sub) {
                flat.add(l);
            }
        }

        return flat;
    }

    public Map<String, Long> building(String data) {
        List<List<Long>> raw = unpack("IHH", data);
        HashMap<String, Long> result = new HashMap<String, Long>();

        for (List<Long> sub : raw) {
            String buindingId = sub.get(1).toString();
            Long buildingLevel = sub.get(2);

            result.put(buindingId, buildingLevel);
        }

        return result;
    }
}