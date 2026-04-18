import sys
import os

# Adds the current directory to the path so it can see the 'ext' folder
sys.path.append(os.getcwd())

# Import using underscores to match the renamed folder
from ext.quantum_omni_tool.quantum.omni.tool.logic import QuantumTool

# 1. Initialize
my_tool = QuantumTool(stage_path="extension_output.usda")

# 2. Run
print("✅ Extension logic loaded successfully!")
print("Step 1: " + my_tool.generate_grid(count=10))

# 3. Measurement
stats = my_tool.run_measurement()

print("\n--- EXTENSION TEST REPORT ---")
print(f"Alpha (Green): {stats['Alpha']}")
print(f"Beta (Red):    {stats['Beta']}")