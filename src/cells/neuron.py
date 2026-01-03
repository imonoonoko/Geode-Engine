import src.dna.config as config
# Phase 6.5: Import config from DNA
try:
    import src.dna.config as config
except ImportError:
    import config # Fallback for legacy

class Neuron:
    def __init__(self, name, is_sensor=False):
        self.name = name
        self.potential = 0.0
        self.connections = {} 
        self.last_fired = 0
        self.is_sensor = is_sensor

    def connect(self, other, weight=0.5):
        if other != self and other not in self.connections:
            self.connections[other] = weight

    def decay(self, hormone_bias=1.0):
        factor = 0.8 if self.is_sensor else (config.HORMONE_DECAY * hormone_bias)
        self.potential *= factor
        
        # 弱い結合の除去 (忘却)
        to_remove = [n for n, w in self.connections.items() if w < 0.1]
        for n in to_remove:
            del self.connections[n]
        
        # 結合減衰
        for n in self.connections:
            self.connections[n] *= 0.9995

    def fire(self, current_time):
        self.potential = 0.0
        self.last_fired = current_time
        fired_neighbors = []
        
        for neighbor, weight in self.connections.items():
            neighbor.potential += weight * 0.8
            fired_neighbors.append(neighbor)
            
            # ヘッブ則 (Hebbian Learning)
            if current_time - neighbor.last_fired < 2.0:
                self.connections[neighbor] = min(2.5, weight + 0.2)
                if self not in neighbor.connections:
                    neighbor.connect(self, weight * 0.5)
                else:
                    neighbor.connections[self] = min(2.5, neighbor.connections[self] + 0.2)
        return fired_neighbors
