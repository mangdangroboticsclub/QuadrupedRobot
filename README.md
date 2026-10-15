<p align="center">
  <img src="docs/images/cover.jpg" alt="Mini Pupper 4" width="820">
</p>

<h1 align="center">Mini Pupper 4</h1>

<p align="center">
  <em>From Learning to Earning — Powered by 3-DoF Coreless Smart Servos.</em>
</p>

<p align="center">
  <a href="https://mangdang.org"><b>Official Website</b></a> ·
  <a href="https://www.facebook.com/groups/519009562699751">Facebook Group</a> ·
  <a href="https://discord.gg/xJdt3dHBVw">Discord Community</a> ·
  <a href="https://mangdang.store/collections/shop">Online Shop</a> ·
  <a href="CONTRIBUTING.md">Contributing Guide</a>
</p>

---

## Capabilities & Frameworks

<table>
<tr>
<td width="50%">
  <img src="docs/images/Mujoko.gif" alt="MuJoCo Simulation" width="410">
</td>
<td width="50%">
  <img src="docs/images/BAM.gif" alt="BAM Actuator Mechanics" width="410">
</td>
</tr>
  
<tr>
<td><b>Close the Sim2Real Gap.</b> Train complex neural network policies flawlessly in high-fidelity simulation, and deploy straight to the real physical robot.</td>
<td><b>Native BAM Integration.</b> Fully compatible with Better Actuator Models (BAM) to capture precise joint friction physics, letting you focus on your advanced applications.</td>
</tr>

<tr>
<td width="50%">
  <img src="docs/images/BAM.gif" alt="micro-ROS Support" width="410">
</td>
<td width="50%">
  <img src="docs/images/ROS.gif" alt="ROS 2 Jazzy Autonomous Navigation" width="410">
</td>
</tr>

<tr>
<td><b>Low-Level micro-ROS.</b> Native support for micro-ROS pipelines directly on the microcontroller for reliable, real-time actuator control.</td>
<td><b>Next-Gen ROS 2 Jazzy.</b> Ready-to-run out-of-the-box templates for advanced SLAM mapping, path planning, and autonomous Nav2 stacks.</td>
</tr>
</table>

All capabilities stem from our proprietary high-performance, **3-DoF coreless smart servo joints** — the ultimate, versatile building block for modern open-source robotics.

<p align="center">
  <img width="680" alt="MD-300C-150 Smart Servo Architecture" src="https://github.com/user-attachments/assets/df96e932-38e8-4ce4-802b-bc2e8bd37f65" />
</p>

## Ecosystem Roadmap

| Component / Repo | Description & Source Code Directory |
|---|---|
| [🤖 Reinforcement Learning](https://github.com) | The physics engine backend: MuJoCo environments, PPO pipelines, domain randomization, and the baked-in ONNX export runtime. |
| [⚙️ BAM Friction Engine](https://github.com/mangdangroboticsclub/bam) | Hardware actuator physics repository. The MangDang MD-300C-150 servo is fully benchmarked and adapted to BAM. |
| [🛹 ROS 2 Core Stack](https://github.com/mangdangroboticsclub/mini_pupper_ros) | Our main software platform. We strictly follow the official Open Robotics roadmap with stable support up to ROS 2 Jazzy. |
| [📡 micro-ROS Stack](https://github.com/mangdangroboticsclub/mini_pupper_ros) | Real-time lower-level agent bridging. Actuator DDS communications introduced natively from Mini Pupper 4. |
| [🧠 Mini Pupper 4 - MCU Brain](https://github.com/mangdangroboticsclub/minipupper-4-mcu) | Complete firmware layer source code for the onboard microcontroller, including embedded local AI routing. |
| [🍓 Mini Pupper 4 - Pi Brain](https://github.com/mangdangroboticsclub/minipupper-4-mcu) | High-level application space source code tailored for the Raspberry Pi computing chassis. |
| [🤝 CONTRIBUTING.md](CONTRIBUTING.md) | Developer guidelines for compiling, local simulation testing, layout conventions, and code submission rules. |
| [📖 Online Manual & FAQ](https://minipupperdocs.readthedocs.io/en/latest/index.html) | Comprehensive documentation hub, including modular mechanical blueprints, PCB schematics, and open research challenges. |
