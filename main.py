class PacketRoutePlanning:
    def __init__(self):
        self.servers, self.cache = {}, {}
        self.all_operations = []

    def makeGraph(self):
        with open('path-info.txt', 'r') as connections:
            paths = connections.readlines()
            for edges in paths:
                curr = edges.split()
                if curr[0] not in self.servers:
                    self.servers[curr[0]] = [curr[1]]
                    self.cache[curr[0]] = {}
                else:
                    self.servers[curr[0]].append(curr[1])

    def askPath(self):
        with open('operation-info.txt', 'r') as operation_info:
            network = operation_info.readlines()
            for operations in network:
                self.all_operations.append(operations.split())

    def isPathInCache(self, curr_operation):
        return curr_operation[1] in self.cache[curr_operation[0]]

    def updatePathInCache(self, curr_path):  # call for both curr_path and curr_path[::-1]
        for i in range(len(curr_path)):
            for j in range(i + 1, len(curr_path)):
                if not self.isPathInCache([curr_path[i], curr_path[j]]) or len(curr_path[i:j + 1]) < len(self.cache[curr_path[i]][curr_path[j]]):
                    self.cache[curr_path[i]][curr_path[j]] = curr_path[i:j + 1]

    def removePathInCache(self, nodes):
        for server in list(self.cache.keys()):
            remove = [links for links in self.cache[server] if nodes[0] in self.cache[server][links] and nodes[1] in self.cache[server][links]]
            for links in remove:
                self.cache[server].pop(links)

    def clearCache(self):
        self.cache.clear()
        for server in self.servers:
            self.cache[server] = {}

    def printPath(self, path):
        print("[ ", end="")
        for server in range(len(path)):
            if server == len(path) - 1:
                print(path[server], " ]")
                continue
            print(f"{path[server]} -> ", end="")

    def breakLink(self, nodes):
        self.removePathInCache(nodes)
        if nodes[1] in self.servers[nodes[0]]:
            self.servers[nodes[0]].remove(nodes[1])

    def addLink(self, nodes):
        if nodes[1] not in self.servers[nodes[0]]:
            self.servers[nodes[0]].append(nodes[1])

    def findShortestPath(self, start_node, end_node):
        queue = [(start_node, [])]
        visited = set()
        while queue:
            node, path = queue.pop(0)
            if node == end_node:
                return path
            visited.add(node)
            for neighbor in self.servers[node]:
                if neighbor not in visited:
                    new_path = path.copy()
                    new_path.append(neighbor)
                    queue.append((neighbor, new_path))
        return []

    def sendPacket(self, nodes):
        if self.isPathInCache(nodes):
            # print(f"Packet sent from {nodes[0]} to {nodes[1]} in path - ", self.cache[nodes[0]][nodes[1]])
            print(f"[{nodes[0]} to {nodes[1]}] cache path: ", end="")
            self.printPath(self.cache[nodes[0]][nodes[1]])
            return
        best_path = self.findShortestPath(nodes[0], nodes[1])
        if len(best_path) == 0:
            print(f"[{nodes[0]} to {nodes[1]}] Packet dropped - no path")
        else:
            best_path.insert(0, nodes[0])
            self.updatePathInCache(best_path)
            print(f"[{nodes[0]} to {nodes[1]}] calculated path: ", end="")
            self.printPath(self.cache[nodes[0]][nodes[1]])

    def runPackets(self):
        for current_packet in self.all_operations:
            if current_packet[0] == 'Break':
                print(f"[{current_packet[1]} - {current_packet[2]}] Link is removed")
                self.breakLink(current_packet[1:])
                continue
            if current_packet[0] == 'Add':
                print(f"[{current_packet[1]} - {current_packet[2]}] Link is added")
                self.addLink(current_packet[1:])
                self.clearCache()
                continue
            if current_packet[0] == 'Send':
                self.sendPacket(current_packet[1:])
                continue


if __name__ == '__main__':
    channel = PacketRoutePlanning()
    channel.makeGraph()
    channel.askPath()
    channel.runPackets()

