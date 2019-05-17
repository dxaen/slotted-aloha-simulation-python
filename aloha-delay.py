from SimPy.Simulation import *
from random import Random, expovariate, uniform
import simpy
import os
import threading
import thread

RAND_ONE = 999314
RAND_TWO = 1000000
TRANS_PROB_IN_BACKOFF = 0.001
ARRIVAL_RATE = 1.0




class RV:
        r = Random(RAND_ONE)
        Channel = Resource(1)


class Node(Process):
        ArrivalRate = ARRIVAL_RATE
        TransmissionTime = 1.0
        AcitiveNodes = []
        InactiveNodes = []
        NodeID = 0
        WastedSlots = 0
        NonWastedSlots = 0
        Clock = 0
        TotalPackets = 0
        TransmissionProbabilityInBackoff = TRANS_PROB_IN_BACKOFF
        def __init__(self):
                Process.__init__(self)
                Node.NodeID += 1
                self.ID = Node.NodeID
                Node.InactiveNodes.append(self)
                self.Packets = 0
                self.Flag = 0
        @property
        def Run(self):
                while True:
                        if self.Flag == 0:
                            ArrivalTime = RV.r.expovariate(Node.ArrivalRate)
                            yield hold, self, ArrivalTime
                            self.Packets += 1
                            Node.TotalPackets += 1

                            yield request, self, RV.Channel
                            if RV.Channel.waitQ != []:
                                Node.WastedSlots += 1
                                self.Flag = 1
                                print self.ID, self.Flag
                                yield release, self, RV.Channel
                            else:
                                Node.NonWastedSlots += 1
                                self.Packets -= 1
                                self.Flag = 0
                                yield hold, self, (now() + 1)
                                yield release, self, RV.Channel
                        else:
                            if RV.r.uniform(0,1) < Node.TransmissionProbabilityInBackoff:
                                print now()
                                yield hold, self, 0.000001
                                print RV.Channel.n
                                yield request, self, RV.Channel
                                if RV.Channel.waitQ != []:
                                    Node.WastedSlots += 1

                                    self.Flag = 1
                                    yield release, self, RV.Channel
                                else:
                                    Node.NonWastedSlots += 1
                                    self.Packets -= 1
                                    self.Flag = 0
                                    yield hold, self, (now() + 1)
                                    yield release, self, RV.Channel


def main():
        initialize()
        NodeList = []
        for I in range(6):
            NodeList.append(Node())
            activate(NodeList[I], NodeList[I].Run)

        simulate(RAND_TWO)

        print 'Wasted Slots = ', Node.WastedSlots
        print 'NotWasted = ', Node.NonWastedSlots
        print now()
        print Node.TotalPackets
        Throughput = float(Node.NonWastedSlots)/float(Node.WastedSlots + Node.NonWastedSlots)
        print 'Througput for the system is = ', Throughput

if __name__ == '__primary__':
    class Node(Process, threading.Thread):
        def __init__(self, myID, mutex):
            self.Id = myID
            self.mutex = mutex
            threading.Thread.__init__(self)

        def run(self):
            ArrivalTime = RV.r.expovariate(Node.ArrivalRate)
            yield hold, self, ArrivalTime
            self.Packets += 1
            Node.TotalPackets += 1

            yield request, self, RV.Channel

            if RV.Channel.waitQ != []:
                Node.WastedSlots += 1
                self.Flag = 1
                print self.ID, self.Flag
                yield release, self, RV.Channel
            else:
                Node.NonWastedSlots += 1
                self.Packets -= 1
                self.Flag = 0
                yield hold, self, (now() + 1)
                yield release, self, RV.Channel

    MutexLock = threading.lock()
    totalHosts = []
    for Nodes in range(8):
        Host = Node(Nodes,MutexLock)
        Host.start()
        totalHosts.append(Host)

    for host in totalHosts:
        host.join()


    def PacketTransmit():
        while True:
            packetPID = os.fork()
            if packetPID == 0:
                packetSend()
            else:
                PacketTransmit()


    def packetSend():
        if RV.Channel.waitQ != []:
            Node.WastedSlots += 1
            Flag = 1
            print  Flag
            yield release, RV.Channel
        else:
            NonWastedSlots = 1
            Packets = 1
            Flag = 0
            yield hold, (now() + 1)
            yield release,  RV.Channel


if __name__ == '__main__' : main()
else:

    """
    The following code has been modelled based on the lectures of Professor Norm Matloff, Dept of Computer Science, UC Davis
    This code on testing however was found not to converge with the closed form solution. It also doesn't use any simlation clock
    or multithreading to simulate real time environment I have placed it here just for testing on the interactive prompt and completeness.

    """


    print 'For Interactive Prompt'
    class RV:
        R = random.Random(RAND_TWO)
    class UserForDelay:
        NumberofNodes = input('Enter the number of nodes ')
        WaitingTimeForAllNodes = 0
        NodesWithPackets = []
        NodesWithoutPackets = []
        NumberOfSuccessfullyTransmittedMessages = 1

        def __init__(self):
            UserForDelay.NodesWithoutPackets.append(self)
            self.Delay = 0

        def hasPacketToSend():
            for user in UserForDelay.NodesWithoutPackets:
                if RV.R.uniform(0,1) < 0.5:
                        UserForDelay.NodesWithoutPackets.remove(user)
                        UserForDelay.NodesWithPackets.append(user)
        hasPacketToSend = staticmethod(hasPacketToSend)

        def Send():
            ActiveUser = None
            NumberOfUsersActive = 0
            for user in UserForDelay.NodesWithPackets:
                user.Delay += 1
                if RV.R.uniform(0,1) < 0.5:
                    ActiveUser = user
                    NumberOfUsersActive += 1
            if NumberOfUsersActive == 1:
                UserForDelay.NumberOfSuccessfullyTransmittedMessages += 1
                UserForDelay.WaitingTimeForAllNodes += ActiveUser.Delay
                UserForDelay.NodesWithPackets.remove(ActiveUser)
                UserForDelay.NodesWithoutPackets.append(ActiveUser)
        Send = staticmethod(Send)

    def SimRun():
            for Users in range(UserForDelay.NumberofNodes):
                UserForDelay()

            for rep in range(1000):
                UserForDelay.hasPacketToSend()
                UserForDelay.Send()

            print 'Mean', UserForDelay.WaitingTimeForAllNodes/float(UserForDelay.NumberOfSuccessfullyTransmittedMessages)

    SimRun()


