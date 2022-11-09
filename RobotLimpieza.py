"""
Autor:
    EQUIPO 8
    Jeovani Hernandez Bastida     A01749164
    Maximiliano Carrasco Rojas    A01025261

Entrada:
    * Habitación de MxN espacios.
    * Número de agentes.
    * Porcentaje de celdas inicialmente sucias.
    * Tiempo máximo de ejecución (steps).
Salida:
    * Tiempo necesario hasta que todas las celdas estén limpias (o se haya llegado al tiempo máximo).
    * Porcentaje de celdas limpias después del termino de la simulación.
    * Número de movimientos realizados por todos los agentes.
"""

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
    def __init__(self, unique_id, model): 
        super().__init__(unique_id, model)
    
    def moveAgent(self): 
        """
        Función que representa un movimiento de la aspiradora.
        Elige una posición vecina de manera aleatoria y mueve al agente.
        """
        
        # Se buscan las celdas vecinas a las que se puede mover el agente
        posiblespasos = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        
        # Se escoge una celda de manera aleatoria
        nuevaposicion = self.random.choice(posiblespasos)
        
        # Se mueve al agente a dicha celda
        self.model.grid.move_agent(self, nuevaposicion)

    def limpiar(self, agent): 
        """
        Función que permite eliminar basura de una celda sucia
        """
        self.model.grid.remove_agent(agent)
        self.model.celdasLimpias += 1

    def step(self): 
        """
        Función que modela el comportamiento de una aspiradora en cada paso
        del modelo. Debe limpiar una celda o moverse.
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
        # Si no se encuentra basura, se mueve al agente
        if not trash:
            RobotLimpiador.PasosRobot += 1
            self.moveAgent()
        # Si se encuentra basura, se elimina 
        else:
            self.limpiar(trashElement)

class RobotModel(Model): 
    """
    Modelo que representa la simulación.
    Recibe el número de agentes: numAgents, las dimensiones de la cuadrícula: m y n,
    el porcentaje de celdas sucias: celdasbasura y el tiempo límite de la simulación: timeEjecucion
    """
    def __init__(self, numAgents, m, n, celdasbasura, timeEjecucion):
        self.grid = MultiGrid(m, n, False)                          # Crear cuadrícula
        self.numAgents = numAgents                                  # Establecer el número de agentes
        self.time = timeEjecucion                                   # Tiempo límite 
        self.pasoscursados = 0                                      # Número de pasos transcurridos
        self.celdasSucias = int((celdasbasura * (n*m)) / 100)       # Número de celdas sucias
        self.celdasLimpias = 0                                      # Número de celdas que han sido limpiadas
        self.schedule = RandomActivation(self)                      # Schedule
        self.running = True                                         # Estado de la simulación
        self.limpiezalimite = False                                 # Booleano que representa si ya se terminó de limpiar toda la basura
        
        # Creación de los agentes aspiradoras
        for i in range(0,self.numAgents):
            # Crear agente y agregarlo al schedule
            a = RobotLimpiador(i, self)
            self.schedule.add(a)
            
            # Colocar al agente en la posición (1,1) de la cuadricula en la parte inferior izquierda
            self.grid.place_agent(a, (1, 1))

        # Creación de celdas sucias por medio de un set
        celdasSucias = set()
        for t in range(self.numAgents+1,self.celdasSucias+self.numAgents+1):
            # Crear agente basura y agregarlo al schedule
            b = CeldasBasura(t,self)
            self.schedule.add(b)
            RobotLimpiador.PasosRobot = 0

            # Establecer coordenadas aleatorias para la basura
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            
            # Evitar poner doble basura en una misma celda
            while (x,y) in celdasSucias:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
            celdasSucias.add((x,y))
                        
            # Colocar al agente en su posición
            self.grid.place_agent(b, (x, y))

    def step(self): 
        """
        Representación de cada paso de la simulación
        """
        # Determinar si ya se limpiaron todas las celdas
        if(self.celdasLimpias == self.celdasSucias):
            self.limpiezalimite = True

        # Imprimir la información solicitada sobre la corrida del modelo
        if(self.limpiezalimite or self.time == self.pasoscursados):
                self.running = False

                if(self.limpiezalimite):
                    print("\nTodas las celdas están limpias \n")
                else:
                    print("Se ha agotado el tiempo límite")

                print("Tiempo transcurrido: " + str(self.pasoscursados) + 
                " steps, Porcentaje de celdas limpiadas: " + 
                str(int((self.celdasLimpias*100)/self.celdasSucias)) + "%")
                print("Número de movimientos: " + str(RobotLimpiador.PasosRobot))

        # Hacer que todos los agentes den un paso (determinado en sus respectivos modelos)
        else:
            self.pasoscursados += 1
            self.schedule.step()








