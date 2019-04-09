from enum import Enum

class KratosConstants :

    class ExtAcquisitionStatus(Enum) :
        IDLE = 1
        INITIALIZING = 2
        WAITING_FOR_TRIGGER = 3
        RUNNING = 4
        TERMINATING = 5
        UNKNOWN = 6