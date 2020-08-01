package com.leyinetwork.udf;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;

class PythonUnpackHandlerTest {

    private final PythonUnpackHandler handler = new PythonUnpackHandler();

    @Test
    public void testUnpack() {
        List<List<Long>> result = handler.unpack("IHH",
                "ZQAAAAAAAgCBAAAAMgABAIIAAAAzAAEAgwAAADQAAQCEAAAANQABAHkAAAATAAEAdgAAAAwAAQDNAAAADwABAMsAAAAQAAEAzAAAABEAAQDOAAAAEgABAHsAAAAFAAEAZgAAAAIAAQA=");
        System.out.println(result);
        assertEquals(13, result.size());
        assertEquals(0, result.get(0).get(1));
        assertEquals(2, result.get(0).get(2));
        assertEquals(2, result.get(12).get(1));
    }

    @Test
    public void testUnpackFlat() {
        List<Long> result = handler.unpackflat("IHH",
                "ZQAAAAAAAgCBAAAAMgABAIIAAAAzAAEAgwAAADQAAQCEAAAANQABAHkAAAATAAEAdgAAAAwAAQDNAAAADwABAMsAAAAQAAEAzAAAABEAAQDOAAAAEgABAHsAAAAFAAEAZgAAAAIAAQA=");
        System.out.println(result);
        assertEquals(13 * 3, result.size());
        assertEquals(101, result.get(0));
        assertEquals(0, result.get(1));
        assertEquals(2, result.get(2));
        assertEquals(102, result.get(36));
        assertEquals(2, result.get(37));
        assertEquals(1, result.get(38));
    }

    @Test
    public void testBuilding() {
        List<HashMap<String, Long>> result = handler.building(
                "ZQAAAAAAAgCBAAAAMgABAIIAAAAzAAEAgwAAADQAAQCEAAAANQABAHkAAAATAAEAdgAAAAwAAQDNAAAADwABAMsAAAAQAAEAzAAAABEAAQDOAAAAEgABAHsAAAAFAAEAZgAAAAIAAQA=");
        System.out.println(result);
        assertEquals(13, result.size());
        // assertEquals(2, result.get("0"));
        // assertEquals(1, result.get("2"));
        // assertEquals(1, result.get("17"));
        // assertEquals(1, result.get("19"));
    }     
}

