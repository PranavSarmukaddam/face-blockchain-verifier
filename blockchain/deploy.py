"""
blockchain/deploy.py
Automated deployment of EvidenceRegistry.sol to any EVM chain (Local Hardhat or Polygon Amoy).
"""
import json
import re
from pathlib import Path
from web3 import Web3
from config.settings import settings

_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _ROOT / ".env"
_ABI_PATH = _ROOT / "contracts" / "EvidenceRegistry.abi.json"
_BIN_PATH = _ROOT / "contracts" / "EvidenceRegistry.bin"
_SOL_PATH = _ROOT / "contracts" / "EvidenceRegistry.sol"


def ensure_compiled():
    """Ensure ABI and bytecode exist, compile if missing."""
    if not _ABI_PATH.exists() or not _BIN_PATH.exists():
        print("Compiling EvidenceRegistry.sol...")
        import solcx
        solcx.install_solc("0.8.20")
        res = solcx.compile_files([str(_SOL_PATH)], solc_version="0.8.20")
        contract_key = list(res.keys())[0]
        abi = res[contract_key]["abi"]
        bin_code = res[contract_key]["bin"]
        with open(_ABI_PATH, "w") as f:
            json.dump(abi, f, indent=2)
        with open(_BIN_PATH, "w") as f:
            f.write(bin_code)
        print("[OK] Compilation successful.")


def update_env_contract_address(contract_address: str):
    """Write the deployed contract address back to .env."""
    if not _ENV_PATH.exists():
        return
    content = _ENV_PATH.read_text(encoding="utf-8")
    if "CONTRACT_ADDRESS=" in content:
        new_content = re.sub(
            r"CONTRACT_ADDRESS=.*",
            f"CONTRACT_ADDRESS={contract_address}",
            content,
        )
    else:
        new_content = content.strip() + f"\nCONTRACT_ADDRESS={contract_address}\n"
    _ENV_PATH.write_text(new_content, encoding="utf-8")
    print(f"[OK] Updated .env with CONTRACT_ADDRESS={contract_address}")


def deploy():
    ensure_compiled()

    rpc_url = settings.POLYGON_RPC_URL
    private_key = settings.PRIVATE_KEY
    if not rpc_url:
        raise ValueError("POLYGON_RPC_URL is not set in .env")
    if not private_key:
        raise ValueError("PRIVATE_KEY is not set in .env")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise RuntimeError(f"Could not connect to RPC at {rpc_url}")

    chain_id = w3.eth.chain_id
    account = w3.eth.account.from_key(private_key)
    balance_wei = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance_wei, "ether")

    print(f"Connected to RPC: {rpc_url}")
    print(f"Chain ID:        {chain_id}")
    print(f"Deployer:        {account.address}")
    print(f"Balance:         {balance_eth} ETH/POL")

    if balance_wei == 0:
        raise RuntimeError(f"Deployer wallet {account.address} has 0 balance! Cannot pay gas.")

    with open(_ABI_PATH, "r") as f:
        abi = json.load(f)
    with open(_BIN_PATH, "r") as f:
        bytecode = f.read().strip()

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(account.address)

    print("Submitting deployment transaction...")
    tx = contract.constructor().build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 2_000_000,
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
    })

    signed = account.sign_transaction(tx)
    raw_tx = getattr(signed, "raw_transaction", getattr(signed, "rawTransaction", None))
    tx_hash = w3.eth.send_raw_transaction(raw_tx)
    print(f"Transaction Hash: {tx_hash.hex()}")
    print("Waiting for confirmation...")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    if receipt.status != 1:
        raise RuntimeError("Deployment transaction failed!")

    deployed_address = receipt.contractAddress
    print(f"\n==========================================")
    print(f"[SUCCESS] CONTRACT DEPLOYED SUCCESSFULLY!")
    print(f"Contract Address: {deployed_address}")
    print(f"Block Number:     {receipt.blockNumber}")
    print(f"Gas Used:         {receipt.gasUsed}")
    print(f"==========================================\n")

    update_env_contract_address(deployed_address)
    return deployed_address


if __name__ == "__main__":
    deploy()
