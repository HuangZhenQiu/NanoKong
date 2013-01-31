import java.io.*;
import nanovm.avr.*;
import nanovm.wkpf.*;
import nanovm.lang.Math;

public class FurExample {

    // =========== Begin: Generated by the translator from application WuML
    /* Component instance IDs to indexes:
    Null => 0
    Null => 1
    */

    //link table
    // fromInstanceIndex(2 bytes), fromPropertyId(1 byte), toInstanceIndex(2 bytes), toPropertyId(1 byte), toWuClassId(2 bytes)
    //eg. (byte)0,(byte)0, (byte)0, (byte)2,(byte)0, (byte)1, (byte)1,(byte)0
    private final static byte[] linkDefinitions = {
        // Note: Component instance id and wuclass id are little endian
        // Note: using WKPF constants now, but this should be generated as literal bytes by the WuML->Java compiler.
        // Connect null to null
        (byte)0, (byte)0, (byte)0, (byte)1, (byte)0, (byte)0, (byte)45, (byte)0,
    };

    //component node id and port number table
    // each row corresponds to the component index mapped from component ID above
    // each row has two items: node id, port number
    private final static byte[][] componentInstanceToWuObjectAddrMap = {
        new byte[]{
                       2, 4,
                       4, 4
                  },
        new byte[]{
                       4, 6,
                       6, 6
                  }
    };

    private final static byte[][] heartbeatToNodeAddrMap = {
        new byte[]{
                       2, 4, 6
                  }
    };
    // =========== End: Generated by the translator from application WuML

    public static void main (String[] args) {
        System.out.println("FurExample");
        System.out.println(WKPF.getMyNodeId());
        WKPF.loadHeartbeatToNodeAddrMap(heartbeatToNodeAddrMap);
        WKPF.loadComponentToWuObjectAddrMap(componentInstanceToWuObjectAddrMap);
        WKPF.loadLinkDefinitions(linkDefinitions);
        initialiseLocalWuObjects();

        while(true){
            VirtualWuObject wuobject = WKPF.select();
            if (wuobject != null) {
                wuobject.update();
            }
        }
    }

    private static void initialiseLocalWuObjects() {
        WKPF.registerWuClass(WKPF.WUCLASS_NULL, GENERATEDVirtualNullWuObject.properties);

        // Only for the first initialization, the backup should have code to
        // create WuObjects when they become the leader...
        if (WKPF.getMyNodeId() == (short)2 || WKPF.getMyNodeId() == (short)4) {
            VirtualWuObject wuclassInstanceNull = new VirtualNullWuObject();
            WKPF.createWuObject((short)WKPF.WUCLASS_NULL, (byte)0x04, wuclassInstanceNull);
            WKPF.setPropertyRefreshRate((short)0, WKPF.PROPERTY_NULL_REFRESH_RATE, (short)3); // Set property to set next_scheduled_update
        }

        if (WKPF.getMyNodeId() == (short)4 || WKPF.getMyNodeId() == (short)6) {
            VirtualWuObject wuclassInstanceNull2 = new VirtualNullWuObject();
            WKPF.createWuObject((short)WKPF.WUCLASS_NULL, (byte)0x06, wuclassInstanceNull2);
            WKPF.setPropertyRefreshRate((short)1, WKPF.PROPERTY_NULL_REFRESH_RATE, (short)3); // Set property to set next_scheduled_update
        }
    }
}
