import math
import csv
import os
from pxr import Usd, UsdGeom, Gf
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

class QuantumOmniTool:
    def __init__(self, stage_path="quantum_sim.usda"):
        if os.path.exists(stage_path):
            self.stage = Usd.Stage.Open(stage_path)
        else:
            self.stage = Usd.Stage.CreateNew(stage_path)
            
        UsdGeom.SetStageUpAxis(self.stage, UsdGeom.Tokens.y)
        self.qubit_data = []
        self.simulator = AerSimulator()

    def _get_quantum_decision(self, stress_factor, shielding_factor=0.0):
        qc = QuantumCircuit(1, 1)
        qc.h(0) 
        effective_stress = stress_factor * (1.0 - shielding_factor)
        theta = effective_stress * math.pi
        qc.ry(theta, 0)
        qc.measure(0, 0)
        
        result = self.simulator.run(qc, shots=1, memory=True).result()
        measurement = result.get_memory()[0]
        return "Beta" if measurement == "1" else "Alpha"

    def generate_grid(self, count=10, spacing=2.0):
        self.qubit_data = []
        for i in range(count):
            for j in range(count):
                path = f"/World/Qubit_{i}_{j}"
                
                # Use GetPrimAtPath (Capital A)
                prim = self.stage.GetPrimAtPath(path)
                if prim.IsValid():
                    cube = UsdGeom.Cube.Get(self.stage, path)
                else:
                    cube = UsdGeom.Cube.Define(self.stage, path)
                
                height = 5.0 + (i * 2.0) 
                pos = Gf.Vec3f(i * spacing, height, j * spacing)
                
                # --- SAFE UPDATE LOGIC ---
                xformable = UsdGeom.Xformable(cube)
                # Check if we already have translation ops
                ops = xformable.GetOrderedXformOps()
                if not ops:
                    xformable.AddTranslateOp().Set(pos)
                else:
                    # Update the existing operation instead of adding a new one
                    ops[0].Set(pos)
                # -------------------------
                
                self.qubit_data.append({
                    "id": f"{i}_{j}", 
                    "height": height, 
                    "path": path
                })
        
        self.stage.Save()

    def run_simulation(self, shielding=0.0, log_file="results.csv"):
        if not self.qubit_data:
            # Fallback in case generate_grid wasn't called in this session
            return {"Alpha": 0, "Beta": 0}

        max_h = max(d["height"] for d in self.qubit_data)
        stats = {"Alpha": 0, "Beta": 0}
        
        with open(log_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Qubit_ID", "Fall_Height", "Resulting_State"])
            
            for data in self.qubit_data:
                stress = (data["height"] - 5.0) / (max_h - 5.0) if max_h > 5.0 else 0
                state = self._get_quantum_decision(stress, shielding)
                stats[state] += 1
                
                cube_prim = UsdGeom.Cube.Get(self.stage, data["path"])
                color = Gf.Vec3f(0.1, 0.8, 0.2) if state == "Alpha" else Gf.Vec3f(0.8, 0.1, 0.1)
                cube_prim.GetDisplayColorAttr().Set([color])
                
                writer.writerow([data["id"], round(data["height"], 2), state])
        
        self.stage.Save()
        return stats