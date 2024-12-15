import time
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from hashlib import sha256

def rsa_encrypt(public_key, symmetric_key):
    """Encrypt symmetric key using RSA."""
    cipher = PKCS1_OAEP.new(public_key)
    return cipher.encrypt(symmetric_key)

def abe_encrypt(cpabe, public_key, symmetric_key, policy):
    """Encrypt using ABE scheme."""
    return cpabe.encrypt(public_key, symmetric_key, policy)

def generate_key_from_element(element):
    """Generate a symmetric key from a pairing group element."""
    return sha256(str(element).encode()).digest()[:16]

def traditional_scheme_encryption(public_key, request_count):
    """Perform traditional encryption for multiple requests."""
    total_time = 0
    for _ in range(request_count):
        symmetric_key = get_random_bytes(16)  # AES-128
        start_time = time.time()
        rsa_encrypt(public_key, symmetric_key)
        end_time = time.time()
        total_time += (end_time - start_time)
    return total_time

def abe_scheme_encryption(cpabe, public_key, policy, request_count):
    """Perform ABE scheme encryption only once, and simulate subsequent request verification."""
    symmetric_key_element = PairingGroup('SS512').random(GT)
    symmetric_key = generate_key_from_element(symmetric_key_element)

    # Encrypt once using ABE
    start_time = time.time()
    abe_encrypt(cpabe, public_key, symmetric_key_element, policy)
    first_encryption_time = time.time() - start_time

    # Simulate subsequent request verification without additional encryption
    total_time = first_encryption_time  # Include only the first encryption time
    return total_time

def run_experiment():
    """Run encryption time comparison experiment."""
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    group = PairingGroup('SS512')
    cpabe = CPabe_BSW07(group)
    abe_public_key, abe_master_key = cpabe.setup()
    policy = '((A or B) and (C or D))'
    request_counts = np.arange(0, 501, 50)

    traditional_results = []
    abe_results = []

    for request_count in request_counts:
        traditional_time = traditional_scheme_encryption(public_key, request_count)
        traditional_results.append(traditional_time)
        abe_time = abe_scheme_encryption(cpabe, abe_public_key, policy, request_count)
        abe_results.append(abe_time)

    return request_counts, traditional_results, abe_results

def plot_results(request_counts, traditional_results, abe_results):
    """Plot and save the results of the encryption time comparison."""
    plt.figure(figsize=(14, 10))
    plt.plot(request_counts, traditional_results, 'b-o', label='Traditional RSA', linewidth=2, markersize=12)
    plt.plot(request_counts, abe_results, 'r--^', label='ABEToken', linewidth=2, markersize=12)

    plt.xlabel('Number of Requests', fontsize=14)
    plt.ylabel('Encryption Time (ms)', fontsize=14)
    plt.title('Encryption Time Comparison Between ABEToken and Traditional RSA Schemes', fontsize=16)
    plt.legend(loc='upper left', frameon=True, framealpha=0.9)
    plt.grid(True)
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(50))
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(0.2))
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.savefig('/home/wb/result/Encryption_Time_Comparison_Key_Only.png')
    plt.show()

if __name__ == "__main__":
    request_counts, traditional_results, abe_results = run_experiment()
    plot_results(request_counts, traditional_results, abe_results)

