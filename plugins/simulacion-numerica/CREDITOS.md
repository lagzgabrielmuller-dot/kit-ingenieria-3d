# Créditos: Simulación numérica

Las partes de métodos numéricos, flujo de simulación, verificación y diagnóstico del paquete *materials-simulation-skills*, con su estructura de carpetas original. No se copiaron las de ontologías de materiales, HPC (SLURM) ni empaquetado FAIR.

Skills escritas por otras personas y copiadas **sin modificaciones** desde sus repos, con permiso de sus licencias. Las licencias completas están en `licencias/`.

| Autor y repo | Licencia | Commit copiado |
|---|---|---|
| heshamfs, [heshamfs/materials-simulation-skills](https://github.com/heshamfs/materials-simulation-skills) | Apache-2.0 | `775055956bb8fa3838032c49a346e26d94d0d1f6` |

## Skills (17)

| Skill | Para qué sirve (descripción original) |
|---|---|
| `convergence-study` | Perform spatial and temporal convergence analysis for solution verification — compute observed convergence orders from grid or timestep refinement studies, apply… |
| `differentiation-schemes` | Select and apply numerical differentiation schemes for PDE and ODE discretization — generate finite-difference stencils at arbitrary order and accuracy, choose… |
| `linear-solvers` | Select and configure linear solvers for Ax=b systems arising in numerical simulations — choose between direct (LU, Cholesky) and iterative (CG, GMRES, BiCGSTAB,… |
| `mesh-generation` | Plan and evaluate mesh generation for numerical simulations — estimate grid resolution from physics scales (interface width, boundary layers, wavelengths), check… |
| `nonlinear-solvers` | Select and configure nonlinear solvers for root-finding f(x)=0, optimization min F(x), and least-squares problems — choose among Newton, Newton-Krylov, quasi-Newton… |
| `numerical-integration` | Select and configure time integration methods for ODE and PDE simulations — choose among explicit Runge-Kutta, BDF, Rosenbrock, and Adams families, set relative and… |
| `numerical-stability` | Analyze numerical stability for time-dependent PDE simulations — check CFL and Fourier criteria, perform von Neumann stability analysis, detect stiffness, evaluate… |
| `time-stepping` | Plan and control time-step policies for transient simulations — couple CFL and physics-based stability limits with adaptive stepping, ramp initial transients through… |
| `simulation-failure-triage` | First-response triage for cross-code (LAMMPS/VASP/QE/MOOSE) simulation failures: classifies the failure signature (nonconvergence, NaN/Inf, exploding energy, unstable… |
| `md-analysis-planner` | Plan molecular dynamics post-processing for materials simulations, including RDF, MSD and diffusion, VACF/VDOS, coordination numbers, bond-angle distributions,… |
| `parameter-optimization` | Explore and optimize simulation parameters via design of experiments (DOE), sensitivity analysis, and optimizer selection — generate Latin Hypercube, quasi-random, or… |
| `performance-profiling` | Identify computational bottlenecks, analyze parallel scaling, estimate memory requirements, and generate optimization recommendations for materials simulations —… |
| `post-processing` | Extract, analyze, and summarize simulation output data — pull spatial fields at specific timesteps, compute time-series trends and detect steady state, extract line… |
| `simulation-orchestrator` | Orchestrate multi-simulation campaigns — generate parameter sweep configurations (grid, linspace, or Latin Hypercube sampling), initialize and track batch job… |
| `simulation-validator` | Validate simulations across three stages — run pre-flight checks on configuration files (parameter ranges, required fields, disk space), monitor runtime logs for… |
| `workflow-engine-mapper` | Map computational materials tasks onto workflow engines such as atomate2, jobflow, AiiDA, pyiron, or a simple one-off script. Use when deciding how to structure a… |
| `benchmark-and-mms-planner` | Plan verification and validation campaigns for simulation codes using manufactured solutions, canonical benchmark problems, grid/time refinement, uncertainty… |

## Qué necesitan

- Python 3.10+ con numpy y scipy (cada skill trae sus scripts en `scripts/` y explica qué necesita).

## Revisión

Antes de copiarlas revisé licencia, estructura, scripts, llamadas de red, binarios, hooks y frases que intenten darle órdenes ocultas a Claude, sin encontrar problemas. Los scripts no se ejecutaron durante la revisión. Si un autor publica una versión nueva, se puede volver a copiar y actualizar el commit de la tabla. Los scripts procesan archivos locales sin `eval` ni red.
