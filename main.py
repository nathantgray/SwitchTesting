import helics as h
import numpy as np
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)


def create_broker(federate_count=1):
    init_string = "--federates={} --name=mainbroker".format(federate_count)
    h.helicsCreateBroker("zmq", "", init_string)


def federate_info(fed):
    # ################################  Registering  federate from json  ########################################
    federate_name = h.helicsFederateGetName(fed)
    count = {"pub": 0, "sub": 0, "ept": 0}
    logger.info(f" Federate {federate_name} has been registered")
    count["pub"] = h.helicsFederateGetPublicationCount(fed)
    count["sub"] = h.helicsFederateGetInputCount(fed)
    count["ept"] = h.helicsFederateGetEndpointCount(fed)
    logger.info(f"Number of publications: {count['pub']}")
    logger.info(f"Number of subscriptions: {count['sub']}")
    logger.info(f"Number of endpoints: {count['ept']}")
    return federate_name, count


def get_links(fed, count):
    # #####################   Reference to Publications and Subscription from index  #############################
    link = {"pub": {}, "sub": {}, "ept": {}}
    for i in range(count["pub"]):
        link["pub"][i] = h.helicsFederateGetPublicationByIndex(fed, i)
        pub_key = h.helicsPublicationGetKey(link["pub"][i])
        logger.info('Registered Publication ---> {}'.format(pub_key))
    for i in range(count["sub"]):
        link["sub"][i] = h.helicsFederateGetInputByIndex(fed, i)
        h.helicsInputSetDefaultComplex(link["sub"][i], 0, 0)
        sub_key = h.helicsSubscriptionGetKey(link["sub"][i])
        logger.info('Registered Subscription ---> {}'.format(sub_key))
    for i in range(count["ept"]):
        link["ept"][i] = h.helicsFederateGetEndpointByIndex(fed, i)
        ept_name = h.helicsEndpointGetName(link["ept"][i])
        logger.info('Registered Endpoint ---> {}'.format(ept_name))

    return link


def destroy_federate(fed):
    h.helicsFederateFinalize(fed)
    h.helicsFederateFree(fed)
    h.helicsCloseLibrary()


def getSubValues(sub):
    pub_type = h.helicsInputGetPublicationType(sub)
    if pub_type.lower() == "double":
        return h.helicsInputGetDouble(sub)
    if pub_type.lower() == "complex":
        v = h.helicsInputGetComplex(sub)
        return complex(v[0], v[1])
    # default to GetString
    return h.helicsInputGetString(sub)


def run():
    config = 'config.json'
    fed = h.helicsCreateCombinationFederateFromConfig(config)
    fed_name, count = federate_info(fed)
    link = get_links(fed, count)
    granted_time = -1

    v_ln_base = 7199.557856794634
    record = []
    end_time = 4

    logger.info("waiting for all feds to enter initialization mode ...")
    h.helicsFederateEnterInitializingMode(fed)
    logger.info("~~~~~~~~~~ Initialization Mode Entered ~~~~~~~~~~")
    h.helicsFederateEnterExecutingMode(fed)
    logger.info("~~~~~~~~~~ Execution Mode Entered ~~~~~~~~~~")
    while granted_time < end_time:
        record_line = []
        granted_time = h.helicsFederateRequestTime(fed, end_time)
        record_line.append(granted_time)
        print(f"{fed_name}: Granted time: {granted_time}")
        # ~~~~~~~~~~~~~ Get data from GLD ~~~~~~~~~~~~~~~~~~~~~~~~
        values = [getSubValues(sub) for sub in link['sub'].values()]  # Get data from each phase and put in list.
        units = [h.helicsInputGetInjectionUnits(sub) for sub in link['sub'].values()]
        print(f"{fed_name}: Sub received value = {values} at time {granted_time} from GLD1")

        # ~~~~~~~~~~~~~ Send data to GLD ~~~~~~~~~~~~~~~~~~~~~~~~
        if round(granted_time, 12) == 1.1:
            cmd = 'OPEN'
            switch_name = 'switch_2_3'
            pub = h.helicsFederateGetPublication(fed, f'{switch_name}_set')
            h.helicsPublicationPublishString(pub, cmd)
            print(f"Sent {cmd} to {switch_name}")
        if round(granted_time, 12) == 1.3:
            cmd = 'CLOSED'
            switch_name = 'switch_2_3'
            pub = h.helicsFederateGetPublication(fed, f'{switch_name}_set')
            h.helicsPublicationPublishString(pub, cmd)
            print(f"Sent {cmd} to {switch_name}")
        if round(granted_time, 12) == 1.5:
            cmd = 'OPEN'
            switch_name = 'switch_4_5'
            pub = h.helicsFederateGetPublication(fed, f'{switch_name}_set')
            h.helicsPublicationPublishString(pub, cmd)
            print(f"Sent {cmd} to {switch_name}")
        if round(granted_time, 12) == 1.7:
            cmd = 'CLOSED'
            switch_name = 'switch_4_5'
            pub = h.helicsFederateGetPublication(fed, f'{switch_name}_set')
            h.helicsPublicationPublishString(pub, cmd)
            print(f"Sent {cmd} to {switch_name}")


if __name__ == '__main__':
    create_broker(2)
    run()
