import wntr.network.options
import wntr
import tsnet

# Création d'un réseau vide
wn = wntr.network.WaterNetworkModel()
wn.options.hydraulic.inpfile_units = 'LPS'
wn.options.hydraulic.headloss = 'D-W'

# Ajout des composants
wn.add_reservoir('Water_Castle', base_head=100 )

wn.add_junction('j1', elevation=20)
wn.add_junction('END1', elevation=20, base_demand=0.0001) # 0.1 LPS
wn.add_junction('j2', elevation=20)
wn.add_junction('END2', elevation=20, base_demand=0.0001)
wn.add_junction('j3', elevation=20)
wn.add_junction('END3', elevation=20, base_demand=0.0001)
wn.add_junction('j4', elevation=20)
wn.add_junction('j5', elevation=20)
wn.add_junction('j6', elevation=20)
wn.add_junction('END_URGENCE', elevation=20, base_demand=0.01) # 10 LPS
wn.add_junction('END_Immeuble', elevation=70, base_demand=0.001) # 1 LPS

# Nœuds intermédiaires pour isoler les vannes du T-junction (exigence de topologie TSNet)
wn.add_junction('jv1', elevation=20)
wn.add_junction('jv2', elevation=20)
wn.add_junction('jv3', elevation=20)
wn.add_junction('jv4', elevation=20)
wn.add_junction('jv5', elevation=70)

# Réseau principal
wn.add_pipe('p1','Water_Castle','j1', length=130, diameter=1.2, roughness=0.01, minor_loss=0, initial_status='OPEN')
wn.add_pipe('p2','j1','j2', length=10, diameter=0.6, roughness=0.01, minor_loss=0, initial_status='OPEN')
wn.add_pipe('p3','j2','j3', length=20, diameter=0.6, roughness=0.01, minor_loss=0, initial_status='OPEN')
wn.add_pipe('p4','j3','j4', length=40, diameter=0.6, roughness=0.01, minor_loss=0, initial_status='OPEN')
wn.add_pipe('p5','j5','j6', length=5, diameter=0.6, roughness=0.01, minor_loss=0, initial_status='OPEN')

# Mini-tuyaux "raccords" (~1m) pour la séparation
wn.add_pipe('stub1','j1','jv1', length=1, diameter=0.158, roughness=0.01, minor_loss=0, initial_status='OPEN')
wn.add_pipe('stub2','j2','jv2', length=1, diameter=0.158, roughness=0.01, minor_loss=0, initial_status='OPEN')
wn.add_pipe('stub3','j3','jv3', length=1, diameter=0.158, roughness=0.01, minor_loss=0, initial_status='OPEN')
wn.add_pipe('stub4','j6','jv4', length=1, diameter=0.158, roughness=0.01, minor_loss=0, initial_status='OPEN')
wn.add_pipe('stub5','j6','jv5', length=1, diameter=0.158, roughness=0.01, minor_loss=0, initial_status='OPEN')

# Vannes branchées sur les stubs
wn.add_valve('v1','jv1','END1', diameter=0.158, valve_type='PRV', minor_loss=0, initial_setting=100000, initial_status='ACTIVE')
wn.add_valve('v2','jv2','END2', diameter=0.158, valve_type='PRV', minor_loss=0, initial_setting=100000, initial_status='ACTIVE')
wn.add_valve('v3','jv3','END3', diameter=0.158, valve_type='PRV', minor_loss=0, initial_setting=100000, initial_status='ACTIVE')
wn.add_valve('v4','jv4','END_URGENCE', diameter=0.158, valve_type='PRV', minor_loss=0, initial_setting=100000, initial_status='CLOSED')
wn.add_valve('v5','jv5','END_Immeuble', diameter=0.158, valve_type='PRV', minor_loss=0, initial_setting=100000, initial_status='ACTIVE')

debit_voulu = 0.200 # m3/s (200 LPS)
charge_voulue = 100 # m (Mètres de colonne d'eau)
wn.add_curve('courbe_pompe', 'HEAD', [(debit_voulu, charge_voulue)])
wn.add_pump('pump', 'j4', 'j5', pump_type='HEAD', pump_parameter='courbe_pompe')
wntr.network.write_inpfile(wn, 'mon_reseau.inp') # Enregistre en fichier INP

tm = tsnet.network.TransientModel('mon_reseau.inp') # Charge sur TSNet

tm.set_wavespeed(1200.)

dt = 0.0004
tf = 20   # simulation period [s]
tm.set_time(tf,dt)

# Initialize steady state simulation
t0 = 0. # initialize the simulation at 0 [s]
engine = 'DD' # demand driven simulator
tm = tsnet.simulation.Initializer(tm, t0, engine)

# Transient simulation
results_obj = 'Test1' # name of the object for saving simulation results
tm1 = tsnet.simulation.MOCSimulator(tm, results_obj)

# report results
import matplotlib.pyplot as plt
node = 'j6'
node = tm.get_node(node)
fig1 = plt.figure(figsize=(10,4), dpi=80, facecolor='w', edgecolor='k')
plt.plot(tm.simulation_timestamps, (node.head - node.elevation) * 9810)
plt.xlim([tm.simulation_timestamps[0],tm.simulation_timestamps[-1]])
plt.title('Pression entre Pompe et Immeuble %s '%node)
plt.xlabel("Time [s]")
plt.ylabel("Pression [Pa]")
plt.legend(loc='best')
plt.grid(True)
plt.show()

pipe = 'p1'
pipe = tm.get_link(pipe)
fig = plt.figure(figsize=(10,4), dpi=80, facecolor='w', edgecolor='k')
plt.plot(tm.simulation_timestamps,pipe.start_node_flowrate,label='Start Node')
plt.plot(tm.simulation_timestamps,pipe.end_node_flowrate,label='End Node')
plt.xlim([tm.simulation_timestamps[0],tm.simulation_timestamps[-1]])
plt.title('Velocity of Pipe %s '%pipe)
plt.xlabel("Time [s]")
plt.ylabel("Velocity [m/s]")
plt.legend(loc='best')
plt.grid(True)
plt.show()
# fig1.savefig('./docs/figures/tnet1_node.png', format='png',dpi=100)

pipe = 'p5'
pipe = tm.get_link(pipe)
fig = plt.figure(figsize=(10,4), dpi=80, facecolor='w', edgecolor='k')
plt.plot(tm.simulation_timestamps,pipe.start_node_flowrate,label='Start Node')
plt.plot(tm.simulation_timestamps,pipe.end_node_flowrate,label='End Node')
plt.xlim([tm.simulation_timestamps[0],tm.simulation_timestamps[-1]])
plt.title('Velocity of Pipe %s '%pipe)
plt.xlabel("Time [s]")
plt.ylabel("Velocity [m/s]")
plt.legend(loc='best')
plt.grid(True)
plt.show()
