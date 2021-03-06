/**
 * Copyright (c) 2020 SUSE LLC
 *
 * This software is licensed to you under the GNU General Public License,
 * version 2 (GPLv2). There is NO WARRANTY for this software, express or
 * implied, including the implied warranties of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
 * along with this software; if not, see
 * http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
 *
 * Red Hat trademarks are not licensed under GPLv2. No permission is
 * granted to use or replicate Red Hat trademarks that are incorporated
 * in this software or its documentation.
 */

package com.redhat.rhn.domain.contentmgmt.modulemd;

import java.util.Objects;

/**
 * Represents a module in a modular repository
 */
public class Module {

    private String name;
    private String stream;

    /**
     * Initialize a new Module instance
     * @param nameIn the name of the module
     * @param streamIn the name of the stream
     */
    public Module(String nameIn, String streamIn) {
        this.name = nameIn;
        this.stream = streamIn;
    }

    public String getName() {
        return name;
    }

    public String getStream() {
        return stream;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }
        Module module = (Module) o;
        return name.equals(module.name) && Objects.equals(stream, module.stream);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, stream);
    }
}
