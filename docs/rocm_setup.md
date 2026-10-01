# Guía de instalación ROCm + vLLM en Droplet AMD

**Protocolo:** WIPO / NNN / NDA
**Titular:** EinsRos Global Cortex Ultd — F1725 Development Technologies

---

## 1. Prerequisitos

- Droplet AMD Instinct MI300X (DigitalOcean o AMD Developer Cloud)
- Ubuntu 22.04 LTS
- Python 3.10+
- Mínimo 100 GB de disco

---

## 2. Instalación de ROCm

```bash
# Agregar repositorio de AMD
wget https://repo.radeon.com/amdgpu-install/6.1/ubuntu/jammy/amdgpu-install_6.1.60100-1_all.deb
sudo apt install ./amdgpu-install_6.1.60100-1_all.deb

# Instalar ROCm
sudo amdgpu-install --usecase=rocm

# Verificar
rocm-smi
rocminfo | grep gfx