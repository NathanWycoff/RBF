''' 
In this example we solve the Poisson equation over an L-shaped domain
with fixed boundary conditions. We use the RBF-FD method. The RBF-FD
method is preferable over the spectral RBF method because it is
scalable and does not require the user to specify a shape parameter
(assuming that we use odd order polyharmonic splines to generate the
weights).
'''
import numpy as np
from rbf.fd import weight_matrix, add_rows
from rbf.basis import phs3
from rbf.geometry import contains
from rbf.nodes import min_energy_nodes
import matplotlib.pyplot as plt
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve
from scipy.interpolate import LinearNDInterpolator

# Define the problem domain with line segments.
vert = np.array([[0.0, 0.0], [2.0, 0.0], [2.0, 1.0],
                 [1.0, 1.0], [1.0, 2.0], [0.0, 2.0]])
smp = np.array([[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]])

N = 500 # total number of nodes.

n = 20 # stencil size. Increase this will generally improve accuracy

basis = phs3 # radial basis function used to compute the weights. Odd
             # order polyharmonic splines (e.g., phs3) have always
             # performed well for me and they do not require the user
             # to tune a shape parameter. Use higher order
             # polyharmonic splines for higher order PDEs.

order = 2 # Order of the added polynomials. This should be at least as
          # large as the order of the PDE being solved (2 in this
          # case). Larger values may improve accuracy

# generate nodes
nodes, groups, _ = min_energy_nodes(N, vert, smp) 

# create the "left hand side" matrix. 
# create the component which evaluates the PDE
A_interior = weight_matrix(nodes[groups['interior']], nodes,
                           diffs=[[2, 0], [0, 2]], n=n, 
                           basis=basis, order=order)
# create the component for the fixed boundary conditions
A_boundary = weight_matrix(nodes[groups['boundary:all']], nodes, 
                           diffs=[0, 0]) 
# Add the components to the corresponding rows of `A`
A = csc_matrix((N, N))
A = add_rows(A,A_interior,groups['interior'])
A = add_rows(A,A_boundary,groups['boundary:all'])
                           
# create "right hand side" vector
d = np.zeros((N,))
d[groups['interior']] = -1.0
d[groups['boundary:all']] = 0.0

# find the solution at the nodes
u_soln = spsolve(A, d) 

# interpolate the solution on a grid
xg, yg = np.meshgrid(np.linspace(-0.05, 2.05, 400), 
                     np.linspace(-0.05, 2.05, 400))
points = np.array([xg.flatten(), yg.flatten()]).T                    
u_itp = LinearNDInterpolator(nodes, u_soln)(points)
# mask points outside of the domain
u_itp[~contains(points, vert, smp)] = np.nan 
ug = u_itp.reshape((400, 400)) # fold back into a grid
# make a contour plot of the solution
fig, ax = plt.subplots()
p = ax.contourf(xg, yg, ug, np.linspace(-1e-6, 0.16, 9), cmap='viridis')
ax.plot(nodes[:, 0], nodes[:, 1], 'ko', markersize=4)
for s in smp:
  ax.plot(vert[s, 0], vert[s, 1], 'k-', lw=2)

ax.set_aspect('equal')
fig.colorbar(p, ax=ax)
fig.tight_layout()
plt.savefig('../figures/fd.i.png')
plt.show()


