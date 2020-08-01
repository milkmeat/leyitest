package com.leyinetwork.udf;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import com.amazonaws.athena.connector.lambda.handlers.UserDefinedFunctionHandler;

public class PythonUnpackHandler
    extends UserDefinedFunctionHandler
{
    private static final String SOURCE_TYPE = "leyinetwork";

    public PythonUnpackHandler()
    {
        super(SOURCE_TYPE);
    }


    public List  test1(Integer p)
    {
        ArrayList<Long> sub1= new ArrayList<Long>();
        sub1.add(1L);
        sub1.add(2L);

        return sub1;
    }

    public Integer test2(Integer p)
    {
            return 100;
    }


    public List  testfunc(Integer p )
    {
        ArrayList<ArrayList<Long>> result=new ArrayList<ArrayList<Long> >();

        ArrayList<Long> sub1= new ArrayList<Long>();
        sub1.add(1L);
        sub1.add(2L);

        ArrayList<Long> sub2= new ArrayList<Long>();
        sub2.add(3L);
        sub2.add(4L);

        result.add(sub1);
        result.add(sub2);


        return result;
    }

    public List unpack(String pattern, String data)
    {
        // java 中没有 unsigned，所以为了实现 unsigned，需要使用比原本类型更大的类型，通过位运算获取其 unsigned 的值
        // unsigned byte & short -> int，unsigned int -> long
        //所有整数都转换到Long，这样不需要额外处理unsigned 的问题
        ArrayList<ArrayList<Long>> result=new ArrayList<ArrayList<Long> >();

        byte[] decodedBytes = Base64.getDecoder().decode(data);

        int readIndex=0;
        while (decodedBytes.length>readIndex)
        {
            int patternIndex=0;
            ArrayList<Long> child = new ArrayList<Long>();
            while(pattern.length()>patternIndex)
            {
                char code = pattern.charAt(patternIndex);


                // see python struct coding at https://docs.python.org/3/library/struct.html
                if (code == 'x'){
                    readIndex += 1;
                }
                else if (code == 'I'){  //unsigned int, 4 bytes
                    int size=4;
                    child.add(extractBySize(decodedBytes, readIndex, size));
                    readIndex+=size;
                }
                else if (code == 'H'){ //unsigned short, 2 bytes
                    int size=2;
                    child.add(extractBySize(decodedBytes, readIndex, size));
                    readIndex+=size;
                }
                else if (code == 'q'){ //long long, 8 bytes
                    int size=8;
                    child.add(extractBySize(decodedBytes, readIndex, size));
                    readIndex+=size;
                }
                else if (code == 'B'){ //unsigned char, 1 bytes
                    int size=1;
                    child.add(extractBySize(decodedBytes, readIndex, size));
                    readIndex+=size;
                }
                else{
                    throw new IllegalArgumentException("unsupported python struct code: "+code);
                }

                patternIndex+=1;
            }
            result.add(child);
        }

        return result;
    }

    private Long extractBySize(byte[] decodedBytes, int readIndex, int size) {
        ByteBuffer bb = ByteBuffer.allocate(8);
        bb.order(ByteOrder.LITTLE_ENDIAN);
        bb.put(decodedBytes,readIndex, size);
        Long l = bb.getLong(0);

        return l;
    }
}