/**
 * Copyright (c) 2014 SUSE
 *
 * This software is licensed to you under the GNU General Public License,
 * version 2 (GPLv2). There is NO WARRANTY for this software, express or
 * implied, including the implied warranties of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
 * along with this software; if not, see
 * http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
 *
 * SUSE trademarks are not licensed under GPLv2. No permission is
 * granted to use or replicate SUSE trademarks that are incorporated
 * in this software or its documentation.
 */

package com.redhat.rhn.frontend.xmlrpc.serializer;

import com.redhat.rhn.frontend.xmlrpc.serializer.util.SerializerHelper;
import com.suse.scc.model.SCCProduct;
import java.io.IOException;
import java.io.Writer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import redstone.xmlrpc.XmlRpcException;
import redstone.xmlrpc.XmlRpcSerializer;

/**
 * SCCProductSerializer
 * @version $Rev$
 * @xmlrpc.doc
 *   #struct("entry")
 *     #prop_desc("string", "name", "Name of the product")
 *     #prop_desc("string", "label", "Label of the product (identifier)")
 *     #prop_desc("string", "version", "Version")
 *     #prop_desc("string", "release", "Release type")
 *     #prop_desc("string", "arch", "Architecture")
 *     #prop_desc("string", "title", "Title (friendly name)")
 *     #prop_desc("string", "description", "Description")
 *     #prop_desc("string", "status", "Available, unavailable or installed")
 *     #array()
 *       #struct("extensions")
 *         #prop_desc("string", "name", "Extension name")
 *         #prop_desc("string", "label", "Extension label")
 *         #prop_desc("string", "version", "Version")
 *         #prop_desc("string", "release", "Type of the release.")
 *         #prop_desc("string", "arch", "Architecture")
 *         #prop_desc("string", "title", "Title (friendly name)")
 *         #prop_desc("string", "description", "Description")
 *         #prop_desc("string", "status", "Available, unavailable or installed")
 *       #struct_end()
 *     #array_end()
 *   #struct_end()
 */
public class SCCProductSerializer extends RhnXmlRpcCustomSerializer {

    @Override
    public Class getSupportedClass() {
        return SCCProduct.class;
    }

    private Object checkNull(Object value) {
        return value == null ? "" : value;
    }

    private Map<String, Object> serializeProduct(SCCProduct product) {
        Map<String, Object> p = new HashMap<String, Object>();
        p.put("name", this.checkNull(product.getName()));
        p.put("label", this.checkNull(product.getIdentifier()));
        p.put("version", this.checkNull(product.getVersion()));
        p.put("release", this.checkNull(product.getReleaseType()));
        p.put("arch", this.checkNull(product.getArch()));
        p.put("title", this.checkNull(product.getFriendlyName()));
        p.put("description", this.checkNull(product.getDescription()));
        p.put("status", "available"); // XXX: Status should be somehow determined.
        return p;
    }

    private SerializerHelper toSerializer(Map<String, Object> data,
                                          XmlRpcSerializer serializer) {
        SerializerHelper p = new SerializerHelper(serializer);
        for (Map.Entry<String, Object> entry : data.entrySet()) {
            p.add(entry.getKey(), entry.getValue());
        }

        return p;
    }

    @Override
    protected void doSerialize(Object obj, Writer writer, XmlRpcSerializer serializer)
            throws XmlRpcException, IOException {
        SCCProduct product = (SCCProduct) obj;
        SerializerHelper helper = this.toSerializer(this.serializeProduct(product),
                                                    serializer);
        List<Map<String, Object>> extensions = new ArrayList<Map<String, Object>>();
        for (SCCProduct ext : product.getExtensions()) {
            extensions.add(this.serializeProduct(ext));
        }

        helper.add("extensions", extensions);
        helper.writeTo(writer);
    }
}
