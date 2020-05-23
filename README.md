# Ballistic projectile simulation

Simulates flight of ballistic projectile over the Earth. Outputs a CSV file
containing data about the flight (see `projectile.data.DataPoints.ProjectileDataPoint`).
Optionally, outputs a CSV file containing data about each force acting upon
the projectile during the flight. Output files are located inside `scenario_data`
directory in the woking directory.

## Prerequisites
- Python 3.7 or newer
- numpy
- matplotlib
- joblib

## Examples
Launch a test scenario:
```shell script
python3 projectile/main.py run test
```
Launch a vary_yaw scenario on all processors (cores):
```shell script
python3 projectile/main.py run vary_yaw
```
Launch a vary_yaw scenario using at most 7 processes:
```shell script
python3 projectile/main.py run vary_yaw 7
```
Plot forces using data file generated after running vary_yaw scenario:
```shell script
python3 projectile/main.py plot scenario_data/ld_vary_yaw/forces/0.csv
```