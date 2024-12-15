import time
import matplotlib.pyplot as plt
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
import hashlib
import base64
import uuid
import json

# Assuming the 'config' module and functions are correctly defined and imported
from config import users, data_sets, update_attributes_based_on_reputation, REPUTATION_REQUIREMENTS

group = PairingGroup('SS512')
cpabe = CPabe_BSW07(group)
(pk, mk) = cpabe.setup()

def generate_key_from_element(group, element):
	if not group.ismember(element):
		raise ValueError("Element is not a valid group member")
	serialized_element = group.serialize(element)
	hashed_key = hashlib.sha256(serialized_element).digest()[:16]
	return hashed_key

def aes_encrypt(data, key):
	cipher_aes = AES.new(key, AES.MODE_EAX)
	nonce, ciphertext, tag = cipher_aes.nonce, *cipher_aes.encrypt_and_digest(data)
	return nonce, ciphertext, tag

def aes_decrypt(nonce, ciphertext, tag, key):
	cipher_aes = AES.new(key, AES.MODE_EAX, nonce=nonce)
	return cipher_aes.decrypt_and_verify(ciphertext, tag)

def generate_rsa_keys():
	key = RSA.generate(2048)
	return key.export_key(), key.publickey().export_key()

def rsa_encrypt(data, public_key):
	rsa_key = RSA.import_key(public_key)
	cipher_rsa = PKCS1_OAEP.new(rsa_key)
	return cipher_rsa.encrypt(data)

def rsa_decrypt(encrypted_data, private_key):
	rsa_key = RSA.import_key(private_key)
	cipher_rsa = PKCS1_OAEP.new(rsa_key)
	return cipher_rsa.decrypt(encrypted_data)

tokens = {}

def generate_token(user_id, data_id, expiration=3600):
	token = str(uuid.uuid4())
	token_data = {'user_id': user_id, 'data_id': data_id, 'expires': time.time() + expiration}
	tokens[token] = token_data
	return token

def initialize_user_keys_abe():
	for user_id, user_info in users.items():
		user_info['sk'] = cpabe.keygen(pk, mk, user_info['attributes'])

def initialize_encrypted_data_abe():
	encrypted_data = {}
	for ds_id, ds_content in data_sets.items():
		encrypted_data[ds_id] = {}
		for level, content in ds_content.items():
			if level != 'policy':
				key = group.random(GT)
				aes_key = generate_key_from_element(group, key)
				nonce, ciphertext, tag = aes_encrypt(content.encode(), aes_key)
				encrypted_data[ds_id][level] = {
					'data': base64.b64encode(nonce + ciphertext + tag).decode(),
					'key': cpabe.encrypt(pk, key, ds_content['policy'][level])
				}
	return encrypted_data

def initialize_encrypted_data_rsa(public_key):
	encrypted_data = {}
	for ds_id, ds_content in data_sets.items():
		encrypted_data[ds_id] = {}
		for level, content in ds_content.items():
			if level != 'policy':
				aes_key = get_random_bytes(16)
				nonce, ciphertext, tag = aes_encrypt(content.encode(), aes_key)
				encrypted_aes_key = rsa_encrypt(aes_key, public_key)
				encrypted_data[ds_id][level] = {
					'data': base64.b64encode(nonce + ciphertext + tag).decode(),
					'key': base64.b64encode(encrypted_aes_key).decode()
				}
	return encrypted_data

def request_data_abe(token, data_id, sensitivity_level):
	step_times = {'token_validation': 0, 'key_decryption': 0, 'data_decryption': 0}
	total_start_time = time.time()
	step_start_time = time.time()

	# Token validation
	if token not in tokens or tokens[token]['expires'] < time.time() or tokens[token]['data_id'] != data_id:
		return "Invalid or expired token.", step_times, time.time() - total_start_time
	step_times['token_validation'] = time.time() - step_start_time

	user = users.get(tokens[token]['user_id'])
	if user is None or 'sk' not in user:
		return "User not found or secret key missing.", step_times, time.time() - total_start_time
	key_info = encrypted_data_abe.get(data_id, {}).get(sensitivity_level)
	if key_info is None:
		return f"No data available for {sensitivity_level} sensitivity level in {data_id}.", step_times, time.time() - total_start_time

	# Key decryption
	step_start_time = time.time()
	decrypted_key_element = cpabe.decrypt(pk, user['sk'], key_info['key'])
	if not decrypted_key_element:
		return f"Access denied: Insufficient attributes for {sensitivity_level} sensitivity.", step_times, time.time() - total_start_time
	decrypted_key = generate_key_from_element(group, decrypted_key_element)
	step_times['key_decryption'] = time.time() - step_start_time

	# Data decryption
	step_start_time = time.time()
	raw_data = base64.b64decode(key_info['data'])
	nonce, ciphertext, tag = raw_data[:16], raw_data[16:-16], raw_data[-16:]
	decrypted_data = aes_decrypt(nonce, ciphertext, tag, decrypted_key)
	step_times['data_decryption'] = time.time() - step_start_time

	total_end_time = time.time()
	return f"Access granted: {user['name']} accessed {sensitivity_level} data in {data_id}: {decrypted_data.decode()}", step_times, total_end_time - total_start_time

def request_data_rsa(token, data_id, sensitivity_level, private_key):
	step_times = {'token_validation': 0, 'key_encryption_transfer': 0, 'key_decryption': 0, 'data_decryption': 0}
	total_start_time = time.time()
	step_start_time = time.time()

	# Token validation
	if token not in tokens or tokens[token]['expires'] < time.time() or tokens[token]['data_id'] != data_id:
		return "Invalid or expired token.", step_times, time.time() - total_start_time
	step_times['token_validation'] = time.time() - step_start_time

	user = users.get(tokens[token]['user_id'])
	if user is None:
		return "User not found.", step_times, time.time() - total_start_time
	key_info = encrypted_data_rsa.get(data_id, {}).get(sensitivity_level)
	if key_info is None:
		return f"No data available for {sensitivity_level} sensitivity level in {data_id}.", step_times, time.time() - total_start_time

	# Key encryption and transfer
	step_start_time = time.time()
	encrypted_aes_key = base64.b64decode(key_info['key'])
	step_times['key_encryption_transfer'] = time.time() - step_start_time

	# Key decryption
	step_start_time = time.time()
	aes_key = rsa_decrypt(encrypted_aes_key, private_key)
	step_times['key_decryption'] = time.time() - step_start_time

	# Data decryption
	step_start_time = time.time()
	raw_data = base64.b64decode(key_info['data'])
	nonce, ciphertext, tag = raw_data[:16], raw_data[16:-16], raw_data[-16:]
	decrypted_data = aes_decrypt(nonce, ciphertext, tag, aes_key)
	step_times['data_decryption'] = time.time() - step_start_time

	total_end_time = time.time()
	return f"Access granted: {user['name']} accessed {sensitivity_level} data in {data_id}: {decrypted_data.decode()}", step_times, total_end_time - total_start_time

def simulate_user_progression(user_id, data_id, private_key):
	total_response_time_abe = {'low': [], 'medium': [], 'high': []}
	total_response_time_rsa = {'low': [], 'medium': [], 'high': []}

	for level in ['low', 'medium', 'high']:
		users[user_id]['reputation'] = REPUTATION_REQUIREMENTS[level]
		users[user_id]['attributes'] = update_attributes_based_on_reputation(users[user_id]['reputation'])
		users[user_id]['sk'] = cpabe.keygen(pk, mk, users[user_id]['attributes'])

		token = generate_token(user_id, data_id)
		result_abe, step_times_abe, total_time_abe = request_data_abe(token, data_id, level)
		total_response_time_abe[level].append((result_abe, step_times_abe, total_time_abe))
		print(f"ABE - Result: {result_abe}, Total Time for {level} level: {total_time_abe:.4f}s, Step Times: {step_times_abe}")

		token = generate_token(user_id, data_id)
		result_rsa, step_times_rsa, total_time_rsa = request_data_rsa(token, data_id, level, private_key)
		total_response_time_rsa[level].append((result_rsa, step_times_rsa, total_time_rsa))
		print(f"RSA - Result: {result_rsa}, Total Time for {level} level: {total_time_rsa:.4f}s, Step Times: {step_times_rsa}")

	# Plotting results
	levels = ['Low', 'Medium', 'High']
	abe_times = [sum([time_info[2] for time_info in total_response_time_abe[level]]) / len(total_response_time_abe[level]) for level in ['low', 'medium', 'high']]
	rsa_times = [sum([time_info[2] for time_info in total_response_time_rsa[level]]) / len(total_response_time_rsa[level]) for level in ['low', 'medium', 'high']]

	plt.figure(figsize=(10, 6))
	x = range(len(levels))

	plt.bar(x, abe_times, width=0.4, label='ABEToken', color='blue', align='center')
	plt.bar([p + 0.4 for p in x], rsa_times, width=0.4, label='Traditional RSA', color='orange', align='center')

	plt.xticks([p + 0.2 for p in x], levels)
	plt.xlabel('Sensitivity Level')
	plt.ylim(0, 0.2)  # Adjust the range as needed
	plt.ylabel('Response Time (ms)')
	plt.title('Comparison of Response Time for Data with Different Sensitivity Levels')

	plt.legend(loc='upper right')
	plt.show()

if __name__ == "__main__":
	user_id = 'user1'
	data_id = 'D1'
	encrypted_data_abe = initialize_encrypted_data_abe()
	initialize_user_keys_abe()
	private_key, public_key = generate_rsa_keys()
	encrypted_data_rsa = initialize_encrypted_data_rsa(public_key)
	simulate_user_progression(user_id, data_id, private_key)

