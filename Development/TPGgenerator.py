import numpy as np

class NTPG:
    def __init__(self, N):
        self._ntpg = {}
        self._htpg = {}
        self._N = N  

class HTPG:
    def __init__(self, N):
        self._ntpg = {}
        self._htpg = {}
        self._N = N

ntpg = {}
htpg = {}

N = 10

for i in range(N):
    ip = f"192.168.0.{i + 1}"
    ntpg[ip] = []
    htpg[ip] = {}

    num_edges = np.random.randint(0, N)
    dest_nodes = np.random.choice(N, size=num_edges, replace=False)

    for j in dest_nodes:
        up = np.random.uniform(0, 1)
        rp = np.random.uniform(0, 1)
        dest_ip = f"192.168.0.{j + 1}"
        ntpg[ip].append((dest_ip, up, rp))

        # Create corresponding HTPG edges
        htpg[ip][dest_ip] = []
        num_htpg_edges = np.random.randint(0, N)
        dest_tuples = np.random.choice(N * 2, size=num_htpg_edges, replace=False)
        for l in dest_tuples:
            dest_host = l // 2 + 1
            dest_host_ip = f"192.168.0.{dest_host}"
            dest_privilege = ["User", "Root"][l % 2]
            service = f"Service{chr(ord('A') + l)}"
            vulnerability = f"Vul{service}{l + 1}"
            probability = np.random.uniform(0, 1)
            htpg[ip][dest_ip].append((service, vulnerability, probability, (dest_host_ip, dest_privilege)))


print("NTPG:", ntpg)
print("HTPG:", htpg)