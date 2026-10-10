# How to Run

### Terminal 1: Start Blockchain Node
Keep this terminal running in the background:
```powershell
cd f:\face-blockchain-verifier
npx hardhat node
```

---

### Terminal 2: Run Pipeline

1. **Activate environment:**
   ```powershell
   cd f:\face-blockchain-verifier
   .\.venv\Scripts\Activate.ps1
   ```

2. **Deploy smart contract (one-time per node session):**
   ```powershell
   python -m blockchain.deploy
   ```

3. **Run face identification & blockchain registration:**
   ```powershell
   python main.py --image input\test_face.jpg
   ```

4. **Verify generated evidence (replace timestamp with your filename):**
   ```powershell
   python main.py --verify output\evidence_20260903_113610.json
   ```
