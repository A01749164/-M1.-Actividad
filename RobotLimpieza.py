from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.batchrunner import BatchRunner

class CeldasBasura(Agent): 
    """
    Clase que representa la basura dentro de una celda
    """
    def _init_(self, unique_id, model):
        super()._init_(unique_id, model)
        
class RobotLimpiador(Agent):
    """
    Clase que representa a una aspiradora.
    Su inicializador recibe una id única: unique_id, y el modelo al que pertenece
    """
    # Número de pasos realizados
    PasosRobot = 0
    
    # Constructor
    def _init_(self, unique_id, model): 
        super()._init_(unique_id, model)
    
    def move(self): 
        """
        Función que representa un movimiento de la aspiradora.
        Elige una posición vecina de manera aleatoria y mueve al agente.
        """
        
        # Se buscan las celdas vecinas a las que se puede mover el agente
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        
        # Se escoge una celda de manera aleatoria
        new_position = self.random.choice(possible_steps)
        
        # Se mueve al agente a dicha celda
        self.model.grid.move_agent(self, new_position)

    def clean(self, agent): 
        """
        Función que permite eliminar basura de una celda sucia
        """
        self.model.grid.remove_agent(agent)
        self.model.cleanCells += 1

    def step(self): 
        """
        Función que modela el comportamiento de una aspiradora en cada paso
        del modelo. Debe limpiar una celda, o moverse.
        """
        # Se obtienen todos los agentes en la celda donde está la aspiradora
        gridContent = self.model.grid.get_cell_list_contents([self.pos])
        trash = False
        trashElement = None
        
        # Se busca basura en la celda
        for element in gridContent:
            if isinstance(element, CeldasBasura):
                trash = True
                trashElement = element
        # Si no se encuentra basura mover al agente
        if not trash:
            RobotLimpiador.PasosRobot += 1
            self.move()
        # Si se encuentra basura, eliminarla
        else:
            self.clean(trashElement)

class RobotModel(Model): 
    """
    Modelo que representa la simulación
    Recibe el número de agentes: numAgents, las dimensiones de la cuadrícula: m y n,
    el porcentaje de celdas sucias: celdasbasura y el tiempo límite de la simulación: timeEjecucion
    
    """
    def _init_(self, numAgents, m, n, celdasbasura, timeEjecucion):
        # Crear cuadrícula
        self.grid = MultiGrid(m, n, False)
        # Establecer el número de agentes
        self.numAgents = numAgents
        # Tiempo límite
        self.tle = timeEjecucion
        # Número de pasos transcurridos
        self.stepsTime = 0
        # Número de celdas sucias
        self.dirtyCells = int((celdasbasura * (n*m)) / 100)
        # Número de celdas que han sido limpiadas
        self.cleanCells = 0
        # Schedule
        self.schedule = RandomActivation(self)
        # Estado de la simulación
        self.running = True
        # Bool que representa si ya se terminó de limpiar toda la basura
        self.cleanLimit = False
        
        # Creación de agentes aspiradoras
        for i in range(0,self.numAgents):
            # Crear agente y agregarlo al schedule
            a = RobotLimpiador(i, self)
            self.schedule.add(a)
            
            # Colocar al agente en la posición (1,1)
            self.grid.place_agent(a, (1, 1))

        
        # Creación de celdas sucias por medio de un set
        dirtyCells = set()
        for t in range(self.numAgents+1,self.dirtyCells+self.numAgents+1):
            # Crear agente basura y agregarlo al schedule
            b = CeldasBasura(t,self)
            self.schedule.add(b)
            RobotLimpiador.PasosRobot = 0
            # Establecer coordenadas aleatorias para la basura
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            
            # Evitar poner doble basura en una misma celda
            while (x,y) in dirtyCells:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
            dirtyCells.add((x,y))
                        
            # Colocar el agente en su posición
            self.grid.place_agent(b, (x, y))


    def step(self): 
        """
        Representación de cada paso de la simulación
        """
        # Determinar si ya se limpiaron todas las celdas
        if(self.cleanCells == self.dirtyCells):
            self.cleanLimit = True

        # Imprimir la información solicitada sobre la corrida del modelo
        if(self.cleanLimit or self.tle == self.stepsTime):
                self.running = False

                if(self.cleanLimit):
                    print("\nTodas las celdas están limpias \n")
                else:
                    print("Se ha agotado el tiempo límite")

                print("Tiempo transcurrido: " + str(self.stepsTime) + " steps, Porcentaje de celdas limpiadas: " + str(int((self.cleanCells*100)/self.dirtyCells))+ "%")
                print("Número de movimientos: " + str(RobotLimpiador.PasosRobot))
        # Hacer que todos los agentes den un paso (determinado en sus respectivos modelos)
        else:
            self.stepsTime += 1
            self.schedule.step()

