from RobotLimpieza import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

# Visualización gráfica de los agentes
def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r":0.6}

    # Distinción entre agente Aspiradora y Basura
    if isinstance(agent, RobotLimpiador):
        portrayal["Color"] = "green"
        portrayal["Layer"] = 0.7
    else:
        portrayal["Color"] = "brown"
        portrayal["Layer"] = 0.5
        portrayal["r"] = 0.2
    return portrayal

# Datos de simulación
n = 15                  # Ancho
m = 15                  # Alto
numAgents = 3           # Aspiradoras
celdasbasura = 40       # Cantidad de basura
timeEjecucion = 200     # Tiempo


# Crear instancia del servidor con el modelo
grid = CanvasGrid(agent_portrayal, n, m, 750, 750)
server = ModularServer(RobotModel,
                       [grid],
                       "Robot de Limpieza Reactivo",
                       {"n": n,
                        "m": m,
                        "numAgents": numAgents,
                        "celdasbasura": celdasbasura,
                        "timeEjecucion": timeEjecucion})
server.port = 8521 # Puerto default
server.launch()