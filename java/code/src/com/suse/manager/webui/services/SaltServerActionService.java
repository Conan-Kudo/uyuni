/**
 * Copyright (c) 2016 SUSE LLC
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
package com.suse.manager.webui.services;

import com.redhat.rhn.domain.action.Action;
import com.redhat.rhn.domain.action.ActionFactory;
import com.redhat.rhn.domain.action.RebootAction;
import com.redhat.rhn.domain.action.errata.ErrataAction;
import com.redhat.rhn.domain.action.server.ServerAction;
import com.redhat.rhn.domain.errata.Errata;
import com.redhat.rhn.domain.server.MinionServer;
import com.redhat.rhn.domain.server.ServerFactory;
import com.redhat.rhn.manager.entitlement.EntitlementManager;

import com.suse.manager.webui.services.impl.SaltAPIService;
import com.suse.salt.netapi.calls.LocalCall;
import com.suse.salt.netapi.calls.modules.Pkg;
import com.suse.salt.netapi.calls.modules.Schedule;
import com.suse.salt.netapi.datatypes.target.MinionList;
import com.suse.salt.netapi.datatypes.target.Target;
import com.suse.salt.netapi.exception.SaltException;

import org.apache.log4j.Logger;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Takes {@link Action} objects to be executed via salt.
 */
public enum SaltServerActionService {

    /* Singleton instance of this class */
    INSTANCE;

    /* Logger for this class */
    private static final Logger LOG = Logger.getLogger(SaltServerActionService.class);

    /**
     * Execute a given {@link Action} via salt.
     *
     * @param actionIn the action to execute
     */
    public void execute(Action actionIn) {
        List<MinionServer> minions = Optional.ofNullable(actionIn.getServerActions())
                .map(serverActions -> serverActions.stream()
                        .flatMap(action ->
                                action.getServer().asMinionServer()
                                        .map(Stream::of)
                                        .orElse(Stream.empty()))
                        .filter(m -> m.hasEntitlement(EntitlementManager.SALT))
                        .collect(Collectors.toList())
                )
                .orElse(new LinkedList<>());

        Map<LocalCall<?>, List<MinionServer>> allCalls;
        if (actionIn.getActionType().equals(ActionFactory.TYPE_ERRATA)) {
            allCalls = errataAction(minions, (ErrataAction) actionIn);
        }
        else if (actionIn.getActionType().equals(ActionFactory.TYPE_REBOOT)) {
            allCalls = rebootAction(minions);
        }
        else {
            if (LOG.isDebugEnabled()) {
                LOG.debug("Action  " + actionIn.getActionType() + " is not supported with Salt");
            }
            return;
        }

        // now prepare each call
        for (Map.Entry<LocalCall<?>, List<MinionServer>> entry : allCalls.entrySet()) {
            LocalCall<?> call = entry.getKey();
            List<MinionServer> targetMinions = entry.getValue();
            Target<?> target = new MinionList(
                    targetMinions.stream()
                            .map(MinionServer::getMinionId)
                            .collect(Collectors.toList()));
            if (LOG.isDebugEnabled()) {
                LOG.debug("Scheduling errata action for: " + target.getTarget());
            }

            LocalDateTime earliestAction = actionIn.getEarliestAction().toInstant()
                    .atZone(ZoneId.of("UTC")).toLocalDateTime();
            Map<String, Long> metadata = new HashMap<>();
            metadata.put("suma-action-id", actionIn.getId());

            try {
                Map<String, Schedule.Result> resultMap = SaltAPIService.INSTANCE
                        .schedule(
                                "scheduled-action-" + actionIn.getId(),
                                call, target, earliestAction, metadata);

                // Update the server action based on the result of the schedule call
                for (MinionServer targetMinion : targetMinions) {
                    Optional<ServerAction> optionalServerAction = actionIn.getServerActions()
                            .stream().filter(sa -> sa.getServerId().equals(targetMinion.getId()))
                            .findFirst();
                    optionalServerAction.ifPresent(serverAction -> {
                        Schedule.Result result = resultMap.get(targetMinion.getMinionId());

                        if (result != null && result.getResult()) {
                            serverAction.setPickupTime(new Date());
                        } else {
                            // There is no result when scheduling has failed
                            LOG.debug("Failed to schedule action for minion '" +
                                    targetMinion.getMinionId() + "'");
                            serverAction.setCompletionTime(new Date());
                            serverAction.setResultCode(-1L);
                            serverAction.setResultMsg("Failed to schedule action.");
                            serverAction.setStatus(ActionFactory.STATUS_FAILED);
                            ActionFactory.save(serverAction);
                        }
                    });
                }
            }
            catch (SaltException saltException) {
                // in a general exception we need to fail all minions (we don't have a result)
                for (MinionServer targetMinion : targetMinions) {
                    Optional<ServerAction> optionalServerAction = actionIn.getServerActions()
                            .stream().filter(sa -> sa.getServerId().equals(targetMinion.getId()))
                            .findFirst();
                    optionalServerAction.ifPresent(serverAction -> {
                        LOG.debug("Failed to schedule action for minion '" +
                                targetMinion.getMinionId() + "': " + saltException.getMessage());
                        serverAction.setCompletionTime(new Date());
                        serverAction.setResultCode(-1L);
                        serverAction.setResultMsg("Failed to schedule action.");
                        serverAction.setStatus(ActionFactory.STATUS_FAILED);
                        ActionFactory.save(serverAction);
                    });
                }
            }
        }
    }

    public Map<LocalCall<?>, List<MinionServer>> errataAction(List<MinionServer> minions, ErrataAction errataAction) {
        Set<Long> serverIds = minions.stream()
                .map(MinionServer::getId)
                .collect(Collectors.toSet());
        Set<Long> errataIds = errataAction.getErrata().stream()
                .map(Errata::getId)
                .collect(Collectors.toSet());
        Map<Long, Map<Long, Set<String>>> errataNames = ServerFactory
                .listErrataNamesForServers(serverIds, errataIds);
        // Group targeted minions by errata names
        Map<Set<String>, List<MinionServer>> collect = minions.stream().collect(Collectors.groupingBy(minion ->
                errataNames.get(minion.getId())
                        .entrySet().stream()
                        .map(Map.Entry::getValue)
                        .flatMap(Set::stream)
                        .collect(Collectors.toSet())
        ));
        // Convert errata names to LocalCall objects of type Pkg.install
        return collect.entrySet().stream().collect(Collectors.toMap(
                entry -> Pkg.install(true, entry.getKey()
                        .stream()
                        .map(patch -> "patch:" + patch)
                        .collect(Collectors.toList()))
                ,
                Map.Entry::getValue
        ));
    }

    public Map<LocalCall<?>, List<MinionServer>> rebootAction(List<MinionServer> minions) {
        Map<LocalCall<?>, List<MinionServer>> ret = new HashMap<>();
        ret.put(com.suse.manager.webui.utils.salt.System.reboot(Optional.empty()), minions);
        return ret;
    }
}
