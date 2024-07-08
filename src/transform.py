import numpy as np

x_gazebo = np.array([2299.9999402931635,2300.1411661599063,2300.178042821874,2339.0378438683088,2301.4102992746816,2025.350723214387,1991.5144448360531])
y_gazebo = np.array([2299.9999999985807,2300.120914251787,2299.8624143754605,2286.559207721772,2228.9848491101147,1971.5367381223903,1939.5703807276745])
z_gazebo = np.array([4.3936147953659,10.504399331753971,27.95453404659851,30.723630467623238,26.680672341620454,28.774208758738727,29.41421463327982])

x_mavros = np.array([0.012230783700942993,0.12839627265930176,0.1933876872062683,38.54129409790039,2.1222853660583496,-275.2359313964844,-309.183349609375])
y_mavros = np.array([-0.004323312547057867,0.1017577201128006,-0.12260359525680542,-12.456621170043945,-70.51370239257812,-328.9762268066406,-361.0201416015625])
z_mavros = np.array([-0.15614479780197144,5.9079437255859375,23.375694274902344,26.33776092529297,22.084075927734375,24.332590103149414,24.928218841552734])

dx = x_gazebo - x_mavros
dy = y_gazebo - y_mavros
dz = z_gazebo - z_mavros

print("dx\n",dx)
print("dy\n",dy)
print("dz\n",dz)

print("dx mean:",np.mean(dx))
print("dy mean:",np.mean(dy))
print("dz mean:",np.mean(dz))
