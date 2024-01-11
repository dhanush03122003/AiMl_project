import random

class GeneticAlgorithm:
    def _init_(self, population_size, p_crossover, p_mutation, max_generations, hof_size):
        self.POPULATION_SIZE = population_size
        self.P_CROSSOVER = p_crossover
        self.P_MUTATION = p_mutation
        self.MAX_GENERATIONS = max_generations
        self.HOF_SIZE = hof_size
        self.start_state = start_state
        self.end_state = end_state
        self.servers, self.cache = {}, {}
        self.all_operations = []

    def initialize_population(self):
        return [self.random_path() for _ in range(self.POPULATION_SIZE)]

    def random_path(self):
        path = [self.start_state]
        current_state = self.start_state
        while current_state != self.end_state:
            next_state = random.choice(list(self.servers[current_state]))
            path.append(next_state)
            current_state = next_state
        return path

    def fitness(self, path):
        return 1 / len(path)

    def select_path(self, population):
        total_fitness = sum(self.fitness(path) for path in population)
        r = random.uniform(0, total_fitness)
        upto = 0
        for path in population:
            if upto + self.fitness(path) >= r:
                return path
            upto += self.fitness(path)
   

    def crossover(self, path1, path2):
        return path1[:path1.index(self.end_state)+1] + path2[path2.index(self.end_state)+1:]

    def mutate(self, path):
        i = random.randint(1, len(path) - 2)
        j = random.randint(1, len(path) - 2)
        path[i], path[j] = path[j], path[i]
        return path

    def run_genetic_algorithm(self, sen_den):
        self.start_state = sen_den[0]
        self.end_state = sen_den[1]
        self.population = self.initialize_population()  # Use instance variable

        for generation in range(self.MAX_GENERATIONS):
            self.population.sort(key=self.fitness, reverse=True)
            if self.population[0] == self.end_state:
                return self.population[0]
            self.population = self.population[:self.HOF_SIZE]
            while len(self.population) < self.POPULATION_SIZE:
                parent1 = self.select_path(self.population)
                parent2 = self.select_path(self.population)
                child = self.crossover(parent1, parent2)
                if random.random() < self.P_MUTATION:
                    child = self.mutate(child)
                self.population.append(child)
        return self.population[0]

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
    def breakLink(self, nodes):
      if nodes[1] in self.servers[nodes[0]]:
          self.servers[nodes[0]].remove(nodes[1])
        
      # Create a set to keep track of paths that need re-initialization
      paths_to_reinitialize = set()

      for i in range(len(self.population)):
          path = self.population[i]
          if nodes[1] in path:
              index = path.index(nodes[1])
              self.population[i] = path[:index]
              paths_to_reinitialize.add(i)

      # Re-initialize the remaining part of the paths only once
      for i in range(len(self.population)):
          if i not in paths_to_reinitialize:
              self.population[i].extend(self.initialize_population()[0][:self.POPULATION_SIZE - len(self.population[i])])



    def addLink(self, nodes):
        if nodes[1] not in self.servers[nodes[0]]:
            self.servers[nodes[0]].append(nodes[1])


    def askPath(self):
        with open('operation-info.txt', 'r') as operation_info:
            network = operation_info.readlines()
            for operations in network:
                self.all_operations.append(operations.split())
    def runPackets(self):
        for current_packet in self.all_operations:
            if current_packet[0] == 'Break':
                print(f"[{current_packet[1]} - {current_packet[2]}] Link is removed")
                self.breakLink(current_packet[1:])
                continue
            if current_packet[0] == 'Add':
                print(f"[{current_packet[1]} - {current_packet[2]}] Link is added")
                self.addLink(current_packet[1:])
                continue
            if current_packet[0] == 'Send':
                ph = self.run_genetic_algorithm(current_packet[1:])
                print("Shortest path from ",current_packet[1],' to ',current_packet[2] , 'is',ph)
                continue


genetic_algo = GeneticAlgorithm(50, 0.7, 0.01, 500, 10)
genetic_algo.makeGraph()
genetic_algo.askPath()
genetic_algo.runPackets()